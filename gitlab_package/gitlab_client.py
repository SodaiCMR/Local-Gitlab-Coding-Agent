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

    def get_ai_agent_issues(self):
        issues = self.project.issues.list(state='opened', labels='ai:agent')
        return issues

    def create_merge_request(self):
        data = {
            'source_branch': 'ai_branch',
            'target_branch': 'main',
            'title': "issue_fix",
            'labels': ['ai:agent'],
            'description': f'closes #{look_for_issues(self)}',
        }
        self.project.mergerequests.create(data)

    def create_commit(self):
        data = {
            'branch': 'ai_branch',
            'commit_message': 'created a hello world script', #TODO AI message
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'hello.py',
                    'content': 'print("hello, world")\n',
                }
            ]
        }
        self.project.commits.create(data)


def look_for_issues(client):
    #TODO take the time in consideration
    # Only the first issue
    # time.sleep(2)
    issues = client.get_ai_agent_issues()
    return issues[0].iid
    # for issue in issues:
    #     issue_details = f"title: {issue.title}, description: {issue.description}".strip()
    #     issue_iids = i
    #     return issue_details
        # return issue.iid

if __name__ == "__main__":
    client = GitlabClient()
    # print(look_for_issues(client))
    # client.create_commit()
    # print(client.project.commits.list(ref_name='ai_branch',get_all=True))
    client.create_merge_request()
#     while True:
#         look_for_issues(client)

