from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser, Node
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_go as tsgo


class GoFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        """Initializes the Tree-sitter parser with the C language grammar."""
        # Load the compiled language grammar for C
        GO_LANGUAGE = Language(tsgo.language())
        self.parser = Parser(GO_LANGUAGE)

        # Read the file content and parse it
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        # Adjust the file path relative to the repository
        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.packages = get_import_statement_path(cutted_path)
        self.file_path = cutted_path[1:]

    def _rec_component_name_extractor(self,
                                      node: Node,
                                      current_struct: str = "") -> list:
        component_names = []

        # Traverse the AST
        for child in node.children:
            # Check for a struct type declaration
            if child.type == 'type_declaration':
                type_spec = child.child_by_field_name('name')
                if type_spec and type_spec.type == 'type_identifier':
                    struct_name = type_spec.text.decode('utf-8')
                    component_names.append(struct_name)
                    # Recurse to find methods associated with this struct
                    component_names.extend(
                        self._rec_component_name_extractor(
                            child, current_struct=struct_name))

            # Check for a method declaration
            elif child.type == 'method_declaration':
                method_name_node = child.child_by_field_name('name')
                receiver_node = child.child_by_field_name('receiver')
                if method_name_node and receiver_node:
                    # The receiver type is the struct name
                    receiver_type_node = receiver_node.named_child(
                        0).child_by_field_name('type')
                    if receiver_type_node:
                        struct_name = receiver_type_node.text.decode('utf-8')
                        method_name = method_name_node.text.decode('utf-8')
                        full_method_name = f"{struct_name}.{method_name}"
                        component_names.append(full_method_name)

            # Check for a function declaration
            elif child.type == 'function_declaration':
                function_name_node = child.child_by_field_name('name')
                if function_name_node:
                    function_name = function_name_node.text.decode('utf-8')
                    component_names.append(function_name)

            # Recurse to handle nested structures
            component_names.extend(
                self._rec_component_name_extractor(child, current_struct))

        return component_names

    def extract_component_names(self):
        component_names = self._rec_component_name_extractor(
            self.tree.root_node)

        modules = [
            f"{self.packages}.{component}".replace("-", "_")
            for component in component_names
        ]

        return modules

    def extract_callable_components(self):
        return super().extract_callable_components()

    def extract_called_components(self):
        return super().extract_called_components()

    def extract_imports(self):
        return super().extract_imports()
