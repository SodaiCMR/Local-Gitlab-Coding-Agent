import os.path
# TODO Test the max_chars limit
MAX_CHARS = 20_000

def get_file_content(working_directory, file_path):
    """

    :param working_directory:
    :param file_path:
    :return:
    """
    abs_work_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(str(os.path.join(working_directory, file_path)))

    if not abs_file_path.startswith(abs_work_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    file_content_string = ""
    try:
        with open(abs_file_path,"r") as f:
            file_content_string = f.read(MAX_CHARS)
            if len(file_content_string) >= MAX_CHARS:
                file_content_string += f"...file truncated at {MAX_CHARS} CHARS"
        return file_content_string
    except Exception as e:
        return f"Exception reading file : {e}"