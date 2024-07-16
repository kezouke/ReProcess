import json
from reprocess.code_component import CodeComponentContainer
from reprocess.file_analyzer import FileContainer
from reprocess.re_processors.processor import ReProcessor
from reprocess.re_container import ReContainer


class JsonDeconverter(ReProcessor):
    """
    A class that processes a JSON file representing a repository's state and reconstructs the repository's structure.
    
    This class inherits from RepositoryProcessor and overrides the `process` method to load a repository's state from a JSON file and populate a `RepositoryContainer` instance accordingly.
    It also handles the reconstruction of complex objects like `FileAnalyzer` and `CodeComponent` instances based on the JSON data.
    """

    def __init__(self, class_map: dict = {}, **kwargs):
        """
        Initializes the JsonDeconverter with a mapping of class names to classes.
        
        This mapping is used during the conversion of dictionaries back to class instances.
        
        :param class_map: A dictionary mapping class names to their corresponding classes.
        """
        self.class_map = class_map
        self.class_map["CodeComponentContainer"] = CodeComponentContainer
        self.class_map["FileContainer"] = FileContainer

    def dict_to_class(self, d, class_map):
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
                        cls)  # Create a new instance without calling __init__
                    for key, value in d.items():
                        setattr(instance, key,
                                self.dict_to_class(value, class_map))
                    return instance
            return {
                key: self.dict_to_class(value, class_map)
                for key, value in d.items()
            }
        elif isinstance(d, list):
            return [self.dict_to_class(element, class_map) for element in d]
        else:
            return d

    def __call__(self,
                 repository_container: ReContainer,
                 inplace: bool = True):
        """
        Processes the given repository container by loading its state from a JSON file and populating the container.
        
        :param repository_container: An instance of RepositoryContainer to be populated with data from the JSON file.
        """

        # Define the path to the JSON file
        self.json_path = repository_container.db_path

        # Load the JSON data
        with open(self.json_path, 'r') as file:
            json_dict = json.load(file)

        predefined_attributes = []

        # Extract and convert external attributes not defined in predefined_attributes
        external_attributes = {}
        for key in json_dict:
            if key not in predefined_attributes:
                external_attributes[key] = json_dict[key]

        # Convert external attributes back to class instances
        external_attributes = self.dict_to_class(external_attributes,
                                                 self.class_map)

        # Populate the repository container with converted external attributes
        return external_attributes