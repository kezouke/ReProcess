from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser, Node
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_go as tsgo

CHUNK_QUERY = """
    [
        (function_declaration) @function
        (type_declaration) @type
        (method_declaration) @method
    ]
""".strip()


class GoFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        """Initializes the Tree-sitter parser with the Go language grammar."""
        # Load the compiled language grammar for Go
        GO_LANGUAGE = Language(tsgo.language())
        self.parser = Parser(GO_LANGUAGE)

        # Read the file content and parse it
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        # Adjust the file path relative to the repository
        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.packages = get_import_statement_path(
            cutted_path.replace(".go", ""))
        self.file_path = cutted_path[1:]

    def _rec_component_name_extractor(self,
                                      node: Node,
                                      current_struct: str = "") -> list:
        component_names = []

        # Traverse the AST
        for child in node.children:
            # Check for a struct type declaration
            if child.type == 'type_declaration':
                type_spec = None
                for child2 in child.children:
                    if child2.type == "type_spec":
                        type_spec = child2
                        break
                if type_spec:
                    # Extract the struct name from the type_spec
                    struct_name = type_spec.children[0].text.decode('utf-8')
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
        callable_components = set()

        def _extract_callable_components(node: Node):
            for child in node.children:
                # Extract function declarations
                if child.type == 'function_declaration':
                    function_name_node = child.child_by_field_name('name')
                    if function_name_node:
                        function_name = function_name_node.text.decode('utf-8')
                        callable_components.add(function_name)

                # Extract method declarations
                elif child.type == 'method_declaration':
                    method_name_node = child.child_by_field_name('name')
                    receiver_node = child.child_by_field_name('receiver')
                    if method_name_node and receiver_node:
                        # The receiver type is the struct name
                        receiver_type_node = receiver_node.named_child(
                            0).child_by_field_name('type')
                        if receiver_type_node:
                            struct_name = receiver_type_node.text.decode(
                                'utf-8')
                            method_name = method_name_node.text.decode('utf-8')
                            full_method_name = f"{struct_name}.{method_name}"
                            callable_components.add(full_method_name)

                # Recurse to handle nested structures
                _extract_callable_components(child)

        # Start extraction from the root node
        _extract_callable_components(self.tree.root_node)

        return list(callable_components)

    def extract_called_components(self):
        var_types = {}
        return list(
            self._rec_extract_called_nodes(self.tree.root_node, var_types))

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


class GoComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        # Determine the type of component from its name
        component_name = self.component_name.replace(
            f"{self.file_parser.packages}.", "")

        def extract_code_from_node(node: Node, name: str) -> str:
            """Extract code for a specific component based on its name."""
            code = ""

            for child in node.children:
                # Check for a struct type declaration
                if child.type == 'type_declaration':
                    type_spec = None
                    for child2 in child.children:
                        if child2.type == "type_spec":
                            type_spec = child2
                            break
                    if type_spec:
                        # Extract the struct name from the type_spec
                        struct_name = type_spec.children[0].text.decode(
                            'utf-8')
                        if struct_name == name:
                            self.component_type = "struct"
                            code = self.source_code[
                                type_spec.start_byte:type_spec.end_byte]
                            break

                elif child.type == 'method_declaration':
                    method_name_node = child.child_by_field_name('name')
                    receiver_node = child.child_by_field_name('receiver')
                    if method_name_node and receiver_node:
                        method_name = method_name_node.text.decode('utf-8')
                        receiver_type_node = receiver_node.named_child(
                            0).child_by_field_name('type')
                        if receiver_type_node and receiver_type_node.text.decode(
                                'utf-8') == name.split('.')[0]:
                            if method_name == name.split('.')[-1]:
                                self.component_type = "method"
                                # Extract the code for the method
                                code = self.source_code[child.start_byte:child.
                                                        end_byte]
                                break

                elif child.type == 'function_declaration':
                    function_name_node = child.child_by_field_name('name')
                    if function_name_node and function_name_node.text.decode(
                            'utf-8') == name:
                        # Extract the code for the function
                        self.component_type = "function"
                        code = self.source_code[child.start_byte:child.
                                                end_byte]
                        break

                # Recurse into child nodes
                code += extract_code_from_node(child, name)

            return code

        # Get the code for the component
        component_code = extract_code_from_node(
            self.file_parser.tree.root_node, component_name)

        # Include import statements if the component is a function
        if component_code:
            import_code = self.file_parser.extract_imports()
            imports = "\n".join([
                f'import "{imp}"' for imp in import_code
                if imp.split("/")[-1] in component_code
            ])
            component_code = f"{imports}\n\n{component_code}"

        return component_code

    def extract_callable_objects(self):
        var_types = {}
        called_components = set()
        imports = self.file_parser.extract_imports()
        package_name = self.file_parser.packages.replace("/", ".")

        # Create a map of import aliases to their full paths
        import_alias_map = {
            imp.split("/")[-1]: imp.replace("/", ".")
            for imp in imports
        }

        def resolve_full_name(name: str):
            """Resolve the full name of a component using imports and the default package."""
            # Check if the name matches any import alias
            for alias, full_path in import_alias_map.items():
                if name == alias or name.startswith(alias + "."):
                    # If it's an alias match, replace the alias with the full path
                    return name.replace(alias, full_path)

            # Otherwise, assume it's from the same package
            return f"{package_name}.{name}"

        def traverse_node(node: Node, current_package: str):
            for child in node.children:
                if child.type == 'call_expression':
                    function_node = child.child_by_field_name('function')
                    if function_node:
                        if function_node.type == 'selector_expression':
                            # This is a method call on a struct
                            operand_node = function_node.child_by_field_name(
                                'operand')
                            field_node = function_node.child_by_field_name(
                                'field')
                            if operand_node and field_node:
                                operand_name = operand_node.text.decode(
                                    'utf-8')
                                field_name = field_node.text.decode('utf-8')
                                struct_name = var_types.get(
                                    operand_name, operand_name)
                                full_method_name = f"{struct_name}.{field_name}"
                                called_components.add(
                                    resolve_full_name(full_method_name))
                        else:
                            # This is a function call
                            function_name = function_node.text.decode('utf-8')
                            called_components.add(
                                resolve_full_name(function_name))

                elif child.type == 'short_var_declaration':
                    left_node = child.child_by_field_name('left')
                    right_node = child.child_by_field_name('right')
                    if left_node and right_node:
                        var_names = [
                            var.text.decode('utf-8')
                            for var in left_node.children
                        ]
                        if right_node.type == 'expression_list':
                            for item in right_node.children:
                                if item.type == 'composite_literal':
                                    type_node = item.child_by_field_name(
                                        'type')
                                    if type_node:
                                        struct_type = type_node.text.decode(
                                            'utf-8')
                                        for var_name in var_names:
                                            var_types[var_name] = struct_type

                elif child.type == 'parameter_list':
                    # Capture function parameters and their types
                    for param in child.named_children:
                        param_name_node = param.child_by_field_name('name')
                        param_type_node = param.child_by_field_name('type')
                        if param_name_node and param_type_node:
                            var_name = param_name_node.text.decode('utf-8')
                            var_type = param_type_node.text.decode('utf-8')
                            var_types[var_name] = var_type

                traverse_node(child, current_package)

        # Start traversal from the root node
        component_code_tree = self.file_parser.parser.parse(
            bytes(self.component_code, "utf8"))
        traverse_node(component_code_tree.root_node, package_name)

        return list(called_components)

    def extract_signature(self):
        GO_LANGUAGE = Language(tsgo.language())
        parser = Parser(GO_LANGUAGE)
        query = GO_LANGUAGE.query(CHUNK_QUERY)
        tree = parser.parse(bytes(self.component_code, encoding="UTF-8"))

        processed_lines = set()
        source_lines = self.component_code.splitlines()
        simplified_lines = source_lines[:]

        captured = query.captures(tree.root_node)

        for name in captured:
            for node in captured[name]:
                start_line = node.start_point[0]
                end_line = node.end_point[0]

                lines = list(range(start_line, end_line + 1))
                if any(line in processed_lines for line in lines):
                    continue

                simplified_lines[start_line] = source_lines[start_line]

                for line_num in range(start_line + 1, end_line + 1):
                    simplified_lines[line_num] = None  # type: ignore

                processed_lines.update(lines)

        return "\n".join(line for line in simplified_lines if line is not None)
