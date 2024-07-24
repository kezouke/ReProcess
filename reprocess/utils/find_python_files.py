import os
from typing import List


def find_code_files(directory: str) -> List[str]:
    """
    Finds and returns a list of all Python (.py) files within a given directory and its subdirectories.
    
    Args:
        directory (str): The root directory to start searching from.
    
    Returns:
        List[str]: A list of absolute paths to all Python files found within the directory and its subdirectories.
    """
    code_files = []
    for root, _, files in os.walk(directory):
        # Iterate through each file in the current directory level
        for file in files:
            # Check if the file has a '.py' extension
            if file.endswith(".py") or file.endswith(".c") or file.endswith(
                    ".cpp"):
                # Construct the full path to the file and add it to the list
                code_files.append(os.path.join(root, file))

    return code_files
