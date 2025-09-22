from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

def main():
    working_directory = "calculator"
    run_test =  run_python_file("calculator", "main.py", ["4 * 5"])
    print(run_test)

    # write_test = write_file("calculator", "/tmp/temp.txt", "this should not be allowed")
    # print(write_test)

    # main_content = get_file_content(working_directory, "/bin/cat")
    # print(main_content)

    # pkg_contents = get_files_info(working_directory, "pkg")
    # print(pkg_contents)

main()