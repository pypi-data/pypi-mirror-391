import logging
import sys
import textwrap

from rich.console import Console
from rich.markdown import Markdown

from arguments import parse_args, Arguments, show_help
from prompt import Prompts
from review import code_review
from version import print_version_text, update_check


def set_logging_level(debug: bool) -> None:
    message_format = '%(asctime)s %(levelname)s %(name)s - %(message)s'
    if debug:
        logging.basicConfig(level=logging.DEBUG, format=message_format)
    else:
        logging.basicConfig(level=logging.INFO, format=message_format)


def main():
    if len(sys.argv) <= 1:
        show_help()
        return

    args: Arguments = parse_args()

    if args.version:
        print_version_text()
        return

    update_check()

    set_logging_level(args.debug)

    if args.list_prompt_templates:
        names = ['* ' + it + '\n' for it in Prompts.list_template_names()]
        output = textwrap.dedent('''
            Avalible Prompt Templates:
                
            {}
        ''').strip().format(''.join(names))
        Console().print(Markdown(output))
        return

    logging.info('args: %s', args)

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
