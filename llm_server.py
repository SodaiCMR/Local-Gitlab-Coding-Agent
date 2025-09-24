from fastapi import FastAPI
import ollama
import sys
from functions.get_files_info import  get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from functions.call_function import call_function
max_iters = 20
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
    IMPORTANT: Only call tools when absolutely necessary to perform an action you cannot do from the model alone. 
    If you can produce the user's final answer without calling any tools, respond directly and do not issue any tool
    """
    }

    messages.append(system_prompt)
    if len(sys.argv) < 2:
        print("Prompt missing !")
        sys.exit(1)
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    msg = {"role":"user", "content":sys.argv[1]}
    messages.append(msg)

    for iter in range(max_iters):
        response = ollama.chat(
            model="qwen2.5",
            messages=messages,
            tools=[get_files_info,get_file_content,run_python_file,write_file],
        )

        if response is None:
            print('Response is malformed')
            return

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                content = getattr(response.message, "content", None)
                if content and str(content).strip():
                    messages.append({"role":"assistant", "content":content})

                function_output = call_function(tool, verbose_flag)
                tool_msg = {"role":"tool", "content":function_output}
                messages.append(tool_msg)
                # print(function_output)
                # print(tool_msg)

            # if verbose_flag:
            #     print("\n")
            #     print(f"User prompt: {msg['content']}")
            #     print(f"Prompt tokens: {response.prompt_eval_count}")
            #     print(f"Response tokens: {response.eval_count}")
        else:
            print(response.message.content)
            return

if __name__ == "__main__":
    generate()