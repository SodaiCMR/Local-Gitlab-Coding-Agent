from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file
from gitlab_package.gitlab_client import GitlabClient

working_directory = "calculator"

def call_function(client, tool, verbose=False):
    if verbose:
        print(f'calling function: {tool.function.name}({tool.function.arguments})')
    else:
        print(f'calling function: {tool.function.name}')

    result = ""
    match tool.function.name:
        # case "get_files_info":
        #     result = get_files_info(working_directory, **tool.function.arguments)
        # case "get_file_content":
        #     result = get_file_content(working_directory, **tool.function.arguments)
        # case "run_python_file":
        #     result = run_python_file(working_directory, **tool.function.arguments)
        # case "write_file":
        #     result = write_file(working_directory, **tool.function.arguments)
        case "agent_fix_issue":
            result = client.agent_fix_issue(**tool.function.arguments)

    if result == "":
        return f'Error: Unknow function name {tool.function.name}'

    return result
