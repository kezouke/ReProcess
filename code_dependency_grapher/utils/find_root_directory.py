import os
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
    root_marker = ['.git', 'README.md', 'code_dependency_grapher']  # Common markers indicating a project root
    while current_path!= os.path.dirname(current_path):  # Continue until reaching the root directory
        # Check if any of the root markers exist in the current directory
        if any(os.path.exists(os.path.join(current_path, marker)) for marker in root_marker):
            return current_path  # Return the current path if a marker is found
        current_path = os.path.dirname(current_path)  # Move up to the next directory level
    return None  # Return None if no root marker is found after reaching the root directory
