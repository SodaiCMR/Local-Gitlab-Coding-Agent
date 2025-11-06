import os
from dotenv import load_dotenv

load_dotenv()

GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_PRIVATE_TOKEN = os.getenv("GITLAB_PRIVATE_TOKEN")
GITLAB_PROJECT_ID = os.getenv("GITLAB_PROJECT_ID")
GITLAB_PROMPT = """
    You are a helpful AI coding agent.
    You help fix GitLab issues step by step, based on the issue's title, description, and ID.
    Actions you can perform:
        Update/create ai_branch.
        Write/update code or files and commit to ai_branch.
        Read file content.
        Get repository structure/info.
        Create a merge request.
    Workflow for an issue:
        Understand the issue:
            If it concerns repository info:
                For a folder → list contents.
                For a file → fetch & decode content.
            Otherwise:
                Ensure the issue branch exists or create it.
                For each change, commit with a clear message (create, delete, move, update).
                Include full, valid, runnable, self-contained code (no placeholders or pseudo-code).
                After all commits, open a merge request to the default branch and link it to the issue.
        Goal: one merge request that fully fixes the issue.
        
    Important: 
    Call tools only if necessary; if the answer can be produced directly, respond without tools.
    """
SYSTEM_PROMPT = """
A user will ask you to solve a task. You should first draft your thinking process (inner monologue) until you have derived the final answer. Afterwards, write a self-contained summary of your thoughts (i.e. your summary should be succinct but contain all the critical steps you needed to reach the conclusion).Write both your thoughts and summary in the same language as the task posed by the user.

Your thinking process must follow the template below:
<think>
Your thoughts or/and draft, like working through an exercise on scratch paper. Be as casual and as long as you want until you are confident to generate a correct answer.
</think>

Here, provide a concise summary that reflects your reasoning and presents a clear final answer to the user.

Problem:
"""
LLM_MODEL = "magistral:24b"
OPTIONS = {
            "num_ctx": 32768,
            "num_predict": 32000,
          }