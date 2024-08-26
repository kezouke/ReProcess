from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_javascript as tsjs


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

        return components

    def extract_called_components(self):
        """
        Extracts all components (functions and methods) being called in the parsed AST code.
        """
        called_components = set()
        variable_types = {
        }  # Dictionary to track variable names and their types

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
                                called_components.add(
                                    f"{class_type}.{property_name}")
                            else:
                                # If object_name is not a tracked instance, add it directly
                                called_components.add(
                                    f"{object_name}.{property_name}")

            # Recursively traverse children
            for child in node.children:
                traverse(child)

        # Start traversing from the root node
        traverse(self.tree.root_node)

        return list(called_components)

    def extract_callable_components(self):
        return super().extract_callable_components()

    def extract_imports(self):
        return super().extract_imports()


class JavaScriptComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        return super().extract_component_code()

    def extract_callable_objects(self):
        return super().extract_callable_objects()
