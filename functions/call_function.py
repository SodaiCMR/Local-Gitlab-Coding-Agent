from functions.run_python_file import run_python_file
from functions.write_file import write_file
def call_function(client, tool, verbose=False):
    if verbose:
        print(f'calling function: {tool.function.name}({tool.function.arguments})')
    else:
        print(f'calling function: {tool.function.name}')

    result = ""
    match tool.function.name:
        # case "run_python_file":
        #     result = run_python_file(working_directory, **tool.function.arguments)
        # case "write_file":
        #     result = write_file(working_directory, **tool.function.arguments)
        case "agent_fix_issue":
            result = client.agent_fix_issue(**tool.function.arguments)
        case "get_repo_info":
            result = client.get_repo_info(**tool.function.arguments)
        case "agent_comment_issue":
            result = client.agent_comment_issue(**tool.function.arguments)
        case "get_repo_file_content":
            result = client.get_repo_file_content(**tool.function.arguments)

    if result == "":
        return f'Error: Unknow function name {tool.function.name}'

    return result
