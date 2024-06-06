import ast
from typing import List, Optional, Dict, Tuple
from FileAnalyzer import FileAnalyzer
from uuid import UUID

from ..utils.mappers.FilePathAstMapper import FilePathAstMapError
from ..utils.mappers.IdComponentMapper import IdComponentMapError
from ..utils.mappers.


class CodeComponent:


    # def __init__(self, component_id: str):
    #     self.component_id = component_id
    #     self.component_path = id_component_map[component_id][0]
    #     self.file_analyzer = path_file_class_map[self.component_path]
    #     self.extract_code()

    def __init__(self, 
                 component_id: str,
                 id_files_manager: Optional[IdFileAnalyzerMapper] = None,
                 file_path_ast_map: Optional[Dict[str, ast.Module]] = None,
                 id_component_map: Optional[Dict[UUID, Tuple[str, str]]] = None,
                 component_code: Optional[str] = None,
                 linked_component_ids: Optional[List[str]] = None,
                 file_analyzer_id: Optional[str] = None
                 ):
        self.component_id = component_id
        self.id_files_manager = id_files_manager
        self.file_path_ast_map = file_path_ast_map
        self.id_component_map = id_component_map
        self.component_code = component_code
        self.linked_component_ids = linked_component_ids
        self.file_analyzer_id = file_analyzer_id

        if self.file_analyzer_id is None:
            self._get_file_analyzer()        

        # Call extract_code() if file_analyzer is provided and component_code is not set
        if self.component_code is None:
            self.extract_code()

        if self.linked_component_ids is None:
            self.linked_component_ids = []


    def _get_file_analyzer(self):
        if self.id_component_map is None:
            raise IdComponentMapError("id_component_map is None")
        
        if self.id_files_manager is None:
            raise IdFileAnalyzeMapError("id_files_manager is None")
        
        path = self.id_component_map[self.component_id][0]
        self.file_analyzer_id = self.id_files_manager.path_id_map[path]


    def extract_code(self):
        if self.file_path_ast_map is None:
            raise FilePathAstMapError("file_path_ast_map is None")
        
        if self.id_component_map is None:
            raise IdComponentMapError("id_component_map is None")
        
        if self.id_files_manager is None:
            raise IdFileAnalyzeMapError("id_files_manager is None")
        
        file_analyzer = self.id_files_manager.id_file_map[self.file_analyzer_id]

        tree = self.file_path_ast_map[file_analyzer.file_path]
        code = ""
        component_tree = None
        for node in tree.body:
            if (isinstance(node, ast.ClassDef) or 
                isinstance(node, ast.FunctionDef)) and (node.name == self.id_component_map[self.component_id][1]):
                code = ast.unparse(node)
                component_tree = node
                break
        
        file_imports = file_analyzer.imports
        used_imports = set()

        for node in ast.walk(component_tree):
            if isinstance(node, ast.Name):
                if node.id in file_imports:
                    used_imports.add(node.id)


        import_statements_code = ""
        
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports_to_add = [alias for alias in node.names if alias.name in used_imports 
                                  or (alias.asname is not None and alias.asname in used_imports)]
                if imports_to_add:
                    code_line = ast.unparse(ast.Import(names=imports_to_add))
                    import_statements_code = code_line + "\n" + import_statements_code
            elif isinstance(node, ast.ImportFrom):
                imports_to_add = [alias for alias in node.names if alias.name in used_imports 
                                  or (alias.asname is not None and alias.asname in used_imports)]
                if imports_to_add:
                    code_line = ast.unparse(ast.ImportFrom(module=node.module, names=imports_to_add))
                    import_statements_code = code_line + "\n" + import_statements_code
            
        code = import_statements_code + "\n" + code
        self.component_code = code


    def extract_imports(self):
        tree = ast.parse(self.component_code)        
        imports = []

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    imports.append(module_name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    module_name = node.module
                    component_name = alias.name
                    imports.append(f"{module_name}.{component_name}")

        return imports
                