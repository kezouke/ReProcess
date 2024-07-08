import uuid
from reprocess.file_analyzer import FileFiller
from reprocess.utils.mappers.file_path_ast_mapper import FilePathAstMapper
from reprocess.utils.mappers.mapper import Mapper
from typing import List


class IdFileAnalyzerMapper(Mapper):
    """
    Maps file paths to unique identifiers and vice versa using FileAnalyzer instances.

    This class facilitates the creation of a mapping between file paths and unique identifiers (UUIDs),
    allowing for efficient retrieval of file analysis data through these identifiers.

    Attributes:
        id_file_map (Dict): Maps unique identifiers to FileAnalyzer instances.
        path_id_map (Dict): Maps file paths to their corresponding unique identifiers.
    """

    def __init__(self, python_files: List[str], ast_manager: FilePathAstMapper,
                 package_components_names: List[str], repos_dir: str):
        """
        Initializes a new instance of the IdFileAnalyzerMapper class.

        Args:
            python_files (List[str]): List of file paths to analyze.
            ast_manager (FilePathAstMapper): An instance of FilePathAstMapper used to manage the AST mapping.
            package_components_names (List[str]): List of component names.
            repos_dir (str): The base directory of the repository.
        """
        super().__init__(repos_dir)
        self.id_file_map = {}
        self.path_id_map = {}
        self.python_files = python_files
        self.ast_manager = ast_manager
        self.package_components_names = package_components_names
        self.generate_mapping()

    def generate_mapping(self):
        """
        Generates mappings between file paths and unique identifiers using FileAnalyzer instances.

        This method iterates over the provided list of file paths, creates a unique identifier for each,
        initializes a FileAnalyzer instance for each file, and populates both the id_file_map and path_id_map dictionaries.
        """
        for path in self.python_files:
            try:
                id = str(uuid.uuid4()
                         )  # Generate a unique identifier for the current file
                file_analyzer = FileFiller(
                    id, path, self.repos_dir,
                    self.ast_manager.file_path_ast_map,
                    self.package_components_names
                )  # Initialize a FileAnalyzer instance
                self.id_file_map[
                    id] = file_analyzer  # Map the unique identifier to the FileAnalyzer instance
                self.path_id_map[
                    path] = id  # Map the file path to its unique identifier
            except Exception as e:
                print(f"Failed to analyze {path}: {e}")
                continue

    def get_mapping(self) -> dict:
        """
        Returns the generated mapping.

        Returns:
            dict: The generated mapping dictionary containing id_file_map and path_id_map.
        """
        return {
            'id_file_map': self.id_file_map,
            'path_id_map': self.path_id_map
        }


class IdFileAnalyzeMapError(Exception):
    """
    Custom exception raised when attempting to access id_component_map with a None value.
    
    This exception is designed to handle cases where the expected mapping between identifiers and components is missing,
    indicating a potential issue with the initialization or generation of the mapping.
    """

    def __init__(self, message="id_files_manager is None"):
        self.message = message
        super().__init__(self.message)
