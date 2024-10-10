from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_javascript as tsjs
import os

CHUNK_QUERY = """
    [
        (class_declaration) @class
        (function_declaration) @function
        (method_definition) @method
        (field_definition) @field
    ]
""".strip()


class JavaScriptFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        cutted_path = self.file_path.split(self.repo_name)[-1]

        JS_LANGUAGE = Language(tsjs.language())
        self.parser = Parser(JS_LANGUAGE)

        self.packages = get_import_statement_path(cutted_path)

        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.packages = get_import_statement_path(
            cutted_path.replace(".js", ""))
        self.file_path = cutted_path[1:]

    def extract_component_names(self):
        """
        Extracts component names such as classes, functions, and methods,
        including handling nested classes.
        """
        components = []

        # Helper function to traverse nodes
        def traverse(node, prefix=""):
            # Check for class declarations
            if node.type == "class_declaration":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    class_name = self.source_code[
                        class_name_node.start_byte:class_name_node.end_byte]
                    full_class_name = f"{prefix}{class_name}" if prefix else class_name
                    components.append(full_class_name)
                    # Traverse class body to find methods and nested classes
                    class_body_node = node.child_by_field_name("body")
                    if class_body_node:
                        for child in class_body_node.children:
                            if child.type == "method_definition":
                                method_name_node = child.child_by_field_name(
                                    "name")
                                if method_name_node:
                                    method_name = self.source_code[
                                        method_name_node.
                                        start_byte:method_name_node.end_byte]
                                    components.append(
                                        f"{full_class_name}.{method_name}")
                            elif child.type == "field_definition":
                                value_node = child.child_by_field_name("value")
                                if value_node and value_node.type == "class":
                                    # Handle static nested class
                                    nested_class_node = value_node
                                    nested_class_name_node = child.child_by_field_name(
                                        "property")
                                    if nested_class_name_node:
                                        nested_class_name = self.source_code[
                                            nested_class_name_node.start_byte:
                                            nested_class_name_node.end_byte]
                                        nested_class_full_name = f"{full_class_name}.{nested_class_name}"
                                        components.append(
                                            nested_class_full_name)
                                        # Recursively traverse the nested class
                                        traverse(nested_class_node,
                                                 f"{nested_class_full_name}.")

            # Handle method definitions in nested classes
            elif node.type == "method_definition" and prefix != "":
                method_name_node = node.child_by_field_name("name")
                if method_name_node:
                    method_name = self.source_code[
                        method_name_node.start_byte:method_name_node.end_byte]
                    components.append(f"{prefix}{method_name}")

            # Handle function declarations
            elif node.type == "function_declaration":
                function_name_node = node.child_by_field_name("name")
                if function_name_node:
                    function_name = self.source_code[
                        function_name_node.start_byte:function_name_node.
                        end_byte]
                    components.append(function_name)

            # Recursively traverse children
            for child in node.children:
                traverse(child, prefix)

        # Start traversing from the root node
        traverse(self.tree.root_node)
        return [
            f"{self.packages}.{component}".replace("-", "_")
            for component in components
        ]

    def extract_called_components(self):
        """
        Extracts all components (functions and methods) being called in the parsed AST code.
        Now includes distinguishing between imported components and local components.
        """
        called_components = set()
        variable_types = {
        }  # Dictionary to track variable names and their types

        # Step 1: Store imported components in a dictionary for quick lookup
        import_map = {}
        imports = self.extract_imports()
        for imp in imports:
            # Example of `imp`: 'feed.utils.someUtilityFunction'
            module_path, component_name = imp.rsplit('.', 1)
            import_map[
                component_name] = imp  # Map the imported component to its full path

        # Step 2: Store local components
        local_components = self.extract_component_names()

        # Helper function to traverse nodes
        def traverse(node):
            # Check for variable declarations
            if node.type == "variable_declarator":
                variable_name_node = node.child_by_field_name("name")
                value_node = node.child_by_field_name("value")

                if value_node and value_node.type == "new_expression":
                    constructor_node = value_node.child_by_field_name(
                        "constructor")
                    if constructor_node:
                        variable_name = self.source_code[
                            variable_name_node.start_byte:variable_name_node.
                            end_byte]
                        constructor_name = self.source_code[
                            constructor_node.start_byte:constructor_node.
                            end_byte]
                        variable_types[variable_name] = constructor_name

            # Check for function or method calls
            elif node.type == "call_expression":
                function_node = node.child_by_field_name("function")
                if function_node:
                    if function_node.type == "identifier":
                        # Simple function call like `createAndShowCar()`
                        function_name = self.source_code[
                            function_node.start_byte:function_node.end_byte]

                        # Check if function_name matches an import or a local component
                        if function_name in import_map:
                            called_components.add(import_map[function_name])
                        else:
                            # Prepend the package path if it is a local component
                            if f"{self.packages}.{function_name}" in local_components:
                                called_components.add(
                                    f"{self.packages}.{function_name}")
                            else:
                                called_components.add(function_name)

                    elif function_node.type == "member_expression":
                        # Method call like `car.displayDetails()` or `console.log()`
                        object_node = function_node.child_by_field_name(
                            "object")
                        property_node = function_node.child_by_field_name(
                            "property")
                        if object_node and property_node:
                            object_name = self.source_code[
                                object_node.start_byte:object_node.end_byte]
                            property_name = self.source_code[
                                property_node.start_byte:property_node.
                                end_byte]

                            # Check if the object name is in the variable_types dictionary
                            if object_name in variable_types:
                                # Use class type if available
                                class_type = variable_types[object_name]
                                full_component = f"{class_type}.{property_name}"
                                if class_type in import_map:
                                    called_components.add(
                                        f"{import_map[class_type]}.{property_name}"
                                    )
                                else:
                                    called_components.add(
                                        f"{self.packages}.{full_component}")
                            else:
                                # If object_name is not a tracked instance, add it directly
                                if f"{object_name}.{property_name}" in import_map:
                                    called_components.add(import_map[
                                        f"{object_name}.{property_name}"])
                                else:
                                    called_components.add(
                                        f"{object_name}.{property_name}")

            # Recursively traverse children
            for child in node.children:
                traverse(child)

        # Start traversing from the root node
        traverse(self.tree.root_node)

        for varibale in variable_types:
            if f"{self.packages}.{variable_types[varibale]}" in local_components:
                variable_types[
                    varibale] = f"{self.packages}.{variable_types[varibale]}"
            elif variable_types[varibale] in import_map:
                variable_types[varibale] = import_map[variable_types[varibale]]

        return list(called_components) + list(variable_types.values())

    def extract_callable_components(self):
        return self.extract_component_names()

    def extract_imports(self):
        """
        Extracts all imported components from the parsed AST code and converts relative import paths
        to module paths based on the file's relative path.
        """
        imports = set()

        def combine_paths(base_path: str, relative_path: str) -> str:
            # Extract the directory part of the base path
            base_dir = os.path.dirname(base_path)

            # Join the base directory with the relative path to get the full path
            if os.path.isabs(relative_path):
                full_path = relative_path
            else:
                full_path = os.path.normpath(
                    os.path.join(base_dir, relative_path))

            # Replace directory separators with dots
            return full_path.replace(os.sep, '.')

        # Helper function to traverse nodes
        def traverse(node):
            if node.type == "import_statement":
                # Extract the source module (e.g., './utils')
                source_node = node.child_by_field_name("source")
                if source_node:
                    source_module = self.source_code[source_node.
                                                     start_byte:source_node.
                                                     end_byte].strip(" '\"")
                    source_module = combine_paths(self.file_path,
                                                  source_module)

                    # Extract the import clause which contains imported names
                    import_clause_node = None
                    for child in node.children:
                        if child.type == "import_clause":
                            import_clause_node = child

                    if import_clause_node:
                        named_imports_node = None
                        for child in import_clause_node.children:
                            if child.type == "named_imports":
                                named_imports_node = child

                        if named_imports_node:
                            for import_specifier_node in named_imports_node.children:
                                import_name_node = import_specifier_node.child_by_field_name(
                                    "name")
                                if import_name_node:
                                    import_name = self.source_code[
                                        import_name_node.
                                        start_byte:import_name_node.end_byte]
                                    imports.add(
                                        f"{source_module}.{import_name}")

            # Recursively traverse children
            for child in node.children:
                traverse(child)

        # Start traversing from the root node
        traverse(self.tree.root_node)

        return list(imports)


class JavaScriptComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        """
        Extracts the source code of the specified component, including relevant import statements.
        """
        # Get the root node of the AST
        root_node = self.file_parser.tree.root_node
        component_code = ''
        import_statements = []

        # Extract import statements first
        import_statements = self.file_parser.extract_imports()
        # Temporary storage for imports to be filtered
        imports_code = {
            imp.split(".")[-1]:
            f'import {{ {imp.split(".")[-1]} }} from "{imp.rsplit(".", 1)[0].replace(".", "/")}";'
            for imp in import_statements
        }

        # Function to decode the text of a node
        def decode_node_text(node):
            return node.text.decode('utf-8') if node else None

        # Helper function to find the node of the component
        def find_component_node(node, component_name_parts):
            if not component_name_parts:
                return None

            # Check if this node represents the target component
            if node.type == 'class_declaration':
                class_name_node = node.child_by_field_name('name')
                if class_name_node and decode_node_text(
                        class_name_node) == component_name_parts[0]:
                    if len(component_name_parts) == 1:
                        self.component_type = "class"
                        return node  # Found the target class
                    # Look for nested classes or methods within this class
                    body_node = node.child_by_field_name('body')
                    if body_node:
                        for child in body_node.children:
                            result = find_component_node(
                                child, component_name_parts[1:])
                            if result:
                                return result

            elif node.type == 'field_definition':
                # Handle field that might be a nested class
                property_node = node.child_by_field_name('property')
                value_node = node.child_by_field_name('value')
                if property_node and value_node and value_node.type == 'class':
                    if decode_node_text(
                            property_node) == component_name_parts[0]:
                        if len(component_name_parts) == 1:
                            self.component_type = "class"
                            return value_node  # Found the nested class
                        return find_component_node(value_node,
                                                   component_name_parts[1:])

            elif node.type == 'class':  # Handle nested class bodies
                if len(component_name_parts) == 0:
                    self.component_type = "class"
                    return node
                body_node = node.child_by_field_name('body')
                if body_node:
                    for child in body_node.children:
                        result = find_component_node(child,
                                                     component_name_parts)
                        if result:
                            return result

            elif node.type == 'method_definition':
                # Check if this method is the one we're looking for
                method_name_node = node.child_by_field_name('name')
                if method_name_node and decode_node_text(
                        method_name_node) == component_name_parts[0]:
                    if len(component_name_parts) == 1:
                        self.component_type = "method"
                        return node  # Found the target method

            elif node.type == 'function_declaration':
                # Check for function declarations
                function_name_node = node.child_by_field_name('name')
                if function_name_node and decode_node_text(
                        function_name_node) == component_name_parts[0]:
                    self.component_type = "function"
                    return node  # Found the target function

            # Traverse child nodes
            for child in node.children:
                result = find_component_node(child, component_name_parts)
                if result:
                    return result
            return None

        # Helper function to collect all identifiers used in the component node
        def collect_identifiers(node, identifiers):
            if node.type == 'identifier':
                identifiers.add(decode_node_text(node))
            for child in node.children:
                collect_identifiers(child, identifiers)

        # Remove package prefix from component name and split it into parts
        component_name_parts = self.component_name.replace(
            f"{self.file_parser.packages}.", "").split('.')

        # Find the component node in the AST
        component_node = find_component_node(root_node, component_name_parts)
        self.component_node = component_node

        if component_node:
            # If the component is found, extract the source code for the component
            component_code = self.file_parser.source_code[
                component_node.start_byte:component_node.end_byte]

            # Handle extraction of class declaration if missing class name
            if component_node.type == 'class' and component_node.parent.type == 'field_definition':
                # Check if this is a class nested inside a field definition
                class_name = decode_node_text(
                    component_node.parent.child_by_field_name('property'))
                if class_name:
                    class_declaration = f"class {class_name} " + component_code[
                        len('class '):]
                    component_code = class_declaration

            # Collect all identifiers used in the component code
            used_identifiers = set()
            collect_identifiers(component_node, used_identifiers)

            # Filter imports to only include those that are used
            used_imports = [
                imports_code[imp] for imp in imports_code
                if imp in used_identifiers
            ]
            imports_code = '\n'.join(used_imports)
            return imports_code + '\n\n' + component_code

        return component_code

    def extract_callable_objects(self):
        if not self.component_node:
            return []

        called_components = set()
        variable_types = {}

        # Step 1: Store imported components in a dictionary for quick lookup
        import_map = {}
        imports = self.file_parser.extract_imports()
        for imp in imports:
            module_path, component_name = imp.rsplit('.', 1)
            import_map[
                component_name] = imp  # Map the imported component to its full path

        # Step 2: Store local components
        local_components = self.file_parser.extract_component_names()

        # Helper function to traverse nodes
        def traverse(node):
            # Check for variable declarations
            if node.type == "variable_declarator":
                variable_name_node = node.child_by_field_name("name")
                value_node = node.child_by_field_name("value")

                if value_node and value_node.type == "new_expression":
                    constructor_node = value_node.child_by_field_name(
                        "constructor")
                    if constructor_node:
                        variable_name = self.file_parser.source_code[
                            variable_name_node.start_byte:variable_name_node.
                            end_byte]
                        constructor_name = self.file_parser.source_code[
                            constructor_node.start_byte:constructor_node.
                            end_byte]
                        variable_types[variable_name] = constructor_name

            # Check for function or method calls
            elif node.type == "call_expression":
                function_node = node.child_by_field_name("function")
                if function_node:
                    if function_node.type == "identifier":
                        # Simple function call like `createAndShowCar()`
                        function_name = self.file_parser.source_code[
                            function_node.start_byte:function_node.end_byte]

                        # Check if function_name matches an import or a local component
                        if function_name in import_map:
                            called_components.add(import_map[function_name])
                        else:
                            # Prepend the package path if it is a local component
                            if f"{self.file_parser.packages}.{function_name}" in local_components:
                                called_components.add(
                                    f"{self.file_parser.packages}.{function_name}"
                                )
                            else:
                                called_components.add(function_name)

                    elif function_node.type == "member_expression":
                        # Method call like `car.displayDetails()` or `console.log()`
                        object_node = function_node.child_by_field_name(
                            "object")
                        property_node = function_node.child_by_field_name(
                            "property")
                        if object_node and property_node:
                            object_name = self.file_parser.source_code[
                                object_node.start_byte:object_node.end_byte]
                            property_name = self.file_parser.source_code[
                                property_node.start_byte:property_node.
                                end_byte]

                            # Check if the object name is in the variable_types dictionary
                            if object_name in variable_types:
                                # Use class type if available
                                class_type = variable_types[object_name]
                                full_component = f"{class_type}.{property_name}"
                                if class_type in import_map:
                                    called_components.add(
                                        f"{import_map[class_type]}.{property_name}"
                                    )
                                else:
                                    called_components.add(
                                        f"{self.file_parser.packages}.{full_component}"
                                    )
                            else:
                                # If object_name is not a tracked instance, add it directly
                                if f"{object_name}.{property_name}" in import_map:
                                    called_components.add(import_map[
                                        f"{object_name}.{property_name}"])
                                else:
                                    called_components.add(
                                        f"{object_name}.{property_name}")

            # Recursively traverse children
            for child in node.children:
                traverse(child)

        # Start traversing from the component node
        traverse(self.component_node)

        # Convert variable types to their fully qualified names
        for variable in variable_types:
            if f"{self.file_parser.packages}.{variable_types[variable]}" in local_components:
                variable_types[
                    variable] = f"{self.file_parser.packages}.{variable_types[variable]}"
            elif variable_types[variable] in import_map:
                variable_types[variable] = import_map[variable_types[variable]]

        return list(called_components) + list(variable_types.values())

    def extract_signature(self):
        JS_LANGUAGE = Language(tsjs.language())
        parser = Parser(JS_LANGUAGE)
        query = JS_LANGUAGE.query(CHUNK_QUERY)
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
