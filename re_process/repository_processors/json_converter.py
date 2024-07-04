import os
import json
from re_process.repository_processors.abstract_processor import ReProcessor
from re_process.repository_processors.repository_container import ReContainer


class JsonConverter(ReProcessor):
    """
    A class that processes a repository container and converts its data into JSON format.
    
    This class inherits from RepositoryProcessor and overrides the `process` method to convert the repository's components and files into a structured JSON object.
    It also handles saving this JSON object to a file within the repository's database path.
    """

    def __init__(self, **kwargs):
        pass

    def class_to_dict(self, obj):
        """
            Recursively converts a class instance to a dictionary.
            
            This function traverses through the attributes of an object (including nested objects and lists) and converts them into a dictionary representation.
            
            :param obj: The object to convert to a dictionary.
            :return: A dictionary representation of the input object.
            """
        if isinstance(obj, dict):
            return {
                key: self.class_to_dict(value)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self.class_to_dict(element) for element in obj]
        elif hasattr(obj, "__dict__"):
            data = {
                key: self.class_to_dict(value)
                for key, value in obj.__dict__.items()
            }
            data['__class__'] = obj.__class__.__name__
            return data
        else:
            return obj

    def set_default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        raise TypeError(f"{type(obj)}")

    def __call__(self,
                 repository_container: ReContainer,
                 inplace: bool = True):
        """
        Processes the given repository container and saves its data in JSON format to a file.
        
        :param repository_container: An instance of RepositoryContainer containing the repository's data.
        """

        # Function to handle serialization of sets to lists

        predefined_attributes = []
        result_json = {}
        external_attributes_of_repository = {}
        for attribute in vars(repository_container):
            if attribute not in predefined_attributes:
                external_attributes_of_repository[
                    attribute] = repository_container.__dict__[attribute]

        # Add these additional attributes to the main JSON structure
        addition_fields_for_json = self.class_to_dict(
            external_attributes_of_repository)
        for key in addition_fields_for_json:
            result_json[key] = addition_fields_for_json[key]

        # Define the path where the JSON will be saved
        db_path = os.path.join(repository_container.db_path,
                               repository_container.repo_name, "data.json")
        directory = os.path.dirname(db_path)

        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the JSON structure to a file
        with open(db_path, "w") as file:
            file.write(
                json.dumps(result_json, indent=4, default=self.set_default))
            print(f"The graph was successfully built and saved to {db_path}.")

        return {"is_converted": True}
