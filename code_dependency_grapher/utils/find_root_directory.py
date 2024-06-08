import os

def find_project_root(current_path):
    """
    Walks up from the current path until it finds a directory containing.git or README.md,
    assuming that's the project root. Returns None if not found.
    """
    root_marker = ['.git', 'README.md', 'code_dependency_grapher']
    while current_path!= os.path.dirname(current_path):  # Stop when reaching the root directory
        if any(os.path.exists(os.path.join(current_path, marker)) for marker in root_marker):
            return current_path
        current_path = os.path.dirname(current_path)
    return None