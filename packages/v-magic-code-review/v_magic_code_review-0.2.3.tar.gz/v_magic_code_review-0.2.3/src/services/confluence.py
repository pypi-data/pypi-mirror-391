import bs4
from atlassian import Confluence
from loguru import logger
from markdownify import MarkdownConverter

from config import ConfluenceConfig


class ConfluenceService:
    def __init__(self):
        self.confluence = Confluence(
            url=ConfluenceConfig.HOST,
            token=ConfluenceConfig.TOKEN,
            cloud=False
        )

    def get_page_by_url(self, url):
        return self.get_page_by_id(url.split('/pages/')[1].split('/')[0])

    def get_page_by_id(self, page_id):
        return self.confluence.get_page_by_id(page_id=page_id, expand='body.storage')

    def get_page_markdown(self, page):
        soup = bs4.BeautifulSoup(page['body']['storage']['value'], "lxml")
        return MarkdownConverter().convert_soup(soup)

    def get_requirements(self, page, jira_key):
        bs_content = bs4.BeautifulSoup(page['body']['storage']['value'], "lxml")

        reference_row = self.get_reference_row(bs_content, jira_key)
        if reference_row is None:
            logger.warning('jira key not found in confluence page: %s', jira_key)
            return ''
        requirements = reference_row.get_text(separator='\n', strip=True)
        return requirements

    def get_reference_row(self, bs_content, jira_key):
        for table in bs_content.find_all('table'):
            for row in table.find_all('tr'):
                for cell in row.find_all(['td', 'th']):
                    if jira_key in cell.get_text(strip=True):
                        return row
        return None
