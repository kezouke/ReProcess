import os
import subprocess
from typing import Union


def find_project_root(current_path: str) -> Union[str, None]:
    """
    Finds the root directory of a project using the `git rev-parse --show-toplevel` command.
    
    This function changes the current working directory to the specified `current_path`. It then attempts to execute the git command to determine the root directory of the project. If successful, it returns the path to the project root. If the command fails due to the absence of a.git directory or other errors, it handles exceptions accordingly and returns `None`.

    Args:
        current_path (str): The initial path from where the search for the project root begins.

    Returns:
        Union[str, None]: The absolute path to the project root if found, otherwise `None`.
    """
    try:
        # Adjust the current_path if it points to a file within the project
        if os.path.isfile(current_path):
            current_path = os.path.dirname(current_path)

        # Switch to the target directory
        os.chdir(current_path)

        # Execute the git command to locate the project root
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                check=True)
        # Extract and return the project root path from the command output
        git_root = result.stdout.strip()
        return git_root
    except subprocess.CalledProcessError as e:
        print(f"Error finding Git root: {e.stderr}")
        return None
    except FileNotFoundError as e:
        print(f"Invalid directory: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
