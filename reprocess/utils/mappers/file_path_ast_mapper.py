import ast
from typing import List, Dict
from reprocess.utils.mappers.mapper import Mapper


class FilePathAstMapper(Mapper):
    """
    Maps Python file paths to their corresponding Abstract Syntax Trees (ASTs).

    This class reads Python files and parses them into their AST representations, storing these trees
    in a dictionary keyed by the file path. This allows for easy retrieval and manipulation of the ASTs
    for further analysis or modification of the original Python code.

    Attributes:
        file_path_ast_map (Dict): Maps file paths to their AST representations.
    """

    def __init__(self, repos_dir: str, python_files: List[str]):
        """
        Initializes a new instance of the FilePathAstMapper class.

        Args:
            repos_dir (str): The base directory of the repository.
            python_files (List[str]): A list of file paths to Python files whose ASTs should be parsed and stored.
        """
        super().__init__(repos_dir)
        self.file_path_ast_map = {}
        self.generate_mapping(python_files)

    def generate_mapping(self, python_files: List[str]):
        """
        Generates mappings between file paths and their AST representations.

        This method reads each Python file from the provided list, parses it into an AST,
        and stores the AST in the file_path_ast_map dictionary.

        Args:
            python_files (List[str]): A list of file paths to Python files whose ASTs should be parsed and stored.
        """
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Parse the file content into an AST
                    tree = ast.parse(file.read())

                    # Store the AST in the file_path_ast_map dictionary, keyed by the file path
                    relative_repo_path = "/".join(
                        file_path.split(f'{self.repos_dir}')[1].split("/")[1:])
                    self.file_path_ast_map[relative_repo_path] = tree
            except Exception as e:
                print(f"Failed to parse {file_path}: {e}")
                continue

    def get_mapping(self) -> Dict:
        """
        Returns the generated mapping.

        Returns:
            dict: The generated mapping dictionary containing file_path_ast_map.
        """
        return {'file_path_ast_map': self.file_path_ast_map}


class FilePathAstMapError(Exception):
    """
    Custom exception class raised when attempting to access the file_path_ast_map attribute of an instance of FilePathAstMapper
    when it has not been properly initialized or is otherwise unavailable.
    """

    def __init__(self, message="file_path_ast_map is None"):
        self.message = message
        super().__init__(self.message)
