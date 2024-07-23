from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from typing import List
import uuid
import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser


class CppFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)
        self.file_id = str(uuid.uuid4())

        # Load the compiled language grammar for C++
        CPP_LANGUAGE = Language(tscpp.language())
        self.parser = Parser(CPP_LANGUAGE)

        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

    def extract_component_names(self):
        components = []

        def visit_node(node, class_name=None):
            if node.type == "function_definition":
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node:
                    func_name = func_node.text.decode('utf-8').replace(
                        "::", ".")
                    if class_name:
                        func_name = f"{class_name}.{func_name}"
                    components.append(func_name)
            elif node.type == "class_specifier":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    class_name = class_name_node.text.decode('utf-8')
                    components.append(class_name)

        def traverse_tree(node, class_name=None):
            if node.type == "class_specifier":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    class_name = class_name_node.text.decode('utf-8')
                    visit_node(node, class_name)
                    for child in node.children:
                        traverse_tree(child, class_name)
            else:
                visit_node(node, class_name)
                for child in node.children:
                    traverse_tree(child, class_name)

        traverse_tree(self.tree.root_node)

        modules = [component.replace("-", "_") for component in components]

        return modules

    def extract_called_components(self) -> List[str]:
        called_components = set()
        variable_to_class = {}

        def visit_node(node, class_scope=None):
            if node.type == "call_expression":
                func_node = node.child_by_field_name("function")
                if func_node:
                    func_name = func_node.text.decode('utf-8')
                    if class_scope and func_name in class_scope:
                        func_name = f"{class_scope}.{func_name}"
                    called_components.add(func_name)
            elif node.type == "field_expression":
                var_node = node.child(0)
                if var_node and var_node.text.decode(
                        'utf-8') in variable_to_class:
                    var_name = var_node.text.decode('utf-8')
                    field_node = node.child_by_field_name("field")
                    if field_node:
                        func_name = f"{variable_to_class[var_name]}.{field_node.text.decode('utf-8')}"
                        called_components.add(func_name)
            elif node.type == "declaration":
                type_node = node.child(0)
                var_node = node.child(1)
                if type_node and var_node:
                    var_name = var_node.text.decode('utf-8')
                    type_name = type_node.text.decode('utf-8')
                    if type_name in class_names:
                        variable_to_class[var_name] = type_name

        def traverse_tree(node, class_scope=None):
            visit_node(node, class_scope)
            for child in node.children:
                traverse_tree(child, class_scope)

        class_names = [
            component for component in self.extract_component_names()
            if '.' not in component
        ]
        traverse_tree(self.tree.root_node)

        # Filter out variable-based calls
        filtered_called_components = set()
        for called_component in called_components:
            parts = called_component.split('.')
            if len(parts) > 1 and parts[0] in variable_to_class:
                class_name = variable_to_class[parts[0]]
                method_name = parts[1]
                filtered_called_components.add(f"{class_name}.{method_name}")
            else:
                filtered_called_components.add(called_component)

        return list(filtered_called_components)

    def extract_callable_components(self):
        callable_components = set()

        def visit_node(node, class_name=None):
            if node.type == "function_definition":
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node:
                    func_name = func_node.text.decode('utf-8').replace(
                        "::", ".")
                    callable_components.add(func_name)
            elif node.type == "class_specifier":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    class_name = class_name_node.text.decode('utf-8')
                    callable_components.add(class_name)

        def traverse_tree(node):
            visit_node(node)
            for child in node.children:
                traverse_tree(child)

        traverse_tree(self.tree.root_node)

        return list(callable_components)

    def extract_imports(self):
        imports = []

        def visit_node(node):
            if node.type == "preproc_include":
                include_node = node.child_by_field_name("path")
                if include_node:
                    imports.append(
                        include_node.text.decode('utf-8').strip('"<>'))

        def traverse_tree(node):
            visit_node(node)
            for child in node.children:
                traverse_tree(child)

        traverse_tree(self.tree.root_node)

        return imports


class CppComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: 'TreeSitterFileParser') -> None:
        super().__init__(component_name, component_file_path, file_parser)
        self.parser = file_parser.parser
        self.tree = file_parser.tree
        self.struct_variable_types = {
        }  # Dictionary to store variable to struct type mappings
        self.current_scope = [
        ]  # To track the current scope of variable declarations
        self.component_code = self.extract_component_code()

    def extract_component_code(self):

        def extract_imports_from_source():
            imports = []
            for node in self.tree.root_node.children:
                if node.type == "preproc_include":
                    include_node = node.child_by_field_name("path")
                    if include_node:
                        imports.append(
                            self.file_parser.source_code[node.start_byte:node.
                                                         end_byte])
            return imports

        # Use this function to get imports directly
        imports_code = "".join(extract_imports_from_source())

        code = self._extract_component_code()
        return imports_code + "\n" + code

    def extract_callable_objects(self):
        code = self.extract_component_code()
        tree = self.parser.parse(bytes(code, "utf8"))
        called_components = set()

        def _extract_components(node, components, struct_vars):
            if node.type == 'call_expression':
                function_name = node.child_by_field_name(
                    'function').text.decode('utf-8')
                components.add(function_name)
            elif node.type == 'field_expression':
                variable_name = node.child(0).text.decode('utf-8')
                field_name = node.child(2).text.decode('utf-8')
                if variable_name in struct_vars:
                    struct_field = f"{struct_vars[variable_name]}.{field_name}"
                    components.add(struct_field)
            elif node.type == 'declaration' and node.child(
                    0).type == 'struct_specifier':
                struct_name = node.child(0).child_by_field_name(
                    'name').text.decode('utf-8')
                var_name = node.child(1).text.decode('utf-8')
                struct_vars[var_name] = struct_name
            # Recursively go through all child nodes
            for child in node.children:
                _extract_components(child, components, struct_vars)

        root_node = tree.root_node
        struct_vars = {}
        _extract_components(root_node, called_components, struct_vars)
        return list(called_components)

    def _extract_component_code(self):
        component_name_splitted = self.component_name.replace(".", "::")

        def visit_node(node):
            if node.type == "function_definition" and node.child_by_field_name(
                    "declarator"):
                self.component_type = "function"
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node and func_node.text.decode(
                        'utf-8') == component_name_splitted[0]:
                    return node
            elif node.type == "class_specifier" and node.child_by_field_name(
                    "name"):
                class_name = node.child_by_field_name("name").text.decode(
                    'utf-8')
                if class_name == component_name_splitted[0]:
                    self.component_type = "class"
                    return node

        def traverse_tree(node):
            result_node = visit_node(node)
            if result_node:
                return result_node
            for child in node.children:
                result_node = traverse_tree(child)
                if result_node:
                    return result_node

        root_node = self.tree.root_node
        found_node = traverse_tree(root_node)
        if found_node:
            extracted_code = self.file_parser.source_code[
                found_node.start_byte:found_node.end_byte]
            if self.component_type == "class" and len(
                    component_name_splitted) > 1:
                self.component_type = "class_method"
                method_name = component_name_splitted[1]
                method_code = self._extract_method_code(
                    found_node, method_name)
                if method_code:
                    return f"class {component_name_splitted[0]} {{\n{method_code}\n}}"
            return extracted_code
        return ""

    def _extract_method_code(self, class_node, method_name):
        body = class_node.child_by_field_name("body")
        if body:
            for class_body_node in body.children:
                if class_body_node.type == "function_definition" and class_body_node.child_by_field_name(
                        "declarator"):
                    if class_body_node.child_by_field_name(
                            "declarator").child_by_field_name(
                                "declarator").text.decode(
                                    'utf-8') == method_name:
                        return self.file_parser.source_code[
                            class_body_node.start_byte:class_body_node.
                            end_byte]
        return ""


# Usage
file_path = "/Users/elisey/AES/test_repo_folder/arxiv-feed/test.cpp"
parser = CppFileParser(file_path, "your_repo_name")

print("Component Names:")
print(parser.extract_component_names())

print("\nCalled Components:")
print(parser.extract_called_components())

print("\nCallable Components:")
print(parser.extract_callable_components())

print("\nImports:")
print(parser.extract_imports())

# helper = CppComponentFillerHelper("MyClass", file_path, parser)
# print()
# print(helper.extract_component_code())
# print(helper.extract_callable_objects())
