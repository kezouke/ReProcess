from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from typing import List
import uuid
import re
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
        self.code = file_parser.source_code
        self.class_methods = {}
        self.component_code = self.extract_component_code()

    def _get_node_text(self, node):
        return self.code[node.start_byte:node.end_byte]

    def _strip_parameters(self, name):
        # Strip off parameters from the function name
        return re.sub(r'\(.*\)', '', name)

    def _find_class_methods(self):
        # Find all methods defined outside class bodies
        for node in self.tree.root_node.children:
            if node.type == 'function_definition':
                declarator = node.child_by_field_name('declarator')
                if declarator:
                    qualified_name = self._get_node_text(declarator).split(
                        '::')
                    if len(qualified_name) > 1:
                        class_name = '::'.join(qualified_name[:-1])
                        method_name = self._strip_parameters(
                            qualified_name[-1])
                        if class_name not in self.class_methods:
                            self.class_methods[class_name] = {}
                        self.class_methods[class_name][method_name] = node

    def _find_component_node(self, node, name_parts):
        if node.type == 'function_definition' or node.type == 'class_specifier':
            declarator = None
            if node.type == 'function_definition':
                declarator = node.child_by_field_name('declarator')
            elif node.type == 'class_specifier':
                declarator = node.child_by_field_name('name')

            if declarator and self._strip_parameters(
                    declarator.text.decode('utf8')) == name_parts[0]:
                if len(name_parts) == 1:
                    return node
                if node.type == 'class_specifier':
                    body = node.child_by_field_name('body')
                    if body:
                        for child in body.children:
                            if self._find_component_node(
                                    child, name_parts[1:]):
                                return self._find_component_node(
                                    child, name_parts[1:])

        for child in node.children:
            result = self._find_component_node(child, name_parts)
            if result:
                return result

        return None

    def _extract_component(self, component_name):
        self._find_class_methods()
        name_parts = component_name.split('.')
        if len(name_parts
               ) > 1 and name_parts[0] in self.class_methods and name_parts[
                   1] in self.class_methods[name_parts[0]]:
            # Handle class methods defined outside the class body
            component_node = self.class_methods[name_parts[0]][name_parts[1]]
            return self._get_node_text(component_node)

        component_node = self._find_component_node(self.tree.root_node,
                                                   name_parts)
        if component_node:
            if component_node.type == 'class_specifier':
                # Include methods defined outside the class body
                class_code = self._get_node_text(component_node)
                class_name = name_parts[0]
                if class_name in self.class_methods:
                    for method in self.class_methods[class_name].values():
                        class_code += '\n' + self._get_node_text(method)
                return class_code
            else:
                return self._get_node_text(component_node)
        else:
            return None

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

        code = self._extract_component(self.component_name)
        return imports_code + "\n" + code

    def extract_callable_objects(self):
        called_components = set()
        variable_to_class = {}

        code = self.component_code
        tree = self.parser.parse(bytes(code, "utf8"))

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
            component
            for component in self.file_parser.extract_component_names()
            if '.' not in component
        ]
        traverse_tree(tree.root_node)

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

helper = CppComponentFillerHelper("globalFunction", file_path, parser)
print()
print(helper.extract_component_code())
print(helper.extract_callable_objects())
