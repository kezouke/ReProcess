import json
from code_dependency_grapher.cdg.CodeComponent import CodeComponent
from code_dependency_grapher.cdg.FileAnalyzer import FileAnalyzer
import os

class JsonConverter:

    def convert(db_path, componets, files):
        component_data = []
        for component in componets:
            component_dict = {
                "component_id": component.component_id,
                "component_name": component.component_name,
                "component_code": component.component_code,
                "linked_component_ids": component.linked_component_ids,
                "file_analyzer_id": component.file_analyzer_id
            }
            component_data.append(component_dict)
        files_data = []
        for key in files:
            file_analyzer = files[key]
            files_dict = {
                "file_id": file_analyzer.file_id,
                "file_path": file_analyzer.file_path,
                "imports": file_analyzer.imports,
                "called_components": file_analyzer.called_components,
                "callable_components": file_analyzer.callable_components
            }
            files_data.append(files_dict)
        result_json = {
            "files" : files_data,
            "components": component_data
        }

        directory = os.path.dirname(db_path)

        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(db_path, "w") as file:
            file.write(json.dumps(result_json,indent=4))
        

