import ast
from typing import List

class FilePathAstMapper:

    def __init__(self, python_files: List[str]):
        self.file_path_ast_map = {}

        for file_path in python_files:
            with open(file_path, 'r', encoding='utf-8') as file:
                tree = ast.parse(file.read())
            self.file_path_ast_map[file_path] = tree


class FilePathAstMapError(Exception):
    """Custom exception raised when file_path_ast_map is None."""
    pass