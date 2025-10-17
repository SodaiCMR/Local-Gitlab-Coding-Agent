import ollama
import sys
from functions.call_function import call_function
from gitlab_package.gitlab_client import GitlabClient, look_for_issues

verbose_flag = False
if len(sys.argv) == 2 and sys.argv[-1] == "--verbose":
    verbose_flag = True

def start_llm_server(issue: str):
    messages = []
    system_prompt = {
        "role": "system",
        "content": """
    You are a helpful AI coding agent.
    You help to fix the gitlab issues by proceeding step by step;
    they are phrased based on three key points: the issue's title, its description and its id.
    
    You can perform the following actions :
    - Update or create the ai_branch.
    - Write or update code or content of a given file and commit changes to ai_branch.
    - Add comment to a gitlab issue.
    - Get the file content of a given file in a repository.
    - Get the repository information's (files and structure).
    - Create a merge request.

    When fixing a GitLab issue, follow this workflow:
        
        First understand what the issue is about:
            If the issue concerns retrieving repository information:
                - If the issue is about a folder (directory structure):
                    - Use the corresponding function to list the content of the folder
                - If the issue is about a file (its content):
                    - Use the corresponding function to fetch and decode the file content
            Finally post the result back to the issue:
                - After retrieving the required information, always the call to add comment to the issue's discussion
            
            Else:
                - Always first ensure that the branch 'ai_branch' is up-to-date or create it by calling the correct function.
                - For each modification, create a commit with a clear and concise message describing the change.
                - Allowed commit actions are: 'create', 'delete', 'move', or 'update'.
                - After all commits are created, open a merge request targeting the default branch and link it to the issue.
                - Ensure that commit messages are meaningful and related to the issue.
                - The final goal is to provide only one merge request that fixes the assigned issue.
    
    IMPORTANT: Only call tools when absolutely necessary to perform an action you cannot do from the model alone. 
    If you can produce the user's final answer without calling any tools, respond directly and do not issue any tool
    """
    }
    messages.append(system_prompt)

    issue_id = int(str(issue).split(" ")[-1])
    msg = {"role":"user", "content":issue}
    messages.append(msg)
    while True:
        response = ollama.chat(
            model="qwen3:8b",
            messages=messages,
            tools=[
                client.update_ai_branch,
                client.create_commit,
                client.create_merge_request,
                client.get_repo_info,
                client.agent_comment_issue,
                client.get_repo_file_content,
            ],
        )
        if response is None:
            print('Response is malformed')
            break
        client.agent_comment_issue(issue_id, response.message.thinking)
        content = getattr(response.message, "content", None)
        if content and str(content).strip():
            messages.append({"role": "assistant", "content": content})
            client.agent_comment_issue(issue_id, content)
        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                function_output = call_function(client, tool, verbose_flag)
                tool_msg = {
                    "role": "tool",
                    "content": f"function_name:{tool.function.name} function_output:{function_output}"
                }
                messages.append(tool_msg)
                client.agent_comment_issue(issue_id, function_output)
        else:
            print(response.message.content)
            break
    return

if __name__ == "__main__":
    while True:
        while True:
            try:
                client = GitlabClient()
                break
            except Exception as e:
                print(f'{e} occurred')
        while not look_for_issues(client):
            print('no issue found yet')
            continue
        issue = look_for_issues(client)
        client.agent_comment_issue(int(str(issue).split(" ")[-1]), 'Looking at the issue👀...')
        start_llm_server(issue)