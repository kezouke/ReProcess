from abc import ABC, abstractmethod
import uuid


class TreeSitterFileParser(ABC):
    """
    Abstract base class for parsing files using Tree-sitter.
    
    Attributes:
        file_path (str): Path to the file being parsed.
        repo_name (str): Name of the repository containing the file.
        file_id (str): Unique identifier for the file.
    """

    def __init__(self, file_path: str, repo_name: str) -> None:
        """Initializes the parser with the file path and repository name."""
        self.file_path = file_path
        self.repo_name = repo_name
        self.file_id = str(uuid.uuid4())
        self._initialize_parser()

        node = self.tree.root_node
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        lines = self.source_code.splitlines()
        code_lines = lines[start_line:end_line + 1]
        self.code_formatted = "\n".join(code_lines)

    @abstractmethod
    def _initialize_parser(self):
        """Initialize the parser with language-specific details."""
        raise NotImplementedError()

    @abstractmethod
    def extract_component_names(self):
        """Extracts names of components defined in the file."""
        raise NotImplementedError()

    @abstractmethod
    def extract_imports(self):
        """Extracts import statements from the file."""
        raise NotImplementedError()

    @abstractmethod
    def extract_called_components(self):
        """Extracts names of components called within the file."""
        raise NotImplementedError()

    @abstractmethod
    def extract_callable_components(self):
        """Extracts names of callable components defined in the file."""
        raise NotImplementedError()


class TreeSitterComponentFillerHelper(ABC):
    """
    Abstract base class for filling component details using Tree-sitter.
    
    Attributes:
        component_name (str): Name of the component being filled.
        component_file_path (str): Path to the file containing the component.
        file_parser (TreeSitterFileParser): Parser instance for the file.
        component_id (str): Unique identifier for the component.
        file_id (str): Unique identifier for the file containing the component.
        component_type (str): Type of the component (e.g., function, structure).
        source_code (str): Source code of the component file.
        component_code (str): Extracted code of the component.
    """

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        """Initializes the helper with component details."""
        self.component_name = component_name
        self.component_file_path = component_file_path
        self.file_parser = file_parser
        self.component_id = str(uuid.uuid4())
        self.file_id = self.file_parser.file_id
        self.component_type = None
        self.source_code = None
        self.component_code = self._initialize_component()

    def _initialize_component(self):
        """Initialize component-specific data and return the extracted code."""
        self.source_code = self._read_source_code()
        return self.extract_component_code()

    def _read_source_code(self):
        """Reads the source code of the component file."""
        try:
            with open(self.component_file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Failed to read {self.component_file_path}: {e}")
            return ""

    @abstractmethod
    def extract_component_code(self):
        """Extracts the code of the component."""
        raise NotImplementedError()

    @abstractmethod
    def extract_callable_objects(self):
        """Extracts callable objects defined within the component."""
        raise NotImplementedError()

    @abstractmethod
    def extract_signature(self):
        """Extracts signature of the component."""
        raise NotImplementedError()
