import os
from typing import List


def find_code_files(directory: str) -> List[str]:
    """
    Recursively finds and returns a list of all Python (.py), C (.c), C++ (.cpp),
    and Java (.java) files within a given directory and its subdirectories.

    Args:
        directory (str): The root directory to start searching from.

    Returns:
        List[str]: A list of absolute paths to all code files found within the directory and its subdirectories.
    """
    # Define the set of file extensions we're interested in
    code_extensions = {".py", ".c", ".cpp", ".java", ".go", ".js", ".ts"}
    code_files = []

    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory):
        # Filter and add files with the desired extensions
        code_files.extend(
            os.path.join(root, file) for file in files
            if os.path.splitext(file)[1] in code_extensions)

    return code_files
