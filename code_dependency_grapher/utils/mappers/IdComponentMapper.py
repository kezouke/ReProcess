import uuid
from ..import_path_extractor import get_import_statement_path

class IdComponentMapper:
    def __init__(self, file_components_map):
        self.id_component_map = {}
        self.component_id_map = {}
        self.generate_mapping(file_components_map)

    def generate_mapping(self, file_components_map):
        for path, components in file_components_map.items():
            for component_name in components:
                id = str(uuid.uuid4())
                value = (path, component_name)
                self.id_component_map[id] = value
                
                packages = get_import_statement_path(path)
                key = f"{packages}.{component_name}"
                self.component_id_map[key] = id


class IdComponentMapError(Exception):
    """Custom exception raised when id_component_map is None."""
    pass
