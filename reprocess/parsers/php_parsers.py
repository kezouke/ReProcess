from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_php as tsphp


class PhpFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        """Initializes the Tree-sitter parser with the PHP language grammar."""
        PHP_LANGUAGE = Language(tsphp.language_php())
        self.parser = Parser(PHP_LANGUAGE)

        # Read the file content and parse it
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        # Adjust the file path relative to the repository
        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.packages = get_import_statement_path(
            cutted_path.replace(".php", ""))
        self.file_path = cutted_path[1:]

    def extract_component_names(self):
        """Extracts the names of all classes, methods, and functions in the PHP file."""
        class_stack = []  # Stack to maintain nested class hierarchy
        component_names = []

        def traverse(node):
            nonlocal class_stack, component_names

            # Check for class declarations
            if node.type == 'class_declaration':
                class_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                if class_stack:
                    full_class_name = f"{class_stack[-1]}.{class_name}"
                else:
                    full_class_name = class_name
                class_stack.append(full_class_name)
                component_names.append(full_class_name)

            # Check for method declarations within a class
            if node.type == 'method_declaration':
                method_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                if class_stack:
                    full_method_name = f"{class_stack[-1]}.{method_name}"
                    component_names.append(full_method_name)

            # Check for standalone functions
            if node.type == 'function_definition':
                function_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                component_names.append(function_name)

            # Recursively visit children of the current node
            for child in node.children:
                traverse(child)

            # Pop class stack when leaving a class scope
            if node.type == 'class_declaration':
                class_stack.pop()

        # Start traversal from the root node of the tree
        root_node = self.tree.root_node
        traverse(root_node)

        # Prepend package path to each component name
        component_names = [f"{self.packages}.{cmp}" for cmp in component_names]

        return component_names

    def extract_callable_components(self):
        pass

    def extract_called_components(self):
        pass

    def extract_imports(self):
        pass


class PhpComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        pass

    def extract_callable_objects(self):
        pass
