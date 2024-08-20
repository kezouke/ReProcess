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

    def _rec_extract_called_nodes(self, node: Node, var_types: dict) -> set:
        called_components = set()

        # Traverse the AST
        for child in node.children:
            if child.type == 'call_expression':
                # Extract the function being called
                function_node = child.child_by_field_name('function')
                if function_node:
                    # Check if it's a selector_expression (e.g., obj.Method())
                    if function_node.type == 'selector_expression':
                        operand_node = function_node.child_by_field_name(
                            'operand')
                        field_node = function_node.child_by_field_name('field')
                        if operand_node and field_node:
                            operand_name = operand_node.text.decode('utf-8')
                            field_name = field_node.text.decode('utf-8')
                            # Determine the full method name based on variable types
                            if operand_name in var_types:
                                struct_name = var_types[operand_name]
                                full_method_name = f"{struct_name}.{field_name}"
                                called_components.add(full_method_name)
                    else:
                        # For non-selector expressions, treat it as a function call
                        function_name = function_node.text.decode('utf-8')
                        called_components.add(function_name)

            elif child.type == 'short_var_declaration':
                left_node = child.child_by_field_name('left')
                right_node = child.child_by_field_name('right')
                if left_node and right_node:
                    # Map variable names to their types
                    var_names = [
                        var.text.decode('utf-8') for var in left_node.children
                    ]
                    # Check if right_node contains a composite_literal to get types
                    if right_node.type == 'expression_list':
                        for item in right_node.children:
                            if item.type == 'composite_literal':
                                type_node = item.child_by_field_name('type')
                                if type_node:
                                    struct_type = type_node.text.decode(
                                        'utf-8')
                                    for var_name in var_names:
                                        var_types[var_name] = struct_type

            # Recurse to handle nested structures
            called_components.update(
                self._rec_extract_called_nodes(child, var_types))

        return called_components

    def extract_callable_components(self):
        pass

    def extract_called_components(self):
        var_types = {}
        return self._rec_extract_called_nodes(self.tree.root_node, var_types)

    def extract_imports(self):
        imports = set()

        def _extract_imports(node: Node):
            # Iterate through each child of the current node
            for child in node.children:

                # If we encounter an import_declaration node
                if child.type == 'import_declaration':

                    for child2 in child.children:
                        if child2.type == "import_spec_list":
                            import_spec_list = child2
                            break

                    if import_spec_list:
                        # Ensure import_spec_list has children
                        for import_spec in import_spec_list.children:
                            if import_spec.type == 'import_spec':
                                # Extract path from import_spec
                                path_node = import_spec.child_by_field_name(
                                    'path')
                                if path_node and path_node.type == 'interpreted_string_literal':
                                    # Decode the path and clean it
                                    path = path_node.text.decode(
                                        'utf-8').strip('"')
                                    imports.add(path)

                # Recurse into child nodes to handle nested structures
                _extract_imports(child)

        # Start extraction from the root node
        _extract_imports(self.tree.root_node)

        # Convert set to list and return
        return list(imports)
