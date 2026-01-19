from services.gitlab_service import GitlabClient, look_for_issues
from services.config import GITLAB_PROMPT
from tools.dispatcher import call_function
import ollama
import time
import sys
import argparse

# Setup argument parser
parser = argparse.ArgumentParser(description="GitLab AI Coding Assistant")
parser.add_argument("--model", type=str, required=True, help="LLM Model to use (e.g., qwen2.5:14b)")
parser.add_argument("--ctx", type=int, default=32768, help="Context token size (num_ctx)")
parser.add_argument("--predict", type=int, default=8192, help="Max output tokens (num_predict)")
parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

args = parser.parse_args()

LLM_MODEL = args.model
OPTIONS = {
    "num_ctx": args.ctx,
    "num_predict": args.predict,
}
verbose_flag = args.verbose

def agent_fix_issue(issue: str):
    try_count, output_token, max_tries = 0, 0, 20
    messages = []
    system_prompt = [
        {"role":"system", "content":GITLAB_PROMPT},
    ]
    messages.extend(system_prompt)

    issue_id = int(issue.split(" ")[-1])
    msg = {"role":"user", "content":issue}
    messages.append(msg)
    while try_count <= max_tries:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=messages,
            tools=[
                client.update_ai_branch,
                client.create_commit,
                client.create_merge_request,
                client.get_repo_info,
                client.read_file_content,
            ],
            options=OPTIONS,
            think=True
        )
        if try_count == max_tries - 1:
            messages.append({"role": "assistant", "content": "reached max number of iterations. Stopping reasoning."})

        if thinking:= response.message.thinking:
            client.agent_comment_issue(issue_id, "Thinking...")
            if try_count == 0:
                client.agent_comment_issue(issue_id, thinking)
                messages.append({"role": "assistant", "thinking": thinking})

        if verbose_flag:
            output_token += response.eval_count
            print(f"Prompt tokens: {response.prompt_eval_count}")
            print(f"Response tokens: {output_token}")

        if tools := response.message.tool_calls:
            for tool in tools:
                function_name = tool.function.name
                client.agent_comment_issue(issue_id, f"calling function {function_name}...")
                function_output = call_function(client, tool, verbose_flag)
                tool_msg = {
                    "role": "tool",
                    "tool_name": function_name,
                    "content": f"function_output:{function_output}"
                }
                messages.append(tool_msg)
        else:
            content = getattr(response.message, "content", None)
            if content and str(content).strip():
                client.agent_comment_issue(issue_id, response.message.content)
            client.issues_list[f"issue{issue_id}"]['state'] = "fixed"
            break

        try_count += 1
    return

if __name__ == "__main__":
    client = None
    for _ in range(5):
        try:
            client = GitlabClient()
            break
        except Exception as e:
            print(f'{e} occurred')
            time.sleep(2)

    if client is None:
        sys.exit()

    while not (issues:= look_for_issues(client)):
        print('no issue found yet')
        continue
    print(" === issue found === ")
    for issue in issues:
        client.agent_comment_issue(int(issue.split(" ")[-1]), "Taking a look at the ticket👀...")
        agent_fix_issue(issue)
