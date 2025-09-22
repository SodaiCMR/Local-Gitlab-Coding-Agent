import os.path

def write_file(working_directory, file_path, content):
    """
    Overwrites an existing file or writes to a new file if it doesn't exist (and create required parent dirs safely),
    constrained to the current working directory

    Args:
        working_directory (str): The based directory in which to search.
        file_path (str): The path of the file in which we should write
        content (str): The content to be written in the file
    Returns:
        The error or the message confirming that the content has been successfully written
    """
    abs_work_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(str(os.path.join(working_directory, file_path)))

    if not abs_file_path.startswith(abs_work_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_file_path):
        dir_name = os.path.dirname(abs_file_path)
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        except Exception as e:
            return f'Error while creating dir {abs_file_path} : {e}'

    try:
        with open(abs_file_path, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Exception writing file : {e}"
