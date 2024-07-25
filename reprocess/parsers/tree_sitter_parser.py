from abc import ABC, abstractmethod
import uuid


class TreeSitterFileParser(ABC):

    def __init__(self, file_path: str, repo_name: str) -> None:
        self.file_path = file_path
        self.repo_name = repo_name

    @abstractmethod
    def extract_component_names(self):
        raise NotImplementedError()

    @abstractmethod
    def extract_imports(self):
        raise NotImplementedError()

    @abstractmethod
    def extract_called_components(self):
        raise NotImplementedError()

    @abstractmethod
    def extract_callable_components(self):
        raise NotImplementedError()


class TreeSitterComponentFillerHelper(ABC):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        self.component_name = component_name
        self.component_file_path = component_file_path
        self.file_parser = file_parser
        self.component_id = str(uuid.uuid4())
        self.file_id = self.file_parser.file_id

    @abstractmethod
    def extract_component_code(self):
        raise NotImplementedError()

    @abstractmethod
    def extract_callable_objects(self):
        raise NotImplementedError()
