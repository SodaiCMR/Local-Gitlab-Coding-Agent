import gitlab
import logging
import time
from gitlab_package.config import GITLAB_PROJECT_ID, GITLAB_PRIVATE_TOKEN, GITLAB_URL
# from config import GITLAB_PROJECT_ID, GITLAB_PRIVATE_TOKEN, GITLAB_URL
from gitlab.exceptions import GitlabGetError

class GitlabClient:
    def __init__(self):
        self.gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_PRIVATE_TOKEN)
        self.gl.auth()
        self.project = self.gl.projects.get(int(GITLAB_PROJECT_ID))
        logging.info(f"connected to GitLab project {GITLAB_PROJECT_ID}")

    def get_ai_agent_issues(self):
        issues = self.project.issues.list(state='opened', labels='ai:agent')
        return issues[0] #TODO Only the first issue for the moment

    def create_merge_request(self, found_issue):
        data = {
            'source_branch': 'ai_branch',
            'target_branch': 'main',
            'title': "issue_fix",
            'labels': ['ai:agent'],
            'description': f'closes #{found_issue}',
        }
        self.project.mergerequests.create(data)
        return f'created merge request for {found_issue[1]}'

    def create_commit(self, action: str,commit_message: str, file_path: str, content: str):
        data = {
            'branch': 'ai_branch',
            'commit_message': commit_message, #TODO AI message
            'actions': [
                {
                    'action': action,
                    'file_path': file_path,
                    'content': content,
                }
            ]
        }
        self.project.commits.create(data)

    def update_ai_branch(self):
        try:
            main_branch = self.project.branches.get("main")
        except GitlabGetError:
            main_branch = self.project.branches.get("master") #In case the main branch is master instead of main

        try:
            ai_branch = self.project.branches.get("ai_branch")
            if ai_branch.commit['id'] !=  main_branch.commit['id']:
                self.project.branches.delete('ai_branch')
                self.project.branches.create({'branch': 'ai_branch','ref': main_branch.commit['id']})
        except GitlabGetError:
            self.project.branches.create({'branch': 'ai_branch','ref': main_branch.commit['id']})

    def agent_fix_issue(self, commit_messages: list[str], action: str,  file_path: str, content: str, issue):
        """
            Automatically fixes a GitLab issue.

            The agent updates the 'ai_branch' on GitLab, creates commits for each modification,
            and finally opens a merge request.

            Args:
                commit_messages (list[str]): A list of commit messages describing each modification.
                action (str): The commit action to perform. Can be one of: 'create', 'delete', 'move', or 'update'.
                file_path (str): The path of the file to be committed.
                content (str): The new content to include in the file for the commit.
                issue: The GitLab issue object that is being fixed.

            Returns:
                str: A message indicating whether the merge request was successfully created.
    """
        self.update_ai_branch()
        for commit_message in commit_messages:
            self.create_commit(action, commit_message, file_path, content)
        return self.create_merge_request(issue[0])

def look_for_issues(client):
    #TODO take the time in consideration
    # Only the first issue
    # time.sleep(2)
    issue = client.get_ai_agent_issues()
    issue_details = f"title: {issue.title}, description: {issue.description}".strip()
    return issue.iid, issue_details

if __name__ == "__main__":
    client = GitlabClient()
    # print(look_for_issues(client))
    # client.create_commit()
    # print(client.project.commits.list(ref_name='ai_branch',get_all=True))
    client.create_merge_request()
#     while True:
#         look_for_issues(client)

