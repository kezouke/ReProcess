import ast
from typing import List, Optional, Dict, Tuple
from uuid import UUID

from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapError
from code_dependency_grapher.utils.mappers.IdComponentMapper import IdComponentMapError
from code_dependency_grapher.utils.mappers.IdFileAnalyzerMapper import IdFileAnalyzerMapper, IdFileAnalyzeMapError


class CodeComponent:
    """
    Represents a code component - function or class in the python file.
    
    Attributes:
        component_id (str): Unique identifier for the component.
        id_files_manager (Optional[IdFileAnalyzerMapper]): Manager for mapping IDs to file analyzers.
        file_path_ast_map (Optional[Dict[str, ast.Module]]): Mapping of file paths to AST modules.
        id_component_map (Optional[Dict[UUID, Tuple[str, str]]]): Mapping of component IDs to file paths and names.
        component_code (Optional[str]): The extracted code of the component.
        linked_component_ids (Optional[List[str]]): IDs of components that this component is linked to.
        file_analyzer_id (Optional[str]): ID of the file analyzer associated with this component.
    """

    def __init__(self, 
                 component_id: str,
                 id_files_manager: Optional[IdFileAnalyzerMapper] = None,
                 file_path_ast_map: Optional[Dict[str, ast.Module]] = None,
                 id_component_map: Optional[Dict[UUID, Tuple[str, str]]] = None,
                 component_code: Optional[str] = None,
                 linked_component_ids: Optional[List[str]] = None,
                 file_analyzer_id: Optional[str] = None
                 ):
        """
        Initializes a new instance of the CodeComponent class.
        
        Args:
            component_id (str): Unique identifier for the component.
            id_files_manager (Optional[IdFileAnalyzerMapper], optional): Manager for mapping IDs to file analyzers. Defaults to None.
            file_path_ast_map (Optional[Dict[str, ast.Module]], optional): Mapping of file paths to AST modules. Defaults to None.
            id_component_map (Optional[Dict[UUID, Tuple[str, str]]], optional): Mapping of component IDs to file paths and names. Defaults to None.
            component_code (Optional[str], optional): The extracted code of the component. Defaults to None.
            linked_component_ids (Optional[List[str]], optional): IDs of components that this component is linked to. Defaults to None.
            file_analyzer_id (Optional[str], optional): ID of the file analyzer associated with this component. Defaults to None.
        """
        self.component_id = component_id
        self.id_files_manager = id_files_manager
        self.file_path_ast_map = file_path_ast_map
        self.id_component_map = id_component_map
        self.component_code = component_code
        self.linked_component_ids = linked_component_ids
        self.file_analyzer_id = file_analyzer_id

        if self.file_analyzer_id is None:
            self._get_file_analyzer()        

        # Extract code if file_analyzer is available and component_code is not set
        if self.component_code is None:
            self.extract_code()

        if self.linked_component_ids is None:
            self.linked_component_ids = []

    def _get_file_analyzer(self):
        """
        Retrieves the file analyzer based on the component's ID and updates the file_analyzer_id attribute.
        
        Raises:
            IdComponentMapError: If id_component_map is None.
            IdFileAnalyzeMapError: If id_files_manager is None.
        """
        if self.id_component_map is None:
            raise IdComponentMapError("id_component_map is None")
        
        if self.id_files_manager is None:
            raise IdFileAnalyzeMapError("id_files_manager is None")
        
        path = self.id_component_map[self.component_id][0]
        self.file_analyzer_id = self.id_files_manager.path_id_map[path]

    def extract_code(self):
        """
        Extracts the code of the component and updates the component_code attribute.
        
        This method also extracts and prepends import statements used by the component.
        
        Raises:
            FilePathAstMapError: If file_path_ast_map is None.
            IdComponentMapError: If id_component_map is None.
            IdFileAnalyzeMapError: If id_files_manager is None.
        """
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
                    code_line = ast.unparse(ast.ImportFrom(module=node.module,
                                                           names=imports_to_add,
                                                           level=node.level))
                    import_statements_code = code_line + "\n" + import_statements_code
            
        code = import_statements_code + "\n" + code
        self.component_code = code

    def extract_imports(self):
        """
        Extracts and returns a list of import statements used by the component.
        
        Returns:
            List[str]: A list of import statements.
        """
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
