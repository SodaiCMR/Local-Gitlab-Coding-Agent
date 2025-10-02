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
        try:
            issues = self.project.issues.list(state='opened', labels='ai:agent')
            return issues[0] #TODO Only the first issue for the moment
        except Exception as e:
            return f'Error: {e} occurred'

    def create_merge_request(self, found_issue_id):
        data = {
            'source_branch': 'ai_branch',
            'target_branch': 'main',
            'title': "issue_fix",
            'labels': ['ai:agent'],
            'description': f'closes #{found_issue_id}',
        }
        try:
            self.project.mergerequests.create(data)
            return f'created merge request for {found_issue_id}'
        except Exception as e:
            return f'Error: {e} occurred'

    def create_commit(self, action: str,commit_message: str, file_path: str, content: str):
        data = {
            'branch': 'ai_branch',
            'commit_message': commit_message,
            'actions': [
                {
                    'action': action,
                    'file_path': file_path,
                    'content': content,
                }
            ]
        }
        try:
            self.project.commits.create(data)
            return f'{commit_message}'
        except Exception as e:
            return f'Error: {e} occurred'

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
        return 'ai_branch is now up to date!'

    def agent_fix_issue(self, issue_id, commit_messages: list[str], action: str,  file_path: str, content: str, ):
        """
            Automatically fixes a GitLab issue.

            The agent updates the 'ai_branch' on GitLab, creates commits for each modification,
            and finally opens a merge request.

            Args:
                issue_id (int): The GitLab issue's id that is being fixed its given in the issue_details.
                commit_messages (list[str]): A list of commit messages describing each modification.
                action (str): The commit action to perform. Can be one of: 'create', 'delete', 'move', or 'update'.
                file_path (str): The path of the file to be committed.
                content (str): The new content to include in the file for the commit.

            Returns:
                str: A message indicating whether the merge request was successfully created.
    """
        self.update_ai_branch()
        for commit_message in commit_messages:
            self.create_commit(action, commit_message, file_path, content)
        return self.create_merge_request(issue_id)

    def agent_comment_issue(self, issue_id: int, content: str):
        """
            Add comment to an issue discussion.
            The agent add a comment to an issue when the issue details specify the need to get infos from the repository

        Args:
            issue_id (int): The GitLab issue's id that is being fixed its given in the issue_details.
            content (str): The content that need to be added to the issue discussion.

        Returns
            str: A message indicating whether the agent added a comment to the issue's discussion.
        """
        try:
            issue = self.project.issues.get(issue_id)
            issue.notes.create({"body": content})
            return f'Added comment to issue#{issue_id} discussion'
        except Exception as e:
            return f'Error: {e} occurred'

    def get_repo_info(self, path:str='.'):#TODO Check folder that need to be exlcuded
        """
           Lists all the items in the specified directory, inside the repository.

           Args:
               path (str): The directory to list files. If not provided use '.'
               lists files in the repository itself.
           Returns:
               str: The list of the files and directories in the specified directory inside the repository.
        """
        repo_infos = ''
        items = self.project.repository_tree(path=path)
        for item in items:
            if item['type'] == 'tree':
                repo_infos += f"- {item['path']}: is_dir= True\n"
                repo_infos += self.get_repo_info(path=item['path'])
            elif item['type'] == 'blob':
                repo_infos += f"- {item['path']}: is_dir= False\n"
        return repo_infos

    def get_repo_files_content(self):
        pass

    def write_repo_file(self):
        pass

    def run_repo_file(self):
        pass


def look_for_issues(client):
    #TODO take the time in consideration
    # Only the first issue
    # time.sleep(2)
    try:
        issue = client.get_ai_agent_issues()
        issue_details = f"title: {issue.title}, description: {issue.description}, issue_id: {issue.iid}".strip()
        return issue_details
    except Exception as e:
        return f'Error: {e} occurred'

if __name__ == "__main__":
    client = GitlabClient()
    # client.agent_comment_issue(5, 'Of course ! WHO THE HELL do you think I am .... ')
