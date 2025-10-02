from fastapi import FastAPI
import ollama
import sys
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from functions.call_function import call_function
from gitlab_package.gitlab_client import GitlabClient, look_for_issues

max_iters = 20 #TODO check the max number of iterations
app = FastAPI()
client = GitlabClient()

@app.post("/generate")
def generate():
    verbose_flag = False
    messages = []
    system_prompt = {
        "role": "system",
        "content": """
    You are a helpful AI coding agent.
    You help to fix the gitlab issues;
    they are phrased based on three key points: the issue's title, it's description and it's id.
    when a user ask questions about a directory or project, you should first try to know which files and folders are inside the project

    When fixing a GitLab issue, follow this workflow:
    
    When fixing a GitLab issue, follow this workflow:
    
    - Always work on the branch 'ai_branch'. If it does not exist, create it from the default branch.
    - For each modification, create a commit with a clear and concise message describing the change.
    - Allowed commit actions are: 'create', 'delete', 'move', or 'update'.
    - After all commits are created, open a merge request targeting the default branch and link it to the issue.
    - Ensure that commit messages are meaningful and related to the issue.
    - The final goal is to provide a merge request that fixes the assigned issue.
    
    All paths you provide should be relative to the working directory.
    You should never provide the working directory in your function calls as it is automatically injected for security reasons !
    IMPORTANT: Only call tools when absolutely necessary to perform an action you cannot do from the model alone. 
    If you can produce the user's final answer without calling any tools, respond directly and do not issue any tool
    """
    }
    messages.append(system_prompt)

    if len(sys.argv) == 2 and sys.argv[-1] == "--verbose":
        verbose_flag = True
    issue = look_for_issues(client)
    msg = {"role":"user", "content":issue}
    messages.append(msg)
    for _ in range(max_iters + 1):
        if _ == max_iters:
            print(f'Reached the maximum number of iterations {max_iters}')
            break
        response = ollama.chat(
            model="qwen2.5",
            messages=messages,
            tools=[
                client.agent_fix_issue,
            ],
        )
        if response is None:
            print('Response is malformed')
            break
        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                content = getattr(response.message, "content", None)
                if content and str(content).strip():
                    messages.append({"role": "assistant", "content": content})
                function_output = call_function(client, tool, verbose_flag)
                tool_msg = {"role": "tool", "content": function_output}
                messages.append(tool_msg)
            # if verbose_flag:
            #     print(f"User prompt: {msg['content']}")
            #     print(f"Prompt tokens: {response.prompt_eval_count}")
            #     print(f"Response tokens: {response.eval_count}")
        else:
            print(response.message.content)
            break
    return


if __name__ == "__main__":
    generate()
