import unittest
from unittest.mock import patch, MagicMock, mock_open

import urllib3.util

from review import code_review
from services.confluence import ConfluenceService
from services.gitlab import GitlabService
from services.jira import JiraService
from src.cli import (
    print_version_text,
    parse_args,
    main
)
from src.config import JiraField
from src.services.gemini import GeminiService


class TestGitlabService(unittest.TestCase):
    @patch('gitlab.Gitlab')
    def test_init(self, mock_gitlab):
        # Setup
        mock_gl = MagicMock()
        mock_project = MagicMock()
        mock_gitlab.return_value = mock_gl
        mock_gl.projects.get.return_value = mock_project

        # Execute
        service = GitlabService()

        # Assert
        mock_gitlab.assert_called_once()
        mock_gl.projects.get.assert_called_once()
        self.assertEqual(service.gl, mock_gl)
        self.assertEqual(service.gl_project, mock_project)

    @patch('gitlab.Gitlab')
    def test_find_mr_by_jira_key(self, mock_gitlab):
        # Setup
        mock_gl = MagicMock()
        mock_project = MagicMock()
        mock_gitlab.return_value = mock_gl
        mock_gl.projects.get.return_value = mock_project

        mock_mr1 = MagicMock()
        mock_mr1.title = "Some MR"
        mock_mr2 = MagicMock()
        mock_mr2.title = "TEST-123: Fix bug"
        mock_project.mergerequests.list.return_value = [mock_mr1, mock_mr2]

        service = GitlabService()

        # Execute
        result = service.find_mr_by_jira_key("TEST-123")

        # Assert
        self.assertEqual(result, mock_mr2)

        # Test not found case
        result = service.find_mr_by_jira_key("NOT-FOUND")
        self.assertIsNone(result)

    @patch('gitlab.Gitlab')
    def test_get_plain_diff_from_mr(self, mock_gitlab):
        # Setup
        mock_gl = MagicMock()
        mock_project = MagicMock()
        mock_gitlab.return_value = mock_gl
        mock_gl.projects.get.return_value = mock_project

        service = GitlabService()

        mock_mr = MagicMock()
        mock_changes = {
            'changes': [
                {
                    'old_path': 'file1.py',
                    'new_path': 'file1.py',
                    'diff': 'diff content',
                    'new_file': False,
                    'renamed_file': False,
                    'deleted_file': False
                }
            ]
        }
        mock_mr.changes.return_value = mock_changes

        # Execute
        result = service.get_plain_diff_from_mr(mock_mr)

        # Assert
        expected = "diff --git a/file1.py b/file1.py\n--- a/file1.py\n+++ b/file1.py\ndiff content"
        self.assertEqual(result, expected)

        # Test with new file
        mock_changes = {
            'changes': [
                {
                    'old_path': 'file2.py',
                    'new_path': 'file2.py',
                    'diff': 'diff content',
                    'new_file': True,
                    'renamed_file': False,
                    'deleted_file': False
                }
            ]
        }
        mock_mr.changes.return_value = mock_changes

        result = service.get_plain_diff_from_mr(mock_mr)
        expected = "diff --git a/file2.py b/file2.py\nnew file mode 100644\n--- /dev/null\n+++ b/file2.py\ndiff content"
        self.assertEqual(result, expected)

    @patch('gitlab.Gitlab')
    def test_add_comments(self, mock_gitlab):
        # Setup
        mock_gl = MagicMock()
        mock_project = MagicMock()
        mock_gitlab.return_value = mock_gl
        mock_gl.projects.get.return_value = mock_project

        service = GitlabService()

        mock_mr = MagicMock()
        mock_notes = MagicMock()
        mock_mr.notes = mock_notes

        # Execute
        service.add_comments(mock_mr, "Test comment")

        # Assert
        mock_notes.create.assert_called_once_with({'body': 'Test comment'})


class TestJiraService(unittest.TestCase):
    @patch('atlassian.Jira')
    def test_init(self, mock_jira_class):
        # Setup
        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira

        # Execute
        service = JiraService()

        # Assert
        mock_jira_class.assert_called_once()
        self.assertEqual(service.jira, mock_jira)

    @patch('atlassian.Jira')
    def test_get_issue(self, mock_jira_class):
        # Setup
        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira
        mock_jira.issue.return_value = {'key': 'TEST-123'}

        service = JiraService()

        # Execute
        result = service.get_issue('TEST-123')

        # Assert
        mock_jira.issue.assert_called_once_with('TEST-123')
        self.assertEqual(result, {'key': 'TEST-123'})

    @patch('atlassian.Jira')
    def test_get_issue_comments(self, mock_jira_class):
        # Setup
        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira

        service = JiraService()
        mock_issue = {
            'fields': {
                'comment': {
                    'comments': [
                        {'author': {'displayName': 'author1'}, 'body': 'comment1',
                         'created': '2021-01-01T00:00:00.000+0000'},
                        {'author': {'displayName': 'author2'}, 'body': 'comment2',
                         'created': '2021-01-02T00:00:00.000+0000'},
                    ]
                }
            }
        }

        # Execute
        result = service.get_issue_comments(mock_issue)

        # Assert
        self.assertEqual(result, '\n'.join([
            '2021-01-01T00:00:00.000+0000 author1：',
            'comment1'
            '',
            '2021-01-02T00:00:00.000+0000 author2：',
            'comment2',
        ]))

    @patch('atlassian.Jira')
    def test_get_issue_requirements_from_description(self, mock_jira_class):
        # Setup
        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira

        service = JiraService()
        mock_issue = {
            'fields': {
                JiraField.DESCRIPTION: 'Test requirements'
            }
        }
        mock_confluence_service = MagicMock()

        # Execute
        result = service.get_issue_requirements(mock_issue, mock_confluence_service)

        # Assert
        self.assertEqual(result, 'Test requirements')

    @patch('atlassian.Jira')
    def test_get_issue_requirements_from_confluence(self, mock_jira_class):
        # Setup
        mock_jira = MagicMock()
        mock_jira_class.return_value = mock_jira

        service = JiraService()
        mock_issue = {
            'key': 'TEST-123',
            'fields': {
                JiraField.DESCRIPTION: 'https://confluence.example.com/pages/12345/page'
            }
        }
        mock_confluence_service = MagicMock()
        mock_page = {'id': '12345'}
        mock_confluence_service.get_page_by_url.return_value = mock_page
        mock_confluence_service.get_requirements.return_value = 'Confluence requirements'

        # Execute
        result = service.get_issue_requirements(mock_issue, mock_confluence_service)

        # Assert
        mock_confluence_service.get_page_by_url.assert_called_once_with('https://confluence.example.com/pages/12345/page')
        mock_confluence_service.get_requirements.assert_called_once_with(mock_page, 'TEST-123')
        self.assertEqual(result, 'Confluence requirements')

    def test_get_issue_design(self):
        jira_service = JiraService()
        confluence_service = ConfluenceService()

        remote_links = jira_service.get_client().get_issue_remote_links('ORI-116650')
        for remote_link in remote_links:
            application = remote_link['application']
            if not application or application['type'] != 'com.atlassian.confluence':
                continue
            url = remote_link['object']['url']
            page_id = urllib3.util.parse_url(url)
            page = confluence_service.get_page_by_id(page_id)
            design = confluence_service.get_requirements(page, 'ORI-116650')
            print(design)


class TestConfluenceService(unittest.TestCase):
    @patch('atlassian.Confluence')
    def test_init(self, mock_confluence_class):
        # Setup
        mock_confluence = MagicMock()
        mock_confluence_class.return_value = mock_confluence

        # Execute
        service = ConfluenceService()

        # Assert
        mock_confluence_class.assert_called_once()
        self.assertEqual(service.confluence, mock_confluence)

    @patch('atlassian.Confluence')
    def test_get_page_by_url(self, mock_confluence_class):
        # Setup
        mock_confluence = MagicMock()
        mock_confluence_class.return_value = mock_confluence

        service = ConfluenceService()
        service.get_page_by_id = MagicMock(return_value={'id': '12345'})

        # Execute
        result = service.get_page_by_url('https://confluence.example.com/pages/12345/page')

        # Assert
        service.get_page_by_id.assert_called_once_with('12345')
        self.assertEqual(result, {'id': '12345'})

    @patch('atlassian.Confluence')
    def test_get_page_by_id(self, mock_confluence_class):
        # Setup
        mock_confluence = MagicMock()
        mock_confluence_class.return_value = mock_confluence
        mock_confluence.get_page_by_id.return_value = {'id': '12345'}

        service = ConfluenceService()

        # Execute
        result = service.get_page_by_id('12345')

        # Assert
        mock_confluence.get_page_by_id.assert_called_once_with(page_id='12345', expand='body.storage')
        self.assertEqual(result, {'id': '12345'})

    @patch('atlassian.Confluence')
    @patch('bs4.BeautifulSoup')
    def test_get_requirements(self, mock_bs, mock_confluence_class):
        # Setup
        mock_confluence = MagicMock()
        mock_confluence_class.return_value = mock_confluence

        service = ConfluenceService()
        mock_page = {
            'body': {
                'storage': {
                    'value': '<html><body>content</body></html>'
                }
            }
        }

        mock_bs_content = MagicMock()
        mock_bs.return_value = mock_bs_content

        mock_row = MagicMock()
        mock_row.get_text.return_value = 'Requirements text'
        service.get_reference_row = MagicMock(return_value=mock_row)

        # Execute
        result = service.get_requirements(mock_page, 'TEST-123')

        # Assert
        mock_bs.assert_called_once_with('<html><body>content</body></html>', 'lxml')
        service.get_reference_row.assert_called_once_with(mock_bs_content, 'TEST-123')
        mock_row.get_text.assert_called_once_with(separator='\n', strip=True)
        self.assertEqual(result, 'Requirements text')

    @patch('atlassian.Confluence')
    def test_get_reference_row(self, mock_confluence_class):
        # Setup
        mock_confluence = MagicMock()
        mock_confluence_class.return_value = mock_confluence

        service = ConfluenceService()

        # Create mock BeautifulSoup content
        mock_bs_content = MagicMock()
        mock_table = MagicMock()
        mock_row = MagicMock()
        mock_cell = MagicMock()

        mock_bs_content.find_all.return_value = [mock_table]
        mock_table.find_all.return_value = [mock_row]
        mock_row.find_all.return_value = [mock_cell]
        mock_cell.get_text.return_value = 'TEST-123 content'

        # Execute
        result = service.get_reference_row(mock_bs_content, 'TEST-123')

        # Assert
        mock_bs_content.find_all.assert_called_once_with('table')
        mock_table.find_all.assert_called_once_with('tr')
        mock_row.find_all.assert_called_once_with(['td', 'th'])
        self.assertEqual(result, mock_row)

        # Test not found case
        mock_cell.get_text.return_value = 'Other content'
        result = service.get_reference_row(mock_bs_content, 'TEST-123')
        self.assertIsNone(result)


class TestGeminiService(unittest.TestCase):
    @patch('gemini_webapi.GeminiClient')
    @patch('util.call_async_func')
    def test_init(self, mock_call_async, mock_gemini_client):
        # Setup
        mock_client = MagicMock()
        mock_gemini_client.return_value = mock_client

        # Execute
        service = GeminiService()

        # Assert
        mock_gemini_client.assert_called_once()
        mock_call_async.assert_called_once_with(mock_client.init, timeout=600, auto_refresh=False)
        self.assertEqual(service.gemini_client, mock_client)

    @patch('gemini_webapi.GeminiClient')
    @patch('util.call_async_func')
    def test_do_code_quality_analysis(self, mock_call_async, mock_gemini_client):
        # Setup
        mock_client = MagicMock()
        mock_gemini_client.return_value = mock_client

        # Mock the response from call_async_func
        mock_response = MagicMock()
        mock_response.text = "Analysis result"
        mock_call_async.side_effect = [None, mock_response]  # First for init, second for generate_content

        service = GeminiService()

        # Execute
        result = service.do_code_quality_analysis(
            issue_summary="Test summary",
            issue_requirements="Test requirements",
            issue_design="Test design",
            issue_comments="Test comments",
            mr_description="Test MR description",
            mr_diff="Test diff"
        )

        # Assert
        self.assertEqual(result, "Analysis result")
        self.assertEqual(mock_call_async.call_count, 2)
        # Check the second call to call_async_func
        args, kwargs = mock_call_async.call_args_list[1]
        self.assertEqual(args[0], mock_client.generate_content)
        self.assertIn('prompt', kwargs)
        self.assertIn('model', kwargs)


class TestCliFunctions(unittest.TestCase):
    @patch('services.gitlab.GitlabService')
    @patch('services.jira.JiraService')
    @patch('services.confluence.ConfluenceService')
    @patch('services.gemini.GeminiService')
    @patch('rich.console.Console')
    @patch('builtins.input')
    def test_code_review(self, mock_input, mock_console, mock_gemini_service,
                         mock_confluence_service, mock_jira_service, mock_gitlab_service):
        # Setup
        mock_jira = MagicMock()
        mock_jira_service.return_value = mock_jira
        mock_jira_issue = {
            'self': 'https://jira.example.com/TEST-123',
            'key': 'TEST-123',
            'fields': {
                JiraField.SUMMARY: 'Test summary'
            }
        }
        mock_jira.get_issue.return_value = mock_jira_issue
        mock_jira.get_issue_requirements.return_value = 'Test requirements'
        mock_jira.get_issue_design.return_value = 'Test design'
        mock_jira.get_issue_comments.return_value = 'Test comments'

        mock_gitlab = MagicMock()
        mock_gitlab_service.return_value = mock_gitlab
        mock_mr = MagicMock()
        mock_mr.web_url = 'https://gitlab.example.com/mr/1'
        mock_mr.title = 'TEST-123: Test MR'
        mock_mr.description = 'Test MR description'
        mock_gitlab.find_mr_by_jira_key.return_value = mock_mr
        mock_gitlab.get_plain_diff_from_mr.return_value = 'Test diff'

        mock_confluence = MagicMock()
        mock_confluence_service.return_value = mock_confluence

        mock_gemini = MagicMock()
        mock_gemini_service.return_value = mock_gemini
        mock_gemini.do_code_quality_analysis.return_value = 'Analysis result'

        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance

        # Test with 'y' input
        mock_input.return_value = 'y'

        # Execute
        code_review('TEST-123')

        # Assert
        mock_jira_service.assert_called_once()
        mock_jira.get_issue.assert_called_once_with('TEST-123')
        mock_gitlab_service.assert_called_once()
        mock_gitlab.find_mr_by_jira_key.assert_called_once_with('TEST-123')
        mock_confluence_service.assert_called_once()
        mock_jira.get_issue_requirements.assert_called_once()
        mock_jira.get_issue_design.assert_called_once()
        mock_jira.get_issue_comments.assert_called_once()
        mock_gitlab.get_plain_diff_from_mr.assert_called_once_with(mock_mr)
        mock_gemini_service.assert_called_once()
        mock_gemini.do_code_quality_analysis.assert_called_once()
        mock_console_instance.print.assert_called_once()
        mock_gitlab.add_comments.assert_called_once_with(mock_mr, 'Analysis result')

    @patch('builtins.open', new_callable=mock_open, read_data='[project]\nname = "test-project"\nversion = "1.0.0"')
    @patch('src.cli.tomllib.load')
    @patch('builtins.print')
    def test_print_version_text(self, mock_print, mock_tomllib_load, mock_file):
        # Setup
        mock_tomllib_load.return_value = {
            'project': {
                'name': 'test-project',
                'version': '1.0.0'
            }
        }

        # Execute
        print_version_text()

        # Assert
        mock_file.assert_called_once_with('pyproject.toml', 'rb')
        mock_tomllib_load.assert_called_once()
        mock_print.assert_called_once()

    def test_parse_args(self):
        # Test with jira_key
        with patch('sys.argv', ['cli.py', 'TEST-123']):
            args = parse_args()
            self.assertEqual(args.jira_key_or_mr_id, 'TEST-123')
            self.assertFalse(args.version)

        # Test with version flag
        with patch('sys.argv', ['cli.py', '-v']):
            args = parse_args()
            self.assertIsNone(args.jira_key)
            self.assertTrue(args.version)

    @patch('src.cli.parse_args')
    @patch('src.cli.print_version_text')
    @patch('src.cli.code_review')
    def test_main(self, mock_code_review, mock_print_version, mock_parse_args):
        # Test with version flag
        mock_args = MagicMock()
        mock_args.version = True
        mock_args.jira_key = None
        mock_parse_args.return_value = mock_args

        main()

        mock_parse_args.assert_called_once()
        mock_print_version.assert_called_once()
        mock_code_review.assert_not_called()

        # Reset mocks
        mock_parse_args.reset_mock()
        mock_print_version.reset_mock()
        mock_code_review.reset_mock()

        # Test with jira_key
        mock_args.version = False
        mock_args.jira_key = 'TEST-123'

        main()

        mock_parse_args.assert_called_once()
        mock_print_version.assert_not_called()
        mock_code_review.assert_called_once_with('TEST-123')


if __name__ == '__main__':
    unittest.main()
