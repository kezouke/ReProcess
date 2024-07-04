import json
import re
from reprocess.repository_processors.abstract_processor import ReProcessor
from reprocess.repository_processors.repository_container import ReContainer


class RegExpFinder(ReProcessor):

    def __init__(self, regExpStr: str = "*"):
        self.regExpStr = regExpStr

    def __call__(self, repository_container: ReContainer, **kwargs):

        try:
            re.compile(self.regExpStr)

            components = repository_container.code_components

            found_components = []

            for component in components:
                component_name = component.component_name
                match = re.search(self.regExpStr, component_name)
                if match:
                    found_components.append(component)

            return {self.regExpStr: found_components}

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return None

        except KeyError as e:
            print(f"Key error: {e}")
            return None

        except re.error:
            print("Given string is not valid regExp")
            return None
