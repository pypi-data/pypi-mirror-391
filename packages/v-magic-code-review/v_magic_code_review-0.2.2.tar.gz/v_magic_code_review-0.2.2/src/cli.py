import sys
import textwrap

from loguru import logger
from rich.console import Console
from rich.markdown import Markdown

from arguments import parse_args, Arguments, show_help
from logger import set_logging_level
from prompt import Prompts
from review import code_review
from version import print_version_text, update_check


def main():
    if len(sys.argv) <= 1:
        show_help()
        return

    args: Arguments = parse_args()
    set_logging_level(args.debug)

    if args.version:
        print_version_text()
        return

    update_check()

    if args.list_prompt_templates:
        names = ['* ' + it + '\n' for it in Prompts.list_template_names()]
        names.sort()
        output = textwrap.dedent('''
            Avalible Prompt Templates:
                
            {}
        ''').strip().format(''.join(names))
        Console().print(Markdown(output))
        return

    logger.info(f'args: {args}')

    if args.jira_key_or_mr_id:
        jira_key_or_mr_id = args.jira_key_or_mr_id
        only_code = args.only_code
        mr_id = args.mr_id

        if mr_id is None and jira_key_or_mr_id.isnumeric():
            mr_id = jira_key_or_mr_id
            only_code = True

        code_review(jira_key_or_mr_id, mr_id, only_code, args.copy_prompt, args.prompt_templates, args.advance)


if __name__ == "__main__":
    main()
