import argparse
from dataclasses import dataclass


@dataclass
class Arguments:
    jira_key_or_mr_id: str | None
    mr_id: int | None
    only_code: bool
    copy_prompt: bool
    prompt_templates: list[str] | None
    list_prompt_templates: bool
    debug: bool
    version: bool
    advance: bool


def parse_args() -> Arguments:
    args = _build_parser().parse_args()
    return Arguments(
        jira_key_or_mr_id=args.jira_key_or_mr_id,
        mr_id=args.mr_id,
        only_code=args.only_code,
        copy_prompt=args.copy_prompt,
        prompt_templates=args.prompt_templates and args.prompt_templates.split(','),
        list_prompt_templates=args.list_prompt_templates,
        debug=args.debug,
        version=args.version,
        advance=args.advance,
    )


def show_help():
    _build_parser().print_help()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Magic Code Review')
    parser.add_argument('jira_key_or_mr_id', type=str, nargs='?', metavar="JIRA_KEY OR MR_ID", help='jira issue key or merge request id')  # noqa
    parser.add_argument('-m', '--mr-id', type=int, help='【DEPRECATED】merge request id')
    parser.add_argument('-o', '--only-code', action='store_true', help='only review code diff')
    parser.add_argument('-c', '--copy-prompt', action='store_true', help='copy prompt to clipboard')
    parser.add_argument('--prompt-templates', type=str, default='default', help='specific prompt template list, separated by [,]')  # noqa
    parser.add_argument('--list-prompt-templates', action='store_true', help='list all prompt templates')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--advance', action='store_true', help='use staged review')
    return parser
