import gitlab
import logging
import time
from config import GITLAB_PROJECT_ID, GITLAB_PRIVATE_TOKEN, GITLAB_URL

class GitlabClient:
    def __init__(self):
        self.gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_PRIVATE_TOKEN)
        self.gl.auth()
        self.project = self.gl.projects.get(int(GITLAB_PROJECT_ID))
        logging.info(f"connected to GitLab project {GITLAB_PROJECT_ID}")

    def get_project_issues(self):
        issues = self.project.issues.list(all=True, state='opened', labels='ai:agent')
        return issues

    def get_project_merge_requests(self):
        return self.project.mergerequests.list(all=True, state='opened')

def look_for_issues(client):
    #TODO take the time in consideration
    # time.sleep(2)
    issues = client.get_project_issues()
    for issue in issues:
        issue_details =f"title: {issue.title}, description: {issue.description}".strip()
        print(issue_details)
    print("\n")
    # [print(issue.description) for issue in issues]

if __name__ == "__main__":
    client = GitlabClient()
    while True:
        look_for_issues(client)

# look_for_issues(client)