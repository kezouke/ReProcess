import os
import json
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class JsonConverter(RepositoryProcessor):

    def __call__(self, repository_container: RepositoryContainer):
        component_data = []
        for component in repository_container.code_components:
            component_dict = {
                "component_id": component.component_id,
                "component_name": component.component_name,
                "component_code": component.component_code,
                "linked_component_ids": component.linked_component_ids,
                "file_id": component.file_analyzer_id,
                "external_component_ids": component.external_component_ids
            }
            component_data.append(component_dict)
        files_data = []
        for file_analyzer in repository_container.files:
            files_dict = {
                "file_id": file_analyzer.file_id,
                "file_path": file_analyzer.file_path,
                "imports": file_analyzer.imports,
                "called_components": file_analyzer.called_components,
                "callable_components": file_analyzer.callable_components
            }
            files_data.append(files_dict)

        result_json = {
            "author":
            repository_container.repo_author,
            "commit hash":
            repository_container.repo_hash,
            "files":
            files_data,
            "components":
            component_data,
            "external_components": [{
                v: k
                for k, v in repository_container.external_components.items()
            }]
        }

        db_path = os.path.join(repository_container.db_path,
                               repository_container.repo_name, "data.json")
        directory = os.path.dirname(db_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        def set_default(obj):
            if isinstance(obj, set):
                return list(obj)
            raise TypeError

        with open(db_path, "w") as file:
            file.write(json.dumps(result_json, indent=4, default=set_default))
            print(f"The graph was successfully built and saved to {db_path}.")
