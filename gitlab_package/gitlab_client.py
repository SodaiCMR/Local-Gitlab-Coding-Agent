from gitlab_package.config import GITLAB_PROJECT_ID, GITLAB_PRIVATE_TOKEN, GITLAB_URL
from gitlab.exceptions import GitlabGetError
import gitlab
import time

class GitlabClient:
    def __init__(self):
        self.gl = gitlab.Gitlab(GITLAB_URL, private_token=GITLAB_PRIVATE_TOKEN)
        self.gl.auth()
        self.project = self.gl.projects.get(int(GITLAB_PROJECT_ID))
        self.issues_list = {}

    def get_ai_agent_issues(self):
        issues_to_fix = []
        try:
            issues = self.project.issues.list(order_by='created_at', sort='asc', state='opened', labels='ai:agent')
            if not issues:
                return {}
            else:
                for issue in issues:
                    related_mrs = issue.related_merge_requests()
                    if related_mrs and any(mr['state'] == 'opened' for mr in related_mrs):
                        continue
                    elif f"issue{issue.iid}" in self.issues_list.keys() and self.issues_list[f"issue{issue.iid}"]["state"] == "fixed":
                        continue
                    else:
                        self.issues_list[f"issue{issue.iid}"] = {"issue": issue, "state": "to fix"}
                        issues_to_fix.append(issue)
            return issues_to_fix
        except GitlabGetError as e:
            return f'Error: {e} occurred'

    def create_merge_request(self, found_issue_id: int, target_branch='main'):
        """
             Automatically create a merge request when done creating commits for a GitLab issue.

             Args:
                found_issue_id (int): The GitLab issue's id that is being fixed its given in the issue_details.
                target_branch (str): The branch on which the merge request should be done. If not specified use "main".
             Returns:
                 str: A message indicating whether the merge request was successfully created.
        """

        issue = self.project.issues.get(found_issue_id)
        related_mrs = issue.related_merge_requests()
        for mr in related_mrs:
            if mr['state'] == "opened":
                return f'Can not create another merge request for issue#{found_issue_id} since one is already opened'

        data = {
            'source_branch': f"ai_branch_issue{found_issue_id}",
            'target_branch': target_branch,
            'title': f"issue#{found_issue_id} fix",
            'labels': ['ai:agent'],
            'description': f'closes #{found_issue_id}',
        }
        try:
            main_branch = self.project.branches.get(target_branch)
            ai_branch = self.project.branches.get(f"ai_branch_issue{found_issue_id}")
            if ai_branch.commit['id'] ==  main_branch.commit['id']:
                return "Can't merge request with no commits"
            else:
                self.project.mergerequests.create(data)
                return f'Done fixing the issue and successfully created the merge request for issue#{found_issue_id}'
        except GitlabGetError as e:
            return f'Error: {e} occurred'

    def create_commit(self, issue_id: int, action: str, commit_message: str, file_path: str, content: str=''):
        """
             Automatically create commits for a GitLab issue

             Args:
                 issue_id (int): The id of the issue being fixed.
                 commit_message (str): The commit message describing each modification.
                 action (str): The commit action to perform. Can be one of: 'create', 'delete', 'update'.
                 file_path (str): The path of the file to be committed.
                 content (str): The new content to write inside the file related to the commit.Therefore, for actions like 'delete' just use ''.

             Returns:
                 str: A message indicating whether the merge request was successfully created.
        """
        data = {
            'branch': f"ai_branch_issue{issue_id}",
            'commit_message': commit_message,
            'actions': [
                {
                    'action': action,
                    'file_path': file_path,
                    'content': content.replace('\r\n','\n')
                }
            ]
        }
        try:
            self.project.commits.create(data)
            return f'successfully committed {commit_message}'
        except GitlabGetError as e:
            return f'Error: {e} occurred'

    def update_ai_branch(self, issue_id: int, target_branch='main'):
        """
            Create or update the ai_branch when addressing a GitLab issue before committing.
            If ai_branch already exists but is outdated, delete and recreate it based on the latest main.
            Otherwise, simply create it from the up-to-date main branch.
            Args:
                issue_id (int): The id of the issue being fixed.
                target_branch (str): The branch to which the ai_branch should be updated. If not specified use "main".

            Returns:
                str: A message indicating whether the ai_branch was successfully created and based to the latest main.
        """
        ai_branch_name = f"ai_branch_issue{issue_id}"
        try:
            main_branch = self.project.branches.get(target_branch)
        except GitlabGetError as e:
            return f'Error {e} occurred'
        try:
            ai_branch = self.project.branches.get(ai_branch_name)
            if ai_branch.commit['id'] !=  main_branch.commit['id']:
                self.project.branches.delete(ai_branch_name)
                print('deleted ai_branch')
                self.project.branches.create({'branch': ai_branch_name,'ref': main_branch.commit['id']})
                print('recreated ai_branch')
        except GitlabGetError:
            self.project.branches.create({'branch': ai_branch_name,'ref': main_branch.commit['id']})
        return 'ai_branch is now up to date!'

    def agent_comment_issue(self, issue_id: int, content: str):
        """
            Add comment to an issue discussion.

        Args:
            issue_id (int): The GitLab issue's id that is being fixed its given in the issue_details.
            content (str): The content that need to be added to the issue discussion.

        Returns
            str: The message that needs to be added to the issue's discussion.
        """
        try:
            issue = self.project.issues.get(issue_id)
            issue.notes.create({"body": content})
            return f'Added comment to issue#{issue_id} discussion'
        except GitlabGetError as e:
            return f'Error: {e} occurred'

    def get_repo_info(self, path: str='.'):
        """
           Lists all the items in the specified directory, inside the repository.

           Args:
               path (str): The directory to list files. If not provided use '.'
               lists files in the repository itself.
           Returns:
               str: The list of the files and directories in the specified directory inside the repository.
        """
        repo_infos = ''
        try:
            items = self.project.repository_tree(path=path)
            for item in items:
                if item['type'] == 'tree':
                    repo_infos += f"- {item['path']}: is_dir= True\n"
                    repo_infos += self.get_repo_info(path=item['path'])
                elif item['type'] == 'blob':
                    repo_infos += f"- {item['path']}: is_dir= False\n"
        except GitlabGetError as e:
            return f'Error: {e} occurred'

        return repo_infos

    def read_file_content(self, file_path: str):
        """
            reads the content of the given file as a string.
            Args:
                file_path (str): The file path to read.
            Returns:
                str: The content of the given file path
        """
        try:
            repo_file = self.project.files.raw(file_path=file_path, ref='main')
            return repo_file.decode('utf-8')
        except GitlabGetError as e:
            return f'Error: {e} occurred'


def look_for_issues(client):
    time.sleep(2) # look for issue every 2 seconds
    issue_details = []
    try:
        issues = client.get_ai_agent_issues()
        if not issues:
            return issues
        for issue in issues:
            issue_details.append(f"title: {issue.title}, description: {issue.description}, issue_id: {issue.iid}".strip())
        return issue_details
    except GitlabGetError as e:
        return f'Error: {e} occurred'