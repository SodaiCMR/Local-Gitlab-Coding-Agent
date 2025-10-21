from gitlab_package.gitlab_client import GitlabClient, look_for_issues
from gitlab_package.config import LLM_MODEL, SYSTEM_PROMPT
from functions.call_function import call_function
from gitlab.exceptions import GitlabGetError
import ollama
import time
import sys

verbose_flag = False
if len(sys.argv) == 2 and sys.argv[-1] == "--verbose":
    verbose_flag = True

def agent_fix_issue(issue: str):
    messages = []
    system_prompt = {
        "role": "system",
        "content":SYSTEM_PROMPT
    }
    messages.append(system_prompt)

    issue_id = int(str(issue).split(" ")[-1])
    msg = {"role":"user", "content":issue}
    messages.append(msg)
    while True:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=messages,
            tools=[
                client.update_ai_branch,
                client.create_commit,
                client.create_merge_request,
                client.get_repo_info,
                client.get_repo_file_content,
            ],
        )
        if response is None:
            print('Response is malformed')
            break

        if content:= response.message.thinking:
            messages.append({"role": "assistant", "content": content})
            client.agent_comment_issue(issue_id, content)
        if tools := response.message.tool_calls:
            for tool in tools:
                function_output = call_function(client, tool, verbose_flag)
                tool_msg = {
                    "role": "tool",
                    "content": f"function_name:{tool.function.name} function_output:{function_output}"
                }
                messages.append(tool_msg)
                client.agent_comment_issue(issue_id, function_output)
        else:
            content = getattr(response.message, "content", None)
            if content and str(content).strip():
                client.agent_comment_issue(issue_id, response.message.content)
            client.issues_list[f"issue{issue_id}"]['state'] = "fixed"
            break
    return

if __name__ == "__main__":
    client = None
    for _ in range(5):
        try:
            client = GitlabClient()
            break
        except GitlabGetError as e:
            print(f'{e} occurred')
            time.sleep(2)

    if client is None:
        sys.exit()

    while True:
        while not (issues:= look_for_issues(client)):
            print('no issue found yet')
            continue
        for issue in issues:
            client.agent_comment_issue(int(str(issue).split(" ")[-1]), "Jetons un coup d'oeil au ticket👀...")
            agent_fix_issue(issue)