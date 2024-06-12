import os
import json
from typing import Optional

from code_dependency_grapher.cdg.requests_handling.RequestManager import RequestManager
from code_dependency_grapher.utils.find_root_directory import find_project_root

class Engine:
    """
    Manages the core functionality of the dependency graph engine, including loading/saving paths,
    initializing the request manager, and handling requests.
    
    This class abstracts away the details of managing project-specific configurations and
    interactions with external resources, providing a streamlined interface for performing actions
    such as requesting data from repositories.
    """
    
    def __init__(self, absolute_path: Optional[str] = None):
        """
        Initializes a new instance of the Engine class.
        
        Args:
            absolute_path (Optional[str], optional): An absolute path to the project directory. Defaults to None.
        """
        # Find the root directory of the project
        self.project_root = find_project_root(os.path.abspath(__file__))
        
        # Define the directory for storing data files
        self.data_dir = os.path.join(self.project_root, 'code_dependency_grapher', 'data')
        
        # Path to the file where the project's absolute path will be saved
        self.path_file = os.path.join(self.data_dir, 'path.json')
        
        # Initialize the absolute path either from a provided argument or by loading it from a file
        if absolute_path is not None:
            self.absolute_path = absolute_path
            self.save_path()  # Save the provided path to the file
        else:
            self.load_path()  # Load the path from the file if none was provided
        
        # Initialize the request manager with the loaded or provided absolute path
        self.request_manager = RequestManager(self.absolute_path)

    def save_path(self):
        """
        Saves the absolute path of the project to a JSON file.
        
        This method ensures that the path is persisted across sessions, allowing the engine to
        locate the project directory even after restarts or changes in environment variables.
        """
        # Ensure the data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Write the absolute path to the JSON file
        with open(self.path_file, 'w') as f:
            json.dump({"path": self.absolute_path}, f)

    def load_path(self):
        """
        Loads the absolute path of the project from a JSON file.
        
        This method attempts to retrieve the previously saved path, failing gracefully if the
        file does not exist or if no path is found within the file.
        """
        # Check if the path file exists
        if not os.path.exists(self.path_file):
            raise FileNotFoundError("Path file does not exist. Pass it to the class constructor")
        
        # Read the path from the JSON file
        with open(self.path_file, 'r') as f:
            data = json.load(f)
            self.absolute_path = data.get('path', None)
            
            # Raise an error if no path was found
            if self.absolute_path is None:
                raise ValueError("No path found in the path file.")

    def request(self, repo_url: str):
        """
        Initiates a request to fetch data from the specified repository URL.
        
        This method delegates the actual request handling to the RequestManager instance,
        passing along the repository URL for processing.
        """
        self.request_manager.manage_request(repo_url)

# Example usage
db_url = "/home/db"
engine = Engine(db_url)
engine.request("https://github.com/vllm-project/SQLite_PyQt")
engine.request("https://github.com/vllm-project/vllm")
engine.request("https://github.com/IU-Capstone-Project-2024/SayNoMore")

