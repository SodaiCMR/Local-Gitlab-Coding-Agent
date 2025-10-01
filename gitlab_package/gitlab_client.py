import gitlab
import logging
import time
# from gitlab_package.config import GITLAB_PROJECT_ID, GITLAB_PRIVATE_TOKEN, GITLAB_URL
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

    def create_merge_request(self):
        # mr_description_template = project.merge_request_templates.get("default")
        merge_request = self.project.mergerequests.create(
            {
                'source_branch': 'ai_branch',
                'target_branch': 'main',
                'title': "issue_fix",
                'labels': ['ai:agent'],
                # 'description': mr_description_template.content
            }
        )

    def create_commit(self):
        data = {
            'branch': 'ai_branch',
            'commit_message': 'created a hello world script', #TODO AI message
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'hello.py',
                    'content': 'print("hello, world")\n'
                }
            ]
        }
        self.project.commits.create(data)


def look_for_issues(client):
    #TODO take the time in consideration
    # time.sleep(2)
    issues = client.get_project_issues()
    for issue in issues:
        issue_details =f"title: {issue.title}, description: {issue.description}".strip()
        return issue_details

if __name__ == "__main__":
    client = GitlabClient()
    # client.create_commit()
    print(client.project.commits.list(ref_name='ai_branch',get_all=True))
    # client.create_merge_request()
#     while True:
#         look_for_issues(client)

# look_for_issues(client)