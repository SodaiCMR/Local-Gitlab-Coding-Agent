def call_function(client, tool, verbose=False):
    if verbose:
        print(f'calling function: {tool.function.name}({tool.function.arguments})')
    else:
        print(f'calling function: {tool.function.name}')

    result = ""
    try:
        match tool.function.name:
            case "agent_fix_issue":
                result = client.agent_fix_issue(**tool.function.arguments)
            case "get_repo_info":
                result = client.get_repo_info(**tool.function.arguments)
            case "agent_comment_issue":
                result = client.agent_comment_issue(**tool.function.arguments)
            case "get_repo_file_content":
                result = client.get_repo_file_content(**tool.function.arguments)
    except Exception as e:
        return f'Error {e} occurred'

    if result == "":
        return f'Error: Unknow function name {tool.function.name}'

    return result