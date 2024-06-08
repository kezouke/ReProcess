import os
import json
from typing import Optional

class SystemInitializer:
    def __init__(self, absolute_path: Optional[str] = None):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.path_file = os.path.join(self.data_dir, 'path.json')

        # Check if a path was provided, otherwise try to load it from file
        if absolute_path is not None:
            self.absolute_path = absolute_path
            self.save_path()
        else:
            self.load_path()

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


# # Example usage
# db_url = "/home/db"
# si1 = SystemInitializer(db_url)
# print(si1.absolute_path)

# si2 = SystemInitializer()
# print(si2.absolute_path)