from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from reprocess.utils.import_path_extractor import get_import_statement_path
import ast
import uuid
from typing import List, Tuple


class PythonFileParser(TreeSitterFileParser):
    """
    Parses Python files using the Python standard library's ast module.
    
    This class inherits from TreeSitterFileParser and overrides methods to work specifically with Python files.
    """

    def __init__(self, file_path: str, repo_name: str) -> None:
        self.file_path = file_path
        self.repo_name = repo_name
        self.file_id = str(uuid.uuid4())
        self._initialize_parser()
        self.code_formatted = ast.unparse(self.tree)

    def _initialize_parser(self):
        """
        Initializes the parser by setting up the file path and parsing the source code into an AST.
        
        Adjusts the file path relative to the repository name and parses the source code using ast.parse.
        """
        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.packages = get_import_statement_path(cutted_path)
        self.tree = self._parse_source_code()
        self.file_path = cutted_path[1:]

    def _parse_source_code(self):
        """
        Parses the source code of the Python file into an AST.
        
        Opens the file, reads its content, and uses ast.parse to convert it into an AST. Handles exceptions gracefully.
        
        Returns:
            Optional[ast.AST]: The AST representation of the source code, or None if parsing fails.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return ast.parse(file.read())
        except Exception as e:
            print(f"Failed to parse {self.file_path}: {e}")
            return None

    def extract_component_names(self):
        """
        Extracts names of components (classes, functions) defined in the Python file.
        
        Walks through the AST to find ClassDef and FunctionDef nodes, constructing fully qualified component names.
        
        Returns:
            List[str]: List of fully qualified component names found in the file.
        """
        components = []

        def visit_node(node):
            if isinstance(node, ast.ClassDef):
                components.append(node.name)
                for class_body_node in node.body:
                    if isinstance(class_body_node, ast.FunctionDef):
                        components.append(
                            f"{node.name}.{class_body_node.name}")
            elif isinstance(node, ast.FunctionDef):
                components.append(node.name)

        for node in self.tree.body:
            visit_node(node)

        modules = [
            f"{self.packages}.{component}".replace("-", "_")
            for component in components
        ]

        return modules

    def extract_called_components(self):
        """
        Identifies components called within the Python file.
        
        Uses ast.walk to traverse the AST and identify calls to functions or methods, adding them to a set.
        
        Returns:
            List[str]: List of unique names of components being called.
        """
        called_components = set()

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_components.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_components.add(node.func.attr)

        return list(called_components)

    def extract_callable_components(self):
        """
        Finds callable components (functions, classes, async functions) defined within the Python file.
        
        Returns:
            List[str]: List of names of callable components found in the file.
        """
        return list(
            set([
                node.name for node in self.tree.body
                if isinstance(node, (ast.FunctionDef, ast.ClassDef,
                                     ast.AsyncFunctionDef))
            ]))

    def extract_imports(self):
        """
        Extracts import statements from the Python file.
        
        Handles both regular imports and wildcard imports, constructing a list of imported modules or objects.
        
        Returns:
            List[str]: List of imported modules or objects found in the file.
        """
        imports = []

        def handle_import_from(node):
            if node.names[0].name == '*':
                module = get_wildcard_module(node)
                for cmp in self.extract_component_names():
                    if cmp.startswith(module):
                        imports.append(cmp.split(".")[-1])
            else:
                append_aliases(node)

        def get_wildcard_module(node):
            if node.level > 0:
                current_package = get_import_statement_path(self.file_path)
                splitted_package = current_package.split(".")
                del splitted_package[-node.level:]
                splitted_package.append(node.module)
                return '.'.join(splitted_package)
            return node.module

        def append_aliases(node):
            for alias in node.names:
                imports.append(alias.asname if alias.asname else alias.name)

        for node in self.tree.body:
            if isinstance(node, ast.Import):
                append_aliases(node)
            elif isinstance(node, ast.ImportFrom):
                handle_import_from(node)

        return imports


class PythonComponentFillerHelper(TreeSitterComponentFillerHelper):
    """
    Helper class for extracting Python component code and related imports.
    
    This class inherits from TreeSitterComponentFillerHelper and overrides methods to work specifically with Python files.
    """

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def _extract_code_without_imports(self):
        """
        Extracts the code of the specified Python component.
        
        Searches through the AST for the specified component (function or method within a class) and returns its source code.
        
        Returns:
            str: The extracted source code of the component, or an empty string if not found.
        """
        #Empty separator handling
        if self.component_name.startswith('.'):
            if self.component_name.count('.') == 1:
                component_name_splitted = [
                    self.component_name.replace(".", "", 1)
                ]
            else:
                self.component_name = self.component_name.replace(".", "", 1)
                component_name_splitted = self.component_name.split(".")[1:]
        else:
            component_name_splitted = self.component_name.split(
                f"{self.file_parser.packages}.")[-1].split(".")

        for node in self.file_parser.tree.body:
            if isinstance(node, ast.FunctionDef
                          ) and node.name == component_name_splitted[0]:
                self.component_type = "function"
                return ast.unparse(node)
            elif isinstance(
                    node,
                    ast.ClassDef) and node.name == component_name_splitted[0]:
                if len(component_name_splitted) == 1:
                    self.component_type = "class"
                    return ast.unparse(node)
                else:
                    # If it's a method within a class
                    for class_node in node.body:
                        if isinstance(
                                class_node, ast.FunctionDef
                        ) and class_node.name == component_name_splitted[1]:
                            self.component_type = "method"
                            return ast.unparse(class_node)

        return ""

    def _collect_used_imports(self, code):
        """
        Collects import statements used within the given code snippet.
        
        Parses the code snippet and identifies import statements that are actually used within it.
        
        Args:
            code (str): The source code snippet to analyze.
            
        Returns:
            Set[str]: A set of names of imported modules or objects used in the code.
        """
        file_imports = self.file_parser.extract_imports()
        used_imports = {
            node.id
            for node in ast.walk(ast.parse(code))
            if isinstance(node, ast.Name) and node.id in file_imports
        }
        return used_imports

    def _generate_import_statements(self, used_imports):
        """
        Generates import statements for the imports used within the component code.
        
        Args:
            used_imports (Set[str]): Names of imported modules or objects used in the component code.
            
        Returns:
            str: Concatenated import statements for the used imports.
        """
        import_statements_code = ""
        for node in self.file_parser.tree.body:
            if isinstance(node, ast.Import):
                import_statements_code = self._handle_import_node(
                    node, used_imports, import_statements_code)
            elif isinstance(node, ast.ImportFrom):
                import_statements_code = self._handle_import_from_node(
                    node, used_imports, import_statements_code)
        return import_statements_code

    def _handle_import_node(self, node, used_imports, import_statements_code):
        """
        Handles regular import nodes, adding necessary imports to the import statements code.
        
        Args:
            node (ast.Import): An AST import node.
            used_imports (Set[str]): Names of imported modules or objects used in the component code.
            import_statements_code (str): Accumulated import statements code.
            
        Returns:
            str: Updated import statements code with necessary imports added.
        """
        imports_to_add = [
            alias for alias in node.names if alias.name in used_imports or (
                alias.asname is not None and alias.asname in used_imports)
        ]
        if imports_to_add:
            code_line = ast.unparse(ast.Import(names=imports_to_add))
            return code_line + "\n" + import_statements_code
        return import_statements_code

    def _handle_import_from_node(self, node, used_imports,
                                 import_statements_code):
        """
        Handles import-from nodes, adding necessary imports to the import statements code.
        
        Args:
            node (ast.ImportFrom): An AST import-from node.
            used_imports (Set[str]): Names of imported modules or objects used in the component code.
            import_statements_code (str): Accumulated import statements code.
            
        Returns:
            str: Updated import statements code with necessary imports added.
        """
        imports_to_add = [
            alias for alias in node.names if alias.name in used_imports or (
                alias.asname is not None and alias.asname in used_imports)
            or alias.name == "*"
        ]
        if imports_to_add:
            module = self._resolve_module(node)
            if imports_to_add[0].name == "*":
                imports_to_add = self._expand_wildcard_imports(
                    module, used_imports)

            if imports_to_add:
                code_line = ast.unparse(
                    ast.ImportFrom(module=module, names=imports_to_add))
                return code_line + "\n" + import_statements_code
        return import_statements_code

    def _resolve_module(self, node):
        """
        Resolves the module path for an import-from node based on relative imports level.
        
        Args:
            node (ast.ImportFrom): An AST import-from node.
            
        Returns:
            str: The resolved module path.
        """
        if node.level > 0:
            current_package = self.component_name
            splitted_package = current_package.split(".")
            del splitted_package[-node.level - 1:]
            if node.module:
                splitted_package.append(node.module)

            return '.'.join(splitted_package)
        return node.module

    def _expand_wildcard_imports(self, module, used_imports):
        """
        Expands wildcard imports (*) into explicit imports for modules actually used in the component code.
        
        Args:
            module (str): The module being imported.
            used_imports (Set[str]): Names of imported modules or objects used in the component code.
            
        Returns:
            List[ast.alias]: A list of explicit imports replacing the wildcard import.
        """
        new_imports = []
        for cmp in self.file_parser.extract_component_names():
            if cmp.startswith(module):
                cmp_name = cmp.split(".")[-1]
                if cmp_name in used_imports:
                    new_imports.append(ast.alias(name=cmp_name))
        return new_imports

    def extract_component_code(self):
        """
        Extracts the component code along with necessary import statements.
        
        Returns:
            str: The extracted component code prefixed with necessary import statements.
        """
        code = self._extract_code_without_imports()
        used_imports = self._collect_used_imports(code)
        import_statements_code = self._generate_import_statements(used_imports)
        return import_statements_code + "\n" + code

    def extract_callable_objects(self):
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

        called_components = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_components.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_components.add(node.func.attr)

        called_components = list(called_components)
        resulted_array = []
        for cmp in called_components:
            if cmp in self.file_parser.extract_callable_components():
                resulted_array.append(f"{self.file_parser.packages}.{cmp}")
        resulted_array += imports
        return resulted_array

    def extract_signature(self):
        tree = ast.parse(self.component_code)
        source_lines = self.component_code.splitlines()
        simplified_lines = source_lines[:]

        indices_to_del: List[Tuple[int, int]] = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(
                    node,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start, end = node.lineno - 1, node.end_lineno
                assert isinstance(end, int)
                indices_to_del.append((start + 1, end))

        for start, end in reversed(indices_to_del):
            del simplified_lines[start + 0:end]

        return "\n".join(simplified_lines)
