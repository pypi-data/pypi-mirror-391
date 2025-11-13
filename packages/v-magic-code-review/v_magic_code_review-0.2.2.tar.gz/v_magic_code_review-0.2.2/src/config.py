import os

from util import get_cookie_from_browser


class GitlabConfig:
    PROJECT_ID = 311
    HOST = os.environ['GITLAB_HOST']
    TOKEN = os.environ['GITLAB_TOKEN']
    DIFF_EXCLUDE_EXT = {'.ttf', '.woff', '.woff2', '.eot', '.otf', '.svg', '.png', '.jpg', '.jpeg', '.gif'}
    DIFF_EXCLUDE_PATH = {'thirdparty'}


class JiraConfig:
    HOST = os.environ['JIRA_HOST']
    TOKEN = os.environ['JIRA_TOKEN']


class JiraField:
    SUMMARY = 'summary'
    AC = 'customfield_13530'
    DESCRIPTION = 'description'
    COMMENT = 'comment'


class ConfluenceConfig:
    HOST = os.environ['CONFLUENCE_HOST']
    TOKEN = os.environ['CONFLUENCE_TOKEN']


class __GeminiConfig:
    __secure_1psid = None
    __secure_1psidts = None

    def __ensure_cookie(self):
        if self.__secure_1psid and self.__secure_1psidts:
            return

        browser_name = os.environ.get('BROWSER_NAME', 'chrome')
        self.__secure_1psid, self.__secure_1psidts = get_cookie_from_browser(browser_name)

    @property
    def cookie_secure_1psid(self) -> str:
        self.__ensure_cookie()
        return self.__secure_1psid or os.environ['GEMINI_COOKIE_SECURE_1PSID']

    @property
    def cookie_secure_1psidts(self) -> str:
        self.__ensure_cookie()
        return self.__secure_1psidts or os.environ['GEMINI_COOKIE_SECURE_1PSIDTS']


GeminiConfig = __GeminiConfig()
