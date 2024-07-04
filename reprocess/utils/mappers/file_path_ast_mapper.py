import ast
from typing import List


class FilePathAstMapper:
    """
    Maps Python file paths to their corresponding Abstract Syntax Trees (ASTs).
    
    This class reads Python files and parses them into their AST representations, storing these trees
    in a dictionary keyed by the file path. This allows for easy retrieval and manipulation of the ASTs
    for further analysis or modification of the original Python code.
    """

    def __init__(self, repos_dir, python_files: List[str]):
        """
        Initializes a new instance of the FilePathAstMapper class.
        
        Args:
            python_files (List[str]): A list of file paths to Python files whose ASTs should be parsed and stored.
        """
        self.file_path_ast_map = {
        }  # Dictionary to store mappings of file paths to their ASTs

        # Iterate over each file path in the provided list
        for file_path in python_files:
            try:
                # Open the file in read mode with UTF-8 encoding
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Parse the file content into an AST
                    tree = ast.parse(file.read())

                    # Store the AST in the file_path_ast_map dictionary, keyed by the file path
                    relative_repo_path = "/".join(
                        file_path.split(f'{repos_dir}')[1].split("/")[1:])
                    self.file_path_ast_map[relative_repo_path] = tree
            except Exception as e:
                print(f"Failed to parse {file_path}: {e}")
                continue


class FilePathAstMapError(Exception):
    """
    Custom exception class raised when attempting to access the file_path_ast_map attribute of an instance of FilePathAstMapper
    when it has not been properly initialized or is otherwise unavailable.
    """
    pass
