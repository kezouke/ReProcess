import uuid
from reprocess.utils.import_path_extractor import get_import_statement_path
from reprocess.utils.mappers.mapper import Mapper
from typing import Dict, List


class IdComponentMapper(Mapper):
    """
    Maps component identifiers to their corresponding file paths and names, and vice versa.

    This class generates unique IDs for each component found within a given map of file components,
    allowing for easy referencing and tracking of these components across different parts of a system.

    Attributes:
        id_component_map (Dict): Maps unique IDs to tuples of (file path, component name).
        component_id_map (Dict): Maps component identifiers to unique IDs.
    """

    def __init__(self, repos_dir: str, file_components_map: Dict[str,
                                                                 List[str]]):
        """
        Initializes a new instance of the IdComponentMapper class.

        Args:
            repos_dir (str): The base directory of the repository.
            file_components_map (Dict[str, List[str]]): A dictionary mapping file paths to lists of component names found within those files.
        """
        super().__init__(repos_dir)
        self.id_component_map = {}
        self.component_id_map = {}
        self.generate_mapping(file_components_map)

    def generate_mapping(self, file_components_map: Dict[str, List[str]]):
        """
        Generates mappings between file paths, component names, and unique IDs.

        This method populates the id_component_map and component_id_map dictionaries based on the provided
        file_components_map.

        Args:
            file_components_map (Dict[str, List[str]]): A dictionary mapping file paths to lists of component names found within those files.
        """
        base_path = self.repos_dir

        for path, components in file_components_map.items():
            for component_name in components:
                # Generate a unique ID for each component
                id = str(uuid.uuid4())
                self.id_component_map[id] = (path, component_name)

                # Determine the package structure of the import statement for the current path
                packages = get_import_statement_path(path.split(base_path)[-1])

                # Construct the component identifier using the package structure and component name
                key = f"{packages}.{component_name}".replace("-", "_")
                self.component_id_map[key] = id

    def get_mapping(self) -> Dict:
        """
        Returns the generated mapping.

        Returns:
            Dict: The generated mapping dictionary containing id_component_map and component_id_map.
        """
        return {
            'id_component_map': self.id_component_map,
            'component_id_map': self.component_id_map
        }


# Custom exception class for handling errors related to missing id_component_map
class IdComponentMapError(Exception):
    """
    Custom exception class raised when attempting to access the id_component_map attribute of an instance of IdComponentMapper
    when it has not been properly initialized or is otherwise unavailable.
    """

    def __init__(self, message="id_component_map is None"):
        self.message = message
        super().__init__(self.message)
