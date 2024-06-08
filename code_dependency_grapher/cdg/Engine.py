import os
import json
from typing import Optional

from code_dependency_grapher.cdg.requests_handling.RequestManager import RequestManager
from code_dependency_grapher.utils.find_root_directory import find_project_root

class Engine:
    def __init__(self, absolute_path: Optional[str] = None):
        self.project_root = find_project_root(os.path.abspath(__file__))
        self.path_file = os.path.join(self.project_root,
                                      'code_dependency_grapher', 
                                      'data',
                                      'path.json')
        
        # Check if a path was provided, otherwise try to load it from file
        if absolute_path is not None:
            self.absolute_path = absolute_path
            self.save_path()
        else:
            self.load_path()

        self.request_manager = RequestManager(self.absolute_path)

    def save_path(self):
        """Save the absolute path to a JSON file."""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.path_file, 'w') as f:
            json.dump({"path": self.absolute_path}, f)

    def load_path(self):
        """Load the absolute path from a JSON file."""
        if not os.path.exists(self.path_file):
            raise FileNotFoundError("Path file does not exist. "
                                    "Pass it to the class constructor")
        
        with open(self.path_file, 'r') as f:
            data = json.load(f)
            self.absolute_path = data.get('path', None)
            
            if self.absolute_path is None:
                raise ValueError("No path found in the path file.")
            
    def request(self, repo_url: str):
        self.request_manager.manage_request(repo_url)


# # Example usage
db_url = "/home/db"
engine = Engine(db_url)
engine.request("https://github.com/triton-lang/triton")