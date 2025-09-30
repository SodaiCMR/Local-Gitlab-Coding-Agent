import gitlab
import logging
from config import GITLAB_PROJECT_ID, GITLAB_PRIVATE_TOKEN, GITLAB_URL

class GitlabClient:
    def __init__(self):
        self.gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_PRIVATE_TOKEN)
        self.gl.auth()
        self.project = self.gl.projects.get(int(GITLAB_PROJECT_ID))
        logging.info(f"connected to GitLab project {GITLAB_PROJECT_ID}")

    def get_project_issues(self):
        issues = self.project.issues.list(all=True)
        return issues

    def get_project_merge_requests(self):
        return self.project.mergerequests.get()


client = GitlabClient()
issues = client.get_project_issues()
[print(issue.description) for issue in issues]
