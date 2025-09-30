from pathlib import Path

def get_files_info(_working_directory, directory="."):
    """
    Lists files in the specified directory along with their sizes, constrained to the working directory.

    Args:
        _working_directory (str): (For internal use only, do not set manually).
        directory (str): The directory to list files from, relative to the working directory. If not provided,
        lists files in the working directory itself.
    Returns:
        str: The list of the files and directories in the specified directory along with their sizes, constrained to the working directory.
    """
    abs_working_dir = Path(_working_directory).resolve()
    abs_dir = abs_working_dir / Path(directory)

    if not abs_dir.is_dir():
        return f'Error: Directory not found or is not a regular directory: "{abs_dir}"'

    if not str(abs_dir).startswith(str(abs_working_dir)):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    final_response = ""
    for entry in abs_dir.rglob("*"):
        if entry.name == "__pycache__" or entry.parent.name == "__pycache__": #TODO check for folders to exclude
            continue
        entry_rel_path = entry.relative_to(abs_working_dir)
        entry_is_dir = entry.is_dir()
        entry_size = entry.stat().st_size
        final_response += f"- {entry_rel_path}: file_size={entry_size} bytes, is_dir={entry_is_dir}\n"
    return final_response