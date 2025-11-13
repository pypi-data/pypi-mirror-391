import asyncio
import concurrent.futures
import json
import os
import re
import textwrap
from dataclasses import dataclass
from typing import Optional

import pyperclip
from gemini_webapi.constants import Model
from gitlab.v4.objects import MergeRequest
from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from termcolor import colored
from yaspin import yaspin
from yaspin.spinners import Spinners

from config import JiraField
from prompt import Prompts
from services.confluence import ConfluenceService
from services.gemini import GeminiService
from services.gitlab import GitlabService
from services.jira import JiraService


@dataclass
class ReviewInformation:
    jira_key: str
    mr: MergeRequest
    mr_id: int
    mr_title: str
    mr_description: str
    mr_diff: str
    mr_diff_by_file: dict[str, str]
    issue_summary: str
    issue_requirements: str
    issue_design: str
    issue_comments: str


class ReviewHandler:
    def __init__(self, ri: ReviewInformation):
        self.ri = ri

    def do_review(self, prompt: str, model: Optional[Model] = None) -> str:
        asyncio.set_event_loop(asyncio.new_event_loop())
        gemini_service = GeminiService()
        analysis_result = gemini_service.chat(prompt, model)
        analysis_result = analysis_result.lstrip("```markdown")
        analysis_result = analysis_result.rstrip("```")
        return analysis_result

    def do_advance_review(self, diff: str, is_frontend: bool) -> str:
        spinner_text = "Performing {} staged code review, this may take a while...".format(
            "frontend" if is_frontend else "backend"
        )
        with yaspin(Spinners.clock, text=spinner_text, timer=True) as sp:
            if is_frontend:
                # Simplified flow for frontend
                sp.text = "Stage 1: Intent & Sanity Check"
                prompt1 = Prompts.build_internal(
                    template_name="stage1_intent_and_sanity_check",
                    mr_diff=diff
                )
                result1 = self.do_review(prompt1)
                sp.write("Stage 1 completed.")

                sp.text = "Stage 4: Final Report Generation"
                prompt4 = Prompts.build_internal(
                    template_name="stage4_final_report_generation",
                    issue_summary=self.ri.issue_summary,
                    issue_requirements=self.ri.issue_requirements,
                    issue_design=self.ri.issue_design,
                    issue_comments=self.ri.issue_comments,
                    mr_description=self.ri.mr_description,
                    mr_diff=diff,
                    review_result_of_stage1_2_3=result1
                )
                final_result = self.do_review(prompt4, model=Model.G_2_5_FLASH)
                sp.write("Stage 4 (Frontend) completed.")
            else:
                # Full flow for backend
                sp.text = "Stages 1, 2, 3: Parallel Review"
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    # Stage 1
                    prompt1 = Prompts.build_internal(
                        template_name="stage1_intent_and_sanity_check",
                        mr_diff=diff
                    )
                    future1 = executor.submit(self.do_review, prompt1)

                    # Stage 2
                    prompt2 = Prompts.build_internal(
                        template_name="stage2_core_practices_and_robustness",
                        mr_diff=diff,
                        review_result_of_stage1=""
                    )
                    future2 = executor.submit(self.do_review, prompt2)

                    # Stage 3
                    prompt3 = Prompts.build_internal(
                        template_name="stage3_systemic_risk_and_advanced_review",
                        mr_diff=diff,
                        review_result_of_stage1_2=""
                    )
                    future3 = executor.submit(self.do_review, prompt3)

                    result1 = future1.result()
                    sp.write("Stage 1 completed.")
                    result2 = future2.result()
                    sp.write("Stage 2 completed.")
                    result3 = future3.result()
                    sp.write("Stage 3 completed.")

                # Stage 4
                sp.text = "Stage 4: Final Report Generation"
                prompt4 = Prompts.build_internal(
                    template_name="stage4_final_report_generation",
                    issue_summary=self.ri.issue_summary,
                    issue_requirements=self.ri.issue_requirements,
                    issue_design=self.ri.issue_design,
                    issue_comments=self.ri.issue_comments,
                    mr_description=self.ri.mr_description,
                    mr_diff=diff,
                    review_result_of_stage1_2_3=f"{result1}\n\n{result2}\n\n{result3}"
                )
                final_result = self.do_review(prompt4, model=Model.G_2_5_FLASH)
                sp.write("Stage 4 (Backend) completed.")

        return final_result

    def do_normal_review(self, copy_prompt: Optional[bool], prompt_templates: list[str]):
        prompts_with_name = []
        for name in prompt_templates:
            prompts_with_name.append(
                (
                    name,
                    Prompts.build(
                        template_name=name,
                        issue_summary=self.ri.issue_summary,
                        issue_requirements=self.ri.issue_requirements,
                        issue_design=self.ri.issue_design,
                        issue_comments=self.ri.issue_comments,
                        mr_description=self.ri.mr_description,
                        mr_diff=self.ri.mr_diff
                    )
                )
            )

        assert len(prompts_with_name) > 0, "no prompt template found"

        if copy_prompt:
            if not prompts_with_name:
                print("✅ {}".format(colored('没有指定用于复制的 Prompt 模板', 'yellow', attrs=['bold'])))
                return

            pyperclip.copy(prompts_with_name[0][1])
            print("✅ {}".format(colored('Prompt 已复制到剪贴板', 'green', attrs=['bold'])))
            return

        results_map = {}
        with yaspin(Spinners.clock, text="Waiting for Gemini's response, usually takes about 2 minutes", timer=True) as sp:  # noqa
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(prompts_with_name) or 1) as executor:
                future_to_template = {
                    executor.submit(self.do_review, prompt): template_name
                    for template_name, prompt in prompts_with_name
                }

                for future in concurrent.futures.as_completed(future_to_template):
                    template_name = future_to_template[future]
                    try:
                        result = future.result()
                        results_map[template_name] = result
                        sp.write(f"review for {template_name} completed.")
                    except Exception as exc:
                        logger.error("review for '%s' generated an exception: %s", template_name, exc)
                        results_map[template_name] = f"Error processing {template_name}: {exc}"

        results = [results_map[name] for name, _ in prompts_with_name]

        # Since we are not in a staged review, we can just use the first result for display and submit
        display_and_submit_review(results[0], prompts_with_name[0][0], self.ri.mr, self.ri.jira_key)


def get_review_information(jira_key: str, mr_id: Optional[int], only_code: Optional[bool]) -> ReviewInformation:
    gitlab_service = GitlabService()
    if mr_id is not None:
        mr = gitlab_service.get_mr(mr_id)
    else:
        mr = gitlab_service.find_mr_by_jira_key(jira_key)
    assert mr is not None, f"merge request not found with jira key: {jira_key}"

    logger.info(f'merge request link: {mr.web_url}')
    logger.info(f'merge request title: {mr.title}')

    if only_code:
        issue_summary = '无'
        issue_requirements = '无'
        issue_design = '无'
        issue_comments = '无'
    else:
        logger.info('get jira ...')
        jira_service = JiraService()
        jira_issue = jira_service.get_issue(jira_key)
        assert jira_issue is not None, f"jira issue not found: {jira_key}"

        logger.info(f"jira issue link: {jira_issue['self']}")
        logger.info(f"jira issue summary: {jira_issue['fields'][JiraField.SUMMARY]}")

        issue_summary = jira_issue['fields'][JiraField.SUMMARY]

        logger.info('get wikis ...')
        confluence_service = ConfluenceService()
        issue_requirements = jira_service.get_issue_requirements(jira_issue, confluence_service)
        logger.info('✨ issue requirements length: {}', len(issue_requirements))

        issue_design = jira_service.get_issue_design(jira_issue, confluence_service)
        logger.info('✨ issue design length: {}', len(issue_design))

        issue_comments = jira_service.get_issue_comments(jira_issue)
        logger.info('✨ issue comments length: {}', len(issue_comments))

    mr_diff, mr_diff_by_file = gitlab_service.get_diff_from_mr(mr)
    logger.info('✨ code  diff length: {}', len(mr_diff))

    return ReviewInformation(
        jira_key=jira_key,
        mr=mr,
        mr_id=mr.id,
        mr_title=mr.title,
        mr_description=mr.description,
        mr_diff=mr_diff,
        mr_diff_by_file=mr_diff_by_file,
        issue_summary=issue_summary,
        issue_requirements=issue_requirements,
        issue_design=issue_design,
        issue_comments=issue_comments,
    )


def split_code(diff: str) -> Optional[dict[str, list[dict]]]:
    assert diff, "diff is empty"
    gemini_service = GeminiService()
    prompt = Prompts.build_internal(template_name="split_code", mr_diff=diff)
    with yaspin(Spinners.clock, text="Splitting code into chunks...", timer=True) as sp:
        chat_result = gemini_service.chat(prompt)
    json_match = re.search(r"```json\n(.*?)```", chat_result, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
    else:
        logger.error("failed to find json in chat result: %s", chat_result)
        json_string = "{}"  # Fallback to empty JSON object to avoid JSONDecodeError

    try:
        chunks = json.loads(json_string)
    except json.JSONDecodeError:
        logger.error("failed to decode chat result: %s", chat_result)
        chunks = {"backend": [], "frontend": []}
    return chunks


def display_and_submit_review(
    result: str,
    review_type: str,
    mr: MergeRequest,
    jira_key: str,
):
    Console().print(Markdown(f"# {review_type.capitalize()} Code Review Result\n\n{result}", code_theme='rrt'))
    print()

    gitlab_comment = textwrap.dedent("""
        <details>
        <summary>AI Code Review ({review_type}) 结果，请 Owner 对结果中的问题一一回复</summary>
        
        {result}
        
        </details>
    """).strip()
    gitlab_comment = gitlab_comment.format(review_type=review_type, result=result)

    add_prompt = colored('是否添加到 MR Comments？', 'yellow', attrs=['bold'])
    add_options = f"/{colored('添加(Y)', 'green', attrs=['bold'])}/{colored('放弃(N)', 'red', attrs=['bold'])}"
    other_options = f"{colored('复制(C)', 'magenta', attrs=['bold'])}/{colored('保存(S)', 'blue', attrs=['bold'])}"

    prompt_text = "✨ For the {review_type} review: {add_prompt}{add_options}， or {other_options}\n👉 ".format(
        review_type=colored(review_type, 'cyan', attrs=['bold']),
        add_prompt=add_prompt,
        add_options=add_options,
        other_options=other_options
    )
    selected = input(prompt_text)

    if selected.lower() == 'y':
        gitlab_service = GitlabService()
        gitlab_service.add_comments(mr, gitlab_comment)
        print(f"✅ {review_type.capitalize()} review 已添加到 MR")
    elif selected.lower() == 'c':
        pyperclip.copy(result)
        print("✅ 已复制到剪贴板")
    elif selected.lower() == 's':
        file_path = os.path.expanduser(f'~/Downloads/magic_code_review_{jira_key}_{review_type}.md')
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ 已保存到 {file_path}")
    else:
        print("👋 Skipped.")


def code_review(
    jira_key: str,
    mr_id: Optional[int],
    only_code: Optional[bool],
    copy_prompt: Optional[bool],
    prompt_templates: list[str],
    advance: bool,
) -> None:
    ri = get_review_information(jira_key, mr_id, only_code)
    rh = ReviewHandler(ri)

    if advance:
        if len(ri.mr_diff) < 500 or len(ri.mr_diff_by_file) == 1:
            result = rh.do_advance_review(ri.mr_diff, is_frontend=False)
            display_and_submit_review(result, "ALL", ri.mr, ri.jira_key)
        else:
            logger.info("✂️ The MR diff is too large, splitting it into chunks...")
            chunks = split_code(ri.mr_diff)
            print(json.dumps(chunks, indent=4, ensure_ascii=False))
            proceed = input("Do you want to proceed with the review? (Y/N) ")
            if proceed.lower() != 'y':
                print("👋 Skipped.")
                return

            backend_chunks = chunks.get("backend", [])
            frontend_chunks = chunks.get("frontend", [])
            chunk_count = len(backend_chunks) + len(frontend_chunks)

            for i, chunk in enumerate(backend_chunks):
                print(f"🤖 Reviewing backend chunk {i + 1}/{chunk_count}: {chunk['summary']}")
                chunk_diff = "".join(ri.mr_diff_by_file.get(file, "") for file in chunk["files"])
                if chunk_diff:
                    backend_result = rh.do_advance_review(chunk_diff, is_frontend=False)
                    display_and_submit_review(backend_result, f"backend: {chunk['summary']}", ri.mr, ri.jira_key)

            for i, chunk in enumerate(frontend_chunks):
                print(f"🤖 Reviewing frontend chunk {len(backend_chunks) + i + 1}/{chunk_count}: {chunk['summary']}")
                chunk_diff = "".join(ri.mr_diff_by_file.get(file, "") for file in chunk["files"])
                if chunk_diff:
                    frontend_result = rh.do_advance_review(chunk_diff, is_frontend=True)
                    display_and_submit_review(frontend_result, f"frontend: {chunk['summary']}", ri.mr, ri.jira_key)
    else:
        rh.do_normal_review(copy_prompt, prompt_templates)
