import os
import json
from code_dependency_grapher.cdg.FileAnalyzer import FileAnalyzer
from code_dependency_grapher.cdg.CodeComponent import CodeComponent
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class JsonDeconverter:

    def deconvert(self, repository_container: RepositoryContainer):
        self.json_path = os.path.join(repository_container.db_path,
                                      repository_container.repo_name,
                                      'data.json')

        with open(self.json_path, 'r') as file:
            json_dict = json.load(file)
        repository_container.repo_author = json_dict["author"]
        repository_container.repo_hash = json_dict["commit hash"]

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
