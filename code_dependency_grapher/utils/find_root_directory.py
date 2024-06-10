import os
import subprocess
from typing import Union

def find_project_root(current_path: str) -> Union[str, None]:
    """
    Attempts to find the root directory of a project by looking for common markers like `.git`, `README.md`, or a specific directory name (`code_dependency_grapher`). 
    
    This function walks up from the given `current_path` towards the root directory, checking each parent directory for the presence of one of these markers. Once a match is found, it assumes this location is the project root and returns the path. If no matching marker is found after reaching the root directory, it returns `None`.
    
    Args:
        current_path (str): The starting path from which to begin the search upwards towards the root directory.
    
    Returns:
        Union[str, None]: The path to the project root if found, otherwise `None`.
    """
    try:
        # Change the current working directory to the specified repo_path
        if os.path.isfile(current_path):
            current_path = os.path.dirname(current_path)
       
        os.chdir(current_path)

        # Run the git command to find the root directory
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        # The stdout contains the path to the root directory
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