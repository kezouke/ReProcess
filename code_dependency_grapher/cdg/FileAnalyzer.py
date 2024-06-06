import ast
from typing import List, Optional, Dict
from ..utils.mappers.FilePathAstMapper import FilePathAstMapError

class FileAnalyzer:

    # def __init__(self, file_id, file_path):
    #     self.file_id = file_id
    #     self.file_path = file_path
    #     self.imports = self.extract_imports()
    #     self.called_components = self.extract_called_components()
    #     self.callable_components = self.extract_callable_components()

    def __init__(self, 
                 file_id: str, 
                 file_path: str,
                 file_path_ast_map: Optional[Dict[str, ast.Module]] = None,
                 imports: Optional[List[str]]=None,
                 called_components: Optional[List[str]]=None,
                 callable_components: Optional[List[str]]=None):
        self.file_id = file_id
        self.file_path = file_path
        self.file_path_ast_map = file_path_ast_map
        self.imports = imports or self.extract_imports()
        self.called_components = called_components or self.extract_called_components()
        self.callable_components = callable_components or self.extract_callable_components()


    def extract_imports(self):
        self._validate_ast_map()

        tree = self.file_path_ast_map[self.file_path]

        imports = []

        for node in tree.body:
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname is not None:
                        imports.append(alias.asname)
                    else:
                        imports.append(alias.name)
        return imports

    def extract_called_components(self):
        self._validate_ast_map()
        
        tree = self.file_path_ast_map[self.file_path]

        called_components = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_components.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_components.add(node.func.attr)

        return list(called_components)

    def extract_callable_components(self):
        self._validate_ast_map()
        
        tree = self.file_path_ast_map[self.file_path]

        callable_components = set()

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                callable_components.add(node.name)
            elif isinstance(node, ast.ClassDef):
                callable_components.add(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                callable_components.add(node.name)

        return list(callable_components)
    
    def _validate_ast_map(self):
        if self.file_path_ast_map is None:
            raise FilePathAstMapError("file_path_ast_map is None")

    def __str__(self) -> str:
        return self.file_path
    
    def __hash__(self) -> int:
        return hash(self.file_path)
    