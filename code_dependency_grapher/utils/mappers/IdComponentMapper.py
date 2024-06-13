import uuid
import hashlib
from code_dependency_grapher.utils.import_path_extractor import get_import_statement_path


class IdComponentMapper:
    """
    Maps component identifiers to their corresponding file paths and names, and vice versa.
    
    This class generates unique IDs for each component found within a given map of file components,
    allowing for easy referencing and tracking of these components across different parts of a system.
    """

    def __init__(self, repos_dir, file_components_map):
        """
        Initializes a new instance of the IdComponentMapper class.
        
        Args:
            file_components_map (dict): A dictionary mapping file paths to lists of component names found within those files.
        """
        self.id_component_map = {
        }  # Stores mappings of unique IDs to tuples of (path, component_name)
        self.component_id_map = {
        }  # Stores mappings of component identifiers to unique IDs
        self.repos_dir = repos_dir

        # Generate initial mappings using the provided file components map
        self.generate_mapping(file_components_map)

    def generate_mapping(self, file_components_map):
        """
        Populates the internal maps with unique IDs for each component and their reverse lookup.
        
        Args:
            file_components_map (dict): A dictionary mapping file paths to lists of component names found within those files.
        """
        base_path = self.repos_dir

        for path, components in file_components_map.items():
            for component_name in components:
                # Generate a unique ID for each component
                id = str(uuid.uuid4())

                # Store the mapping of the unique ID to the tuple of (path, component_name)
                self.id_component_map[id] = (path, component_name)

                # Determine the package structure of the import statement for the current path
                packages = get_import_statement_path(path.split(base_path)[-1])

                # Construct the component identifier using the package structure and component name
                key = f"{packages}.{component_name}".replace("-", "_")

                # Store the reverse mapping of the constructed component identifier to the unique ID
                self.component_id_map[key] = id


# Custom exception class for handling errors related to missing id_component_map
class IdComponentMapError(Exception):
    """
    Custom exception class raised when attempting to access the id_component_map attribute of an instance of IdComponentMapper
    when it has not been properly initialized or is otherwise unavailable.
    """
    pass
