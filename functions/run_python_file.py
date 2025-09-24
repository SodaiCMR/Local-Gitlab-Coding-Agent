import os
import subprocess

# TODO update the run function to execute more than python files
def run_python_file(_working_directory, file_path, args: list[str]=[]):
    """
    Runs a python file with the python interpreter, accepts additional CLI args as optional list

    Args:
        _working_directory (str): (For internal use only, do not set manually).
        file_path (str): The file to run, relative to the current directory.
        args (list[str]): an optional list of strings to be used as the CLI args for the python file.
    Returns:
        str: The output or the errors after running the file.
    """
    abs_work_dir = os.path.abspath(_working_directory)
    abs_file_path = os.path.abspath(os.path.join(_working_directory, file_path))

    if not abs_file_path.startswith(abs_work_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        final_args = ["python", file_path]
        final_args.extend(args)
        output = subprocess.run(
            final_args,
            cwd=abs_work_dir,
            timeout=30,
            capture_output=True
        )
        final_result = f"""
    STDOUT: {output.stdout}
    STDERR: {output.stderr}
"""
        if output.stdout == "" and output.stderr == "":
            final_result = "No output produced.\n"
        if output.returncode != 0:
            final_result += f'Process exited with code {output.returncode}'
        return final_result
    except Exception as e:
        return f"Error: executing Python file: {e}"