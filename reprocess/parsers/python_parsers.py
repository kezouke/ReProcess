from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
import ast
from reprocess.utils.import_path_extractor import get_import_statement_path


class PythonFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                # Parse the file content into an AST
                tree = ast.parse(file.read())
                self.tree = tree
        except Exception as e:
            print(f"Failed to parse {self.file_path}: {e}")

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
        return components

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
