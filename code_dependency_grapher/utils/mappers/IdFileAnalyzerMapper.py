import uuid
from ...cdg.FileAnalyzer import FileAnalyzer
from FilePathAstMapper import FilePathAstMapper
from typing import List

class IdFileAnalyzerMapper:
    def __init__(self, 
                 python_files: List[str],
                 ast_manager: FilePathAstMapper):
        self.id_file_map = {}
        self.path_id_map = {}
        self.generate_mapping(python_files, ast_manager)
    
    def generate_mapping(self, python_files, ast_manager):
        for path in python_files:
            id = str(uuid.uuid4())
            file_analyzer = FileAnalyzer(id, path, ast_manager.file_path_ast_map)
            self.id_file_map[id] = file_analyzer
            self.path_id_map[path] = id



class IdFileAnalyzeMapError(Exception):
    """Custom exception raised when id_component_map is None."""
    pass
