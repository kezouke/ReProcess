import json
import re
import os
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class RegExpFinder(RepositoryProcessor):

    def __init__(self, regExpStr: str):
        self.regExpStr = regExpStr

    def process(self, repository_container: RepositoryContainer):

        try:
            path_to_repo = os.path.join(repository_container.db_path,
                                        repository_container.repo_name,
                                        "data.json")
            re.compile(self.regExpStr)
            with open(path_to_repo, "r") as file:
                json_data = json.load(file)

            components = json_data.get("components", [])

            for component in components:
                component_name = component.get("component_name", "")
                match = re.search(self.regExpStr, component_name)
                if match:
                    print(
                        f"Found match '{match.group()}' in component: {component_name}"
                    )
                    return component
            print("No match found in any component.")
            return None

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {path_to_repo}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

        except KeyError as e:
            print(f"Key error: {e}")
            return None

        except re.error:
            print("Given string is not valid regExp")
            return None
