from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_javascript as tsjs
import os


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
        base_directory = os.path.dirname(self.file_path)

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
        return super().extract_component_code()

    def extract_callable_objects(self):
        return super().extract_callable_objects()
