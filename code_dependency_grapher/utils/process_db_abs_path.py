import os
from typing import Optional
import json

from code_dependency_grapher.utils.find_root_directory import find_project_root


def process_abs_db_path(abs_db_path: Optional[str]):
    """
    Processes the absolute database path by either saving it to a file or loading it from a file.
    
    This function acts as a wrapper around two inner functions: `save_path` and `load_path`.
    It determines whether to save or load the path based on the presence of the `abs_db_path` argument.
    
    Args:
        abs_db_path (Optional[str]): The absolute path to save. If None, the function attempts to load the path instead.
        
    Returns:
        Union[str, None]: The loaded absolute path if loading, or None if saving.
    """

    def save_path(abs_db_path: str, data_dir: str,
                  file_with_abs_db_path: str) -> None:
        """
        Saves the absolute path of the project to a JSON file.
        
        Ensures that the path is persisted across sessions, allowing the engine to locate the project
        directory even after restarts or changes in environment variables.
        
        Args:
            abs_db_path (str): The absolute path to save.
            data_dir (str): Directory where the JSON file will be stored.
            file_with_abs_db_path (str): File path including filename where the absolute path will be written.
        """
        # Ensure the data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Write the absolute path to the JSON file
        with open(file_with_abs_db_path, 'w') as f:
            json.dump({"path": abs_db_path}, f)

        return abs_db_path

    def load_path(file_with_abs_db_path: str) -> str:
        """
        Loads the absolute path of the project from a JSON file.
        
        Attempts to retrieve the previously saved path, failing 
        gracefully if the file does not exist or if no path is 
        found within the file.
        
        Args:
            file_with_abs_db_path (str): File path including filename 
                        from which the absolute path will be read.
            
        Returns:
            str: The loaded absolute path.
            
        Raises:
            FileNotFoundError: If the path file does not exist.
            ValueError: If no path is found in the path file.
        """
        # Check if the path file exists
        if not os.path.exists(file_with_abs_db_path):
            raise FileNotFoundError(
                "Path file does not exist. Pass it to the class constructor.")

        # Read the path from the JSON file
        with open(file_with_abs_db_path, 'r') as f:
            data = json.load(f)
            abs_db_path = data.get('path', None)

            # Raise an error if no path was found
            if abs_db_path is None:
                raise ValueError("No path found in the path file.")

        return abs_db_path

    # Find the root folder of the Code Dependency Grapher project
    cdg_root_folder = find_project_root(os.path.abspath(__file__))
    # Define the directory where the path file will be stored
    data_dir = os.path.join(cdg_root_folder, 'code_dependency_grapher', 'data')
    # Define the full path to the path file
    file_with_abs_db_path = os.path.join(data_dir, 'path.json')

    # Determine whether to save or load the path based
    # on the presence of the abs_db_path argument
    if abs_db_path is None:
        return load_path(file_with_abs_db_path)
    else:
        return save_path(abs_db_path, data_dir, file_with_abs_db_path)
