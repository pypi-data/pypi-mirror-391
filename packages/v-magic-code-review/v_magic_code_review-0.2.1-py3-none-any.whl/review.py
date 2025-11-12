import asyncio
import concurrent.futures
import logging
import os
import textwrap
from dataclasses import dataclass
from typing import Optional

import pyperclip
from gemini_webapi.constants import Model
from gitlab.v4.objects import MergeRequest
from rich.console import Console
from rich.markdown import Markdown
from termcolor import colored
from yaspin import yaspin
from yaspin.spinners import Spinners

from config import JiraField
from constants import FRONTEND_EXT
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
        analysis_result = gemini_service.do_code_quality_analysis(prompt, model)
        analysis_result = analysis_result.lstrip("```markdown")
        analysis_result = analysis_result.rstrip("```")
        return analysis_result

    def do_staged_review(self, diff: str, is_frontend: bool) -> str:
        spinner_text = "Performing {} staged code review, this may take a while...".format(
            "frontend" if is_frontend else "backend"
        )
        with yaspin(Spinners.clock, text=spinner_text, timer=True) as sp:
            if is_frontend:
                # Simplified flow for frontend
                sp.text = "Stage 1: Intent & Sanity Check"
                prompt1 = Prompts.create(
                    template_name="stage1_intent_and_sanity_check",
                    mr_diff=diff
                )
                result1 = self.do_review(prompt1)
                logging.info("Stage 1 completed.")

                sp.text = "Stage 4: Final Report Generation"
                prompt4 = Prompts.create(
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
                logging.info("Stage 4 (Frontend) completed.")
            else:
                # Full flow for backend
                sp.text = "Stages 1, 2, 3: Parallel Review"
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    # Stage 1
                    prompt1 = Prompts.create(
                        template_name="stage1_intent_and_sanity_check",
                        mr_diff=diff
                    )
                    future1 = executor.submit(self.do_review, prompt1)

                    # Stage 2
                    prompt2 = Prompts.create(
                        template_name="stage2_core_practices_and_robustness",
                        mr_diff=diff,
                        review_result_of_stage1=""
                    )
                    future2 = executor.submit(self.do_review, prompt2)

                    # Stage 3
                    prompt3 = Prompts.create(
                        template_name="stage3_systemic_risk_and_advanced_review",
                        mr_diff=diff,
                        review_result_of_stage1_2=""
                    )
                    future3 = executor.submit(self.do_review, prompt3)

                    result1 = future1.result()
                    logging.info("Stage 1 completed.")
                    result2 = future2.result()
                    logging.info("Stage 2 completed.")
                    result3 = future3.result()
                    logging.info("Stage 3 completed.")

                # Stage 4
                sp.text = "Stage 4: Final Report Generation"
                prompt4 = Prompts.create(
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
                logging.info("Stage 4 (Backend) completed.")

        return final_result

    def do_normal_review(self, copy_prompt: Optional[bool], prompt_templates: list[str]):
        prompts_with_name = []
        for name in prompt_templates:
            prompts_with_name.append(
                (
                    name,
                    Prompts.create(
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
                        logging.info("review for '%s' completed.", template_name)
                    except Exception as exc:
                        logging.error("review for '%s' generated an exception: %s", template_name, exc)
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

    logging.info('merge request link: %s', mr.web_url)
    logging.info('merge request title: %s', mr.title)

    if only_code:
        issue_summary = '无'
        issue_requirements = '无'
        issue_design = '无'
        issue_comments = '无'
    else:
        logging.info('get jira ...')
        jira_service = JiraService()
        jira_issue = jira_service.get_issue(jira_key)
        assert jira_issue is not None, f"jira issue not found: {jira_key}"

        logging.info('jira issue link: %s', jira_issue['self'])
        logging.info('jira issue summary: %s', jira_issue['fields'][JiraField.SUMMARY])

        issue_summary = jira_issue['fields'][JiraField.SUMMARY]

        logging.info('get wikis ...')
        confluence_service = ConfluenceService()
        issue_requirements = jira_service.get_issue_requirements(jira_issue, confluence_service)
        logging.info('✨ issue requirements length: %s', len(issue_requirements))

        issue_design = jira_service.get_issue_design(jira_issue, confluence_service)
        logging.info('✨ issue design length: %s', len(issue_design))

        issue_comments = jira_service.get_issue_comments(jira_issue)
        logging.info('✨ issue comments length: %s', len(issue_comments))

    mr_diff = gitlab_service.get_plain_diff_from_mr(mr)
    logging.info('✨ code  diff length: %s', len(mr_diff))

    return ReviewInformation(
        jira_key=jira_key,
        mr=mr,
        mr_id=mr.id,
        mr_title=mr.title,
        mr_description=mr.description,
        mr_diff=mr_diff,
        issue_summary=issue_summary,
        issue_requirements=issue_requirements,
        issue_design=issue_design,
        issue_comments=issue_comments,
    )


def split_diff_by_file_type(full_diff: str) -> tuple[str, str]:
    if not full_diff:
        return "", ""

    diff_blocks = full_diff.splitlines(True)
    blocks = []
    current_block = []
    for line in diff_blocks:
        if line.startswith('diff --git ') and current_block:
            blocks.append("".join(current_block))
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append("".join(current_block))

    frontend_diff_parts = []
    backend_diff_parts = []

    for block in blocks:
        first_line = block.splitlines()[0]
        try:
            path = first_line.split(' ')[-1]
            if path.startswith('b/'):
                path = path[2:]
            file_ext = os.path.splitext(path)[1]

            if file_ext in FRONTEND_EXT:
                frontend_diff_parts.append(block)
            else:
                backend_diff_parts.append(block)
        except IndexError:
            backend_diff_parts.append(block)

    return "".join(frontend_diff_parts), "".join(backend_diff_parts)


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
    add_options = f"/{colored('添加(Y)', 'green', attrs=['bold'])}/{colored('放弃(Q)', 'red', attrs=['bold'])}"
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
        frontend_diff, backend_diff = split_diff_by_file_type(ri.mr_diff)

        if backend_diff:
            backend_result = rh.do_staged_review(backend_diff, is_frontend=False)
            display_and_submit_review(backend_result, "backend", ri.mr, ri.jira_key)

        if frontend_diff:
            frontend_result = rh.do_staged_review(frontend_diff, is_frontend=True)
            display_and_submit_review(frontend_result, "frontend", ri.mr, ri.jira_key)
    else:
        rh.do_normal_review(copy_prompt, prompt_templates)
