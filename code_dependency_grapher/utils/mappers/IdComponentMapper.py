import uuid

class IdComponentMapper:
    def __init__(self, file_components_map):
        self.id_component_map = {}
        self.generate_mapping(file_components_map)

    def generate_mapping(self, file_components_map):
        for path, components in file_components_map.items():
            for component_name in components:
                value = (path, component_name)
                self.id_component_map[str(uuid.uuid4())] = value


class IdComponentMapError(Exception):
    """Custom exception raised when id_component_map is None."""
    pass
