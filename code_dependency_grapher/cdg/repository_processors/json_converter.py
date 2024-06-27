import os
import json
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class JsonConverter(RepositoryProcessor):
    """
    A class that processes a repository container and converts its data into JSON format.
    
    This class inherits from RepositoryProcessor and overrides the `process` method to convert the repository's components and files into a structured JSON object.
    It also handles saving this JSON object to a file within the repository's database path.
    """

    def __call__(self, repository_container: RepositoryContainer):
        """
        Processes the given repository container and saves its data in JSON format to a file.
        
        :param repository_container: An instance of RepositoryContainer containing the repository's data.
        """

        def class_to_dict(obj):
            """
            Recursively converts a class instance to a dictionary.
            
            This function traverses through the attributes of an object (including nested objects and lists) and converts them into a dictionary representation.
            
            :param obj: The object to convert to a dictionary.
            :return: A dictionary representation of the input object.
            """
            if isinstance(obj, dict):
                return {
                    key: class_to_dict(value)
                    for key, value in obj.items()
                }
            elif isinstance(obj, list):
                return [class_to_dict(element) for element in obj]
            elif hasattr(obj, "__dict__"):
                data = {
                    key: class_to_dict(value)
                    for key, value in obj.__dict__.items()
                }
                data['__class__'] = obj.__class__.__name__
                return data
            else:
                return obj

        # Function to handle serialization of sets to lists
        def set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError(f"{type(obj)}")

        # # Initialize lists to hold component and file data
        # component_data = []
        # files_data = []

        # # Process each component in the repository container
        # for component in repository_container.code_components:
        #     component_dict = {
        #         "component_id": component.component_id,
        #         "component_name": component.component_name,
        #         "component_code": component.component_code,
        #         "linked_component_ids": component.linked_component_ids,
        #         "file_id": component.file_id,
        #         "external_component_ids": component.external_component_ids
        #     }
        #     component_data.append(component_dict)

        # # Process each file analyzer in the repository container
        # for file_analyzer in repository_container.files:
        #     files_dict = {
        #         "file_id": file_analyzer.file_id,
        #         "file_path": file_analyzer.file_path,
        #         "imports": file_analyzer.imports,
        #         "called_components": file_analyzer.called_components,
        #         "callable_components": file_analyzer.callable_components
        #     }
        #     files_data.append(files_dict)

        # # Construct the main JSON structure
        # result_json = {
        #     "author":
        #     repository_container.repo_author,
        #     "commit hash":
        #     repository_container.repo_hash,
        #     "files":
        #     files_data,
        #     "components":
        #     component_data,
        #     "external_components": [{
        #         v: k
        #         for k, v in repository_container.external_components.items()
        #     }]
        # }

        # # Collect additional attributes not explicitly defined in the predefined attributes
        # predefined_attributes = [
        #     "external_components", "code_components", "files", "repo_author",
        #     "repo_hash", "repo_name", "repo_path", "db_path"
        # ]
        predefined_attributes = []
        result_json = {}
        external_attributes_of_repository = {}
        for attribute in repository_container.__dict__:
            if attribute not in predefined_attributes:
                external_attributes_of_repository[
                    attribute] = repository_container.__dict__[attribute]

        # Add these additional attributes to the main JSON structure
        addition_fields_for_json = class_to_dict(
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
            file.write(json.dumps(result_json, indent=4, default=set_default))
            print(f"The graph was successfully built and saved to {db_path}.")
