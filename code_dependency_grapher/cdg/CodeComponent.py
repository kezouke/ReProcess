import ast
from typing import List, Optional, Dict, Tuple
from uuid import UUID

from code_dependency_grapher.utils.import_path_extractor import get_import_statement_path
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapError
from code_dependency_grapher.utils.mappers.IdComponentMapper import IdComponentMapError
from code_dependency_grapher.utils.mappers.IdFileAnalyzerMapper import IdFileAnalyzerMapper, IdFileAnalyzeMapError


class CodeComponent:
    """
    Represents a code component - function or class in the python file.
    
    Attributes:
        component_id (str): Unique identifier for the component.
        repos_dir (str): String path to the repository.
        id_files_manager (Optional[IdFileAnalyzerMapper]): Manager for mapping IDs to file analyzers.
        file_path_ast_map (Optional[Dict[str, ast.Module]]): Mapping of file paths to AST modules.
        id_component_map (Optional[Dict[UUID, Tuple[str, str]]]): Mapping of component IDs to file paths and names.
        package_components_names: Optional[List[str]]: List of all component names with its full package path
        component_name (Optional[str]): The name of the component with its relative path in the repo
        component_code (Optional[str]): The extracted code of the component.
        linked_component_ids (Optional[List[str]]): IDs of components that this component is linked to.
        file_analyzer_id (Optional[str]): ID of the file analyzer associated with this component.
        additional_component_ids (Optional[List[str]]): IDs of external components
    """

    def __init__(self, 
                 component_id: str,
                 repos_dir: str,
                 id_files_manager: Optional[IdFileAnalyzerMapper] = None,
                 file_path_ast_map: Optional[Dict[str, ast.Module]] = None,
                 id_component_map: Optional[Dict[UUID, Tuple[str, str]]] = None,
                 package_components_names: Optional[List[str]] = None,
                 component_name: Optional[str] = None,
                 component_code: Optional[str] = None,
                 linked_component_ids: Optional[List[str]] = None,
                 file_analyzer_id: Optional[str] = None,
                 additional_component_ids: Optional[List[str]] = None,
                 ):
        """
        Initializes a new instance of the CodeComponent class.
        
        Args:
            component_id (str): Unique identifier for the component.
            repos_dir (str): String path to the repository.
            id_files_manager (Optional[IdFileAnalyzerMapper]): Manager for mapping IDs to file analyzers.
            file_path_ast_map (Optional[Dict[str, ast.Module]]): Mapping of file paths to AST modules.
            id_component_map (Optional[Dict[UUID, Tuple[str, str]]]): Mapping of component IDs to file paths and names.
            package_components_names: Optional[List[str]]: List of all component names with its full package path
            component_name (Optional[str]): The name of the component with its relative path in the repo
            component_code (Optional[str]): The extracted code of the component.
            linked_component_ids (Optional[List[str]]): IDs of components that this component is linked to.
            file_analyzer_id (Optional[str]): ID of the file analyzer associated with this component.
            additional_component_ids (Optional[List[str]]): IDs of external components
        """
        self.component_id = component_id
        self.repos_dir = repos_dir
        self.id_files_manager = id_files_manager
        self.file_path_ast_map = file_path_ast_map
        self.id_component_map = id_component_map
        self.package_components_names = package_components_names
        self.component_name = component_name
        self.component_code = component_code
        self.linked_component_ids = linked_component_ids
        self.file_analyzer_id = file_analyzer_id
        self.additional_component_ids = additional_component_ids

        if self.file_analyzer_id is None:
            self._get_file_analyzer()        
            if self.component_name is None:
                file_path, cmp_name = self.id_component_map[self.component_id]
                relative_repo_path = "/".join(file_path.split(f'{self.repos_dir}')[1].split("/"))
                self.component_name = get_import_statement_path(relative_repo_path) + f".{cmp_name}"

        self.component_name = self.component_name.replace("-", "_")
        # Extract code if file_analyzer is available and component_code is not set
        if self.component_code is None:
            self.extract_code()

        if self.linked_component_ids is None:
            self.linked_component_ids = []
        if self.additional_component_ids is None:
            self.additional_component_ids = []

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
        self._validate_attributes()

        file_analyzer = self.id_files_manager.id_file_map[self.file_analyzer_id]
        tree = self.file_path_ast_map[file_analyzer.file_path]
        
        component_tree, code = self._extract_component_code(tree)
        used_imports = self._collect_used_imports(component_tree, 
                                                  file_analyzer.imports)

        import_statements_code = self._generate_import_statements(tree,
                                                                  used_imports)

        self.component_code = import_statements_code + "\n" + code

    def _validate_attributes(self):
        if self.file_path_ast_map is None:
            raise FilePathAstMapError("file_path_ast_map is None")
        if self.id_component_map is None:
            raise IdComponentMapError("id_component_map is None")
        if self.id_files_manager is None:
            raise IdFileAnalyzeMapError("id_files_manager is None")

    def _extract_component_code(self, tree):
        for node in tree.body:
            if (isinstance(node, (ast.ClassDef, ast.FunctionDef)) and 
                    node.name == self.id_component_map[self.component_id][1]):
                return node, ast.unparse(node)
        return None, ""

    def _collect_used_imports(self, component_tree, file_imports):
        used_imports = set()
        for node in ast.walk(component_tree):
            if isinstance(node, ast.Name) and node.id in file_imports:
                used_imports.add(node.id)
        return used_imports

    def _generate_import_statements(self, tree, used_imports):
        import_statements_code = ""
        for node in tree.body:
            if isinstance(node, ast.Import):
                import_statements_code = self._handle_import_node(node,
                                                                  used_imports,
                                                                  import_statements_code)
            elif isinstance(node, ast.ImportFrom):
                import_statements_code = self._handle_import_from_node(node,
                                                                       used_imports,
                                                                       import_statements_code)
        return import_statements_code

    def _handle_import_node(self, node, used_imports, import_statements_code):
        imports_to_add = [
            alias for alias in node.names 
            if alias.name in used_imports or (alias.asname is not None and alias.asname in used_imports)
        ]
        if imports_to_add:
            code_line = ast.unparse(ast.Import(names=imports_to_add))
            return code_line + "\n" + import_statements_code
        return import_statements_code

    def _handle_import_from_node(self, node, used_imports, import_statements_code):
        imports_to_add = [
            alias for alias in node.names 
            if alias.name in used_imports or (alias.asname is not None and alias.asname in used_imports) or alias.name == "*"
        ]
        if imports_to_add:
            module = self._resolve_module(node)
            if imports_to_add[0].name == "*":
                imports_to_add = self._expand_wildcard_imports(module, used_imports)

            if imports_to_add:       
                code_line = ast.unparse(ast.ImportFrom(module=module, names=imports_to_add))
                return code_line + "\n" + import_statements_code
        return import_statements_code

    def _resolve_module(self, node):
        if node.level > 0:
            current_package = self.component_name
            splitted_package = current_package.split(".")
            del splitted_package[-node.level-1:]      
            if node.module:
                splitted_package.append(node.module)
            return '.'.join(splitted_package)
        return node.module

    def _expand_wildcard_imports(self, module, used_imports):
        new_imports = []
        for cmp in self.package_components_names:
            if cmp.startswith(module):
                cmp_name = cmp.split(".")[-1]
                if cmp_name in used_imports:
                    new_imports.append(ast.alias(name=cmp_name))
        return new_imports


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
