from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from reprocess.utils.import_path_extractor import get_import_statement_path
import ast
import uuid


class PythonFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        self.file_path = file_path
        self.repo_name = repo_name
        self.file_id = str(uuid.uuid4())

        cutted_path = self.file_path.split(repo_name)[-1]
        self.packages = get_import_statement_path(cutted_path)

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                # Parse the file content into an AST
                tree = ast.parse(file.read())
                self.tree = tree
        except Exception as e:
            print(f"Failed to parse {self.file_path}: {e}")

        self.file_path = cutted_path[1:]

    def extract_component_names(self):
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
        called_components = set()

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_components.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_components.add(node.func.attr)

        return list(called_components)

    def extract_callable_components(self):
        callable_components = set()

        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                callable_components.add(node.name)
            elif isinstance(node, ast.ClassDef):
                callable_components.add(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                callable_components.add(node.name)

        return list(callable_components)

    def extract_imports(self):
        imports = []

        def handle_import_from(node):
            if node.names[0].name == '*':
                module = get_wildcard_module(node)
                for cmp in self.package_components_names:
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

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)
        try:
            with open(self.component_file_path, 'r', encoding='utf-8') as file:
                self.tree = ast.parse(file.read())
        except Exception as e:
            print(f"Failed to parse {self.component_file_path}: {e}")

        self.component_code = self.extract_component_code()

    def _extract_component_code(self):
        component_name_splitted = self.component_name.split(
            self.file_parser.packages)[-1].split(".")[1:]

        for node in self.tree.body:
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
        file_imports = self.file_parser.extract_imports()
        used_imports = set()
        for node in ast.walk(ast.parse(code)):
            if isinstance(node, ast.Name) and node.id in file_imports:
                used_imports.add(node.id)
        return used_imports

    def _generate_import_statements(self, used_imports):
        import_statements_code = ""
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                import_statements_code = self._handle_import_node(
                    node, used_imports, import_statements_code)
            elif isinstance(node, ast.ImportFrom):
                import_statements_code = self._handle_import_from_node(
                    node, used_imports, import_statements_code)
        return import_statements_code

    def _handle_import_node(self, node, used_imports, import_statements_code):
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
        if node.level > 0:
            current_package = self.component_name
            splitted_package = current_package.split(".")
            del splitted_package[-node.level - 1:]
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

    def extract_component_code(self):
        code = self._extract_component_code()
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
