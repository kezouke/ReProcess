import os
import json
from code_dependency_grapher.cdg.FileAnalyzer import FileAnalyzer
from code_dependency_grapher.cdg.CodeComponent import CodeComponent
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class JsonDeconverter(RepositoryProcessor):
    """
    A class that processes a JSON file representing a repository's state and reconstructs the repository's structure.
    
    This class inherits from RepositoryProcessor and overrides the `process` method to load a repository's state from a JSON file and populate a `RepositoryContainer` instance accordingly.
    It also handles the reconstruction of complex objects like `FileAnalyzer` and `CodeComponent` instances based on the JSON data.
    """

    def __init__(self, class_map: dict = {}):
        """
        Initializes the JsonDeconverter with a mapping of class names to classes.
        
        This mapping is used during the conversion of dictionaries back to class instances.
        
        :param class_map: A dictionary mapping class names to their corresponding classes.
        """
        self.class_map = class_map

    def __call__(self, repository_container: RepositoryContainer):
        """
        Processes the given repository container by loading its state from a JSON file and populating the container.
        
        :param repository_container: An instance of RepositoryContainer to be populated with data from the JSON file.
        """

        def dict_to_class(d, class_map):
            """
            Recursively converts a dictionary to a class instance using the provided class map.
            
            This function assumes that dictionaries may contain a special key '__class__' indicating the class name of the object they represent.
            
            :param d: The dictionary to convert.
            :param class_map: A mapping of class names to their corresponding classes.
            :return: A class instance reconstructed from the dictionary.
            """
            if isinstance(d, dict):
                if '__class__' in d:
                    class_name = d.pop('__class__')
                    if class_name in class_map:
                        cls = class_map[class_name]
                        instance = cls.__new__(
                            cls
                        )  # Create a new instance without calling __init__
                        for key, value in d.items():
                            setattr(instance, key,
                                    dict_to_class(value, class_map))
                        return instance
                return {
                    key: dict_to_class(value, class_map)
                    for key, value in d.items()
                }
            elif isinstance(d, list):
                return [dict_to_class(element, class_map) for element in d]
            else:
                return d

        # Define the path to the JSON file
        self.json_path = os.path.join(repository_container.db_path,
                                      repository_container.repo_name,
                                      'data.json')

        # Load the JSON data
        with open(self.json_path, 'r') as file:
            json_dict = json.load(file)

        # Populate the repository container with loaded data
        repository_container.repo_author = json_dict["author"]
        repository_container.repo_hash = json_dict["commit hash"]

        # Process files
        for file in json_dict["files"]:
            repository_container.files.append(
                FileAnalyzer(
                    file["file_id"],
                    f"{repository_container.repo_path}/{file['file_path']}",
                    repository_container.repo_path,
                    imports=file["imports"],
                    called_components=file['called_components'],
                    callable_components=file['callable_components'],
                    deparse=True))

        # Process components
        for component in json_dict["components"]:
            repository_container.code_components.append(
                CodeComponent(
                    component["component_id"],
                    repository_container.repo_path,
                    component_name=component["component_name"],
                    component_code=component["component_code"],
                    linked_component_ids=component["linked_component_ids"],
                    file_analyzer_id=component["file_id"],
                    external_component_ids=component["external_component_ids"])
            )

        # Process external components
        tmp_external_components = json_dict["external_components"][0]
        repository_container.external_components = {
            v: k
            for k, v in tmp_external_components.items()
        }

        # Handle predefined attributes
        predefined_attributes = [
            "external_components", "code_components", "files", "repo_author",
            "repo_hash", "repo_name", "repo_path", "db_path", "author",
            "commit_hash", "components"
        ]

        # Extract and convert external attributes not defined in predefined_attributes
        external_attributes = {}
        for key in json_dict:
            if key not in predefined_attributes:
                external_attributes[key] = json_dict[key]

        # Convert external attributes back to class instances
        external_attributes = dict_to_class(external_attributes,
                                            self.class_map)

        # Populate the repository container with converted external attributes
        for key in external_attributes:
            setattr(repository_container, key, external_attributes[key])
