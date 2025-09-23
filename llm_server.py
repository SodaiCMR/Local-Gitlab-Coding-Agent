from fastapi import FastAPI
import ollama
import sys
from functions.get_files_info import  get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from functions.call_function import call_function

app = FastAPI()
@app.post("/generate")
def generate():
    verbose_flag = False
    messages = []
    system_prompt = {
        "role": "system",
        "content": """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files
    
    All paths you provide should be relative to the working directory. You should never provide the working directory in your function calls as it is automatically injected for security reasons !
    """
    }

    available_functions = {
        'get_files_info':get_files_info,
        'get_file_content':get_file_content,
        'run_python_file':run_python_file,
        'write_file':write_file,
    }

    messages.append(system_prompt)
    if len(sys.argv) < 2:
        print("Prompt missing !")
        sys.exit(1)
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    msg = {"role":"user", "content":sys.argv[1]}
    messages.append(msg)
    response = ollama.chat(
        model="qwen2.5",
        messages=messages,
        tools=[get_files_info,get_file_content,run_python_file,write_file],
    )

    if response.message.tool_calls is None:
        print('Response is malformed')
        return
    for tool in response.message.tool_calls:
        function_to_call = available_functions.get(tool.function.name)
        if function_to_call:
            # print(f'calling function: {tool.function.name}({tool.function.arguments})')
            print(call_function(tool, verbose_flag))
        else:
            print(response.message.content)


    if verbose_flag:
        print("\n")
        print(f"User prompt: {msg['content']}")
        print(f"Prompt tokens: {response['prompt_eval_count']}")
        print(f"Response tokens: {response['eval_count']}")

if __name__ == "__main__":
    generate()