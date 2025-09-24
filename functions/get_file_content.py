import os.path
# TODO Test the max_chars limit
MAX_CHARS = 20_000

def get_file_content(_working_directory, file_path):
    """
    Reads the content of the given file as a string, constrained to the working directory
    Args:
        _working_directory (str): (For internal use only, do not set manually).
        file_path (str): The file path to the file from the working directory.
    Returns:
        str: what is inside the given file
    """
    abs_work_dir = os.path.abspath(_working_directory)
    abs_file_path = os.path.abspath(os.path.join(_working_directory, file_path))

    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" does not exist or not found in the current directory.'

    if not abs_file_path.startswith(abs_work_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    file_content_string = ""
    try:
        with open(abs_file_path,"r") as f:
            file_content_string = f.read(MAX_CHARS)
            if len(file_content_string) >= MAX_CHARS:
                file_content_string += f"...file truncated at {MAX_CHARS} CHARS"
        return file_content_string
    except Exception as e:
        return f"Exception reading file : {e}"