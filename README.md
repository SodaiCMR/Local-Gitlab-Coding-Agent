# AI Coding Assistant

This project is an automated AI coding agent capable of fixing GitLab issues. It uses Ollama to interact with a Local Language Model (LLM) and the `python-gitlab` library to interact with your GitLab repository.

## Features

- Monitors GitLab issues labeled with `ai:agent`.
- Analyzes the issue title and description.
- Interacts with the repository (reads files, lists directories).
- Creates a dedicated branch for the fix.
- Generates code fixes and commits them.
- Opens a Merge Request when the fix is ready.

## configuration
Create a `.env` file at the root of the project with the following variables:

```dotenv
GITLAB_PRIVATE_TOKEN="<your_gitlab_token>"
GITLAB_URL="https://gitlab.com/"
GITLAB_PROJECT_ID="<your_project_id>"
```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_folder>
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Ollama:**
    Ensure [Ollama](https://ollama.com/) is installed and running on your machine.
    Pull the model you intend to use:
    ```bash
    ollama pull qwen2.5:14b
    ```
    *Important: The model you use must be capable of tool usage (function calling).*

## Usage

Run the `main.py` script with the required argument.

### Command Line Arguments

*   `--model` (Required): The name of the Ollama model to use.
*   `--ctx`: The context window size (number of tokens). Default: 32768.
*   `--predict`: The maximum number of tokens to predict. Default: 8192.
*   `--verbose`: Enable verbose output in the console.

### Example Run

```bash
python main.py --model qwen2.5:14b --ctx 32768 --predict 8192 --verbose
```

## How it works

1.  The script polls GitLab for open issues with the label `ai:agent`.
2.  When an issue is found, it starts an LLM session.
3.  The agent "thinks" about the problem, exploring the codebase using provided tools.
4.  It modifies the code on a new branch `ai_branch_issue<id>`.
5.  Finally, it submits a Merge Request.

## Contributing

Feel free contributing to improve this tool!
