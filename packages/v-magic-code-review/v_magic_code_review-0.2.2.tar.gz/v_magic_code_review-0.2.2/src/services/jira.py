from urllib.parse import urlparse, parse_qs

from atlassian import Jira
from loguru import logger

from services.confluence import ConfluenceService
from config import JiraConfig, JiraField
from util import remove_blank_lines, first_element


class JiraService:
    def __init__(self):
        self.jira = Jira(
            url=JiraConfig.HOST,
            token=JiraConfig.TOKEN,
        )

    def get_client(self) -> Jira:
        return self.jira

    def get_issue(self, issue_key: str) -> dict:
        return self.jira.issue(issue_key)

    def get_issue_comments(self, issue: dict) -> str:
        original_comments = issue['fields'][JiraField.COMMENT]['comments']
        text_comments = []
        for comment in original_comments:
            author_section = '{} {}：\n'.format(comment['created'], comment['author']['displayName'])
            body_section = remove_blank_lines(comment['body'])
            text_comments.append(author_section + body_section)
            logger.info('get issue comment, author: %s, body: %s', author_section, body_section.splitlines()[-1])
        return '\n'.join(text_comments)

    def get_issue_requirements(self, issue: dict, confluence_service: 'ConfluenceService') -> str:
        description = issue['fields'][JiraField.DESCRIPTION]
        if not description:
            return ''

        if description.startswith('https://'):
            logger.info("get requirements from confluence: %s", description)

            wiki_url = description
            page = confluence_service.get_page_by_url(wiki_url)
            requirements = confluence_service.get_requirements(page, issue['key'])
        else:
            logger.info('get requirements from description: %s', description)
            requirements = description
        return requirements

    def get_issue_design(self, issue: dict, confluence_service: 'ConfluenceService') -> str:
        remote_links = self.jira.get_issue_remote_links(issue['key'])
        issue_designs = []
        for remote_link in remote_links:
            application = remote_link['application']
            if not application or application['type'] != 'com.atlassian.confluence':
                continue
            url = remote_link['object']['url']
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            page_id = first_element(params.get('pageId') or [])
            page = confluence_service.get_page_by_id(page_id)
            space = page['_expandable']['space']
            if space != '/rest/api/space/ORI':
                continue
            logger.info('get design from confluence, title: %s, url: %s', page['title'], url)
            issue_designs.append(confluence_service.get_page_markdown(page))
        return '\n\n'.join(issue_designs)
