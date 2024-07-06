import uuid
from reprocess.file_analyzer import FileFiller
from reprocess.utils.mappers.file_path_ast_mapper import FilePathAstMapper
from typing import List


class IdFileAnalyzerMapper:
    """
    Maps file paths to unique identifiers and vice versa using FileAnalyzer instances.
    
    This class facilitates the creation of a mapping between file paths and unique identifiers (UUIDs),
    allowing for efficient retrieval of file analysis data through these identifiers.
    
    Attributes:
        id_file_map (Dict[str, FileAnalyzer]): Maps unique identifiers to FileAnalyzer instances.
        path_id_map (Dict[str, str]): Maps file paths to their corresponding unique identifiers.
    """

    def __init__(self, python_files: List[str], ast_manager: FilePathAstMapper,
                 package_components_names: List[str], repos_dir):
        """
        Initializes a new instance of the IdFileAnalyzerMapper class.
        
        Args:
            python_files (List[str]): List of file paths to analyze.
            ast_manager (FilePathAstMapper): An instance of FilePathAstMapper used to manage the AST mapping.
        """
        self.id_file_map = {
        }  # Maps unique identifiers to FileAnalyzer instances.
        self.path_id_map = {
        }  # Maps file paths to their corresponding unique identifiers.
        self.repos_dir = repos_dir
        self.generate_mapping(python_files, ast_manager,
                              package_components_names)

    def generate_mapping(self, python_files, ast_manager,
                         package_components_names):
        """
        Generates mappings between file paths and unique identifiers using FileAnalyzer instances.
        
        This method iterates over the provided list of file paths, creates a unique identifier for each,
        initializes a FileAnalyzer instance for each file, and populates both the id_file_map and path_id_map dictionaries.
        
        Args:
            python_files (List[str]): List of file paths to analyze.
            ast_manager (FilePathAstMapper): An instance of FilePathAstMapper used to manage the AST mapping.
        """
        for path in python_files:
            id = str(uuid.uuid4()
                     )  # Generate a unique identifier for the current file.
            file_analyzer = FileFiller(id, path, self.repos_dir,
                                       ast_manager.file_path_ast_map,
                                       package_components_names
                                       )  # Initialize a FileAnalyzer instance.
            self.id_file_map[
                id] = file_analyzer  # Map the unique identifier to the FileAnalyzer instance.
            self.path_id_map[
                path] = id  # Map the file path to its unique identifier.


class IdFileAnalyzeMapError(Exception):
    """
    Custom exception raised when attempting to access id_component_map with a None value.
    
    This exception is designed to handle cases where the expected mapping between identifiers and components is missing,
    indicating a potential issue with the initialization or generation of the mapping.
    """

    def __init__(self, message="id_files_manager is None"):
        self.message = message
        super().__init__(self.message)
