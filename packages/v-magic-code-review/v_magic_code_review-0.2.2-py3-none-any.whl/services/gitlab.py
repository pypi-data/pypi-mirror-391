import gitlab
from gitlab.v4.objects import MergeRequest

from config import GitlabConfig


class GitlabService:
    def __init__(self):
        gl = gitlab.Gitlab(GitlabConfig.HOST, private_token=GitlabConfig.TOKEN)
        gl_project = gl.projects.get(GitlabConfig.PROJECT_ID)

        self.gl = gl
        self.gl_project = gl_project

    def get_mr(self, mr_id):
        return self.gl_project.mergerequests.get(mr_id)

    def find_mr_by_jira_key(self, jira_key):
        merge_requests = self.gl_project.mergerequests.list(state='opened', iterator=True)
        for mr in merge_requests:
            if jira_key in mr.title:
                return mr
        return None

    def get_diff_from_mr(self, mr: MergeRequest) -> tuple[str, dict[str, str]]:
        latest_diff_version = max([it.id for it in mr.diffs.list(all=True)])
        latest_diff = mr.diffs.get(latest_diff_version)

        full_plain_diff = []
        file_and_diff = {}

        for change in latest_diff.diffs:
            old_path = change.get('old_path')
            new_path = change.get('new_path')
            diff_content = change.get('diff')
            new_file = change.get('new_file')
            renamed_file = change.get('renamed_file')
            deleted_file = change.get('deleted_file')

            # Skip files based on an extension or path
            if (
                any(old_path.endswith(ext) for ext in GitlabConfig.DIFF_EXCLUDE_EXT)
                or any(old_path.startswith(path) for path in GitlabConfig.DIFF_EXCLUDE_PATH)
            ):
                continue
            # Skip files based on an extension or path
            if (
                any(new_path.endswith(ext) for ext in GitlabConfig.DIFF_EXCLUDE_EXT)
                or any(new_path.startswith(path) for path in GitlabConfig.DIFF_EXCLUDE_PATH)
            ):
                continue
            # Skip empty diffs
            if not diff_content:
                continue

            diff_git_line = f"diff --git a/{old_path} b/{new_path}"
            full_plain_diff.append(diff_git_line)

            # Handle file mode changes, new files, deleted files, and renamed files
            if new_file:
                full_plain_diff.append("new file mode 100644")  # Assuming typical file mode
                full_plain_diff.append("--- /dev/null")
                full_plain_diff.append(f"+++ b/{new_path}")
            elif deleted_file:
                full_plain_diff.append(f"--- a/{old_path}")
                full_plain_diff.append("+++ /dev/null")
            elif renamed_file:
                full_plain_diff.append(f"rename from {old_path}")
                full_plain_diff.append(f"rename to {new_path}")
                full_plain_diff.append(f"--- a/{old_path}")
                full_plain_diff.append(f"+++ b/{new_path}")
            else:
                full_plain_diff.append(f"--- a/{old_path}")
                full_plain_diff.append(f"+++ b/{new_path}")
            full_plain_diff.append(diff_content)
            file_and_diff[new_path] = diff_content
        return "\n".join(full_plain_diff), file_and_diff

    def add_comments(self, mr, body):
        mr.notes.create({'body': body})
