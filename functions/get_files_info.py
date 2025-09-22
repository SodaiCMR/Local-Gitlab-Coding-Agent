import os.path

def get_files_info(working_directory, directory="."):
    """
    Lists files in the specified directory along with their sizes, constrained to the working directory.

    Args:
        working_directory (str):
        directory (str): The directory to list files from, relative to the working directory. If not provided,
         lists files in the working directory itself.
    Returns:
        str: The list of the files in the specified directory along with their sizes, constrained to the working directory.
    """
    abs_working_dir = os.path.abspath(working_directory)
    abs_dir = os.path.abspath(str(os.path.join(working_directory, directory)))
    if not abs_dir.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    final_response = ""
    contents = os.listdir(abs_dir)
    for content in contents:
        content_path = os.path.join(abs_dir, content)
        is_dir = os.path.isdir(content_path)
        file_size = os.path.getsize(content_path)
        final_response += f"- {content}: file_size={file_size} bytes, is_dir={is_dir}\n"
    return final_response

