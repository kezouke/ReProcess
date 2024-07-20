from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from typing import List
import uuid
import tree_sitter_c as tsc
from tree_sitter import Language, Parser


class CFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)
        self.file_id = str(uuid.uuid4())

        # Load the compiled language grammar
        C_LANGUAGE = Language(tsc.language())
        self.parser = Parser(C_LANGUAGE)

        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

    def extract_component_names(self):
        components = []

        def visit_node(node):
            if node.type == "function_definition":
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node:
                    func_name = func_node.text.decode('utf-8')
                    components.append(func_name)
            elif node.type == "struct_specifier":
                struct_name = node.child_by_field_name("name").text.decode(
                    'utf-8')
                components.append(struct_name)
                body = node.child_by_field_name("body")
                if body:
                    for struct_node in body.children:
                        if struct_node.type == "field_declaration":
                            field_name = struct_node.child_by_field_name(
                                "declarator").text.decode('utf-8')
                            components.append(f"{struct_name}.{field_name}")

        def traverse_tree(node):
            visit_node(node)
            for child in node.children:
                traverse_tree(child)

        traverse_tree(self.tree.root_node)

        modules = [component.replace("-", "_") for component in components]

        return modules

    def extract_called_components(self) -> List[str]:
        called_components = set()

        def visit_node(node):
            if node.type == "call_expression":
                func_node = node.child_by_field_name("function")
                if func_node:
                    called_components.add(func_node.text.decode('utf-8'))
            elif node.type == "field_expression":
                field_node = node.child_by_field_name("field")
                if field_node:
                    called_components.add(field_node.text.decode('utf-8'))

        def traverse_tree(node):
            visit_node(node)
            for child in node.children:
                traverse_tree(child)

        traverse_tree(self.tree.root_node)

        return list(called_components)

    def extract_callable_components(self):
        callable_components = set()

        def visit_node(node):
            if node.type == "function_definition":
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node:
                    func_name = func_node.text.decode('utf-8')
                    callable_components.add(func_name)
            elif node.type == "struct_specifier":
                struct_name = node.child_by_field_name("name").text.decode(
                    'utf-8')
                callable_components.add(struct_name)
                body = node.child_by_field_name("body")
                if body:
                    for struct_node in body.children:
                        if struct_node.type == "field_declaration":
                            field_name = struct_node.child_by_field_name(
                                "declarator").text.decode('utf-8')
                            callable_components.add(
                                f"{struct_name}.{field_name}")

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


class CComponentFillerHelper(TreeSitterComponentFillerHelper):

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
        component_name_splitted = self.component_name.split(".")

        def visit_node(node):
            if node.type == "function_definition" and node.child_by_field_name(
                    "declarator"):
                self.component_type = "function"
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node and func_node.text.decode(
                        'utf-8') == component_name_splitted[0]:
                    return node
            elif node.type == "struct_specifier" and node.child_by_field_name(
                    "name"):
                struct_name = node.child_by_field_name("name").text.decode(
                    'utf-8')
                if struct_name == component_name_splitted[0]:
                    self.component_type = "structure"
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
            if self.component_type == "structure" and len(
                    component_name_splitted) > 1:
                self.component_type = "structure_field"
                field_name = component_name_splitted[1]
                field_code = self._extract_field_code(found_node, field_name)
                if field_code:
                    return f"struct {component_name_splitted[0]} {{\n{field_code}\n}}"
            return extracted_code
        return ""

    def _extract_field_code(self, struct_node, field_name):
        body = struct_node.child_by_field_name("body")
        if body:
            for struct_node in body.children:
                if struct_node.type == "field_declaration" and struct_node.child_by_field_name(
                        "declarator"):
                    if struct_node.child_by_field_name(
                            "declarator").text.decode('utf-8') == field_name:
                        return self.file_parser.source_code[
                            struct_node.start_byte:struct_node.end_byte]
        return ""


# # Test the parser with a sample C file
# file_path = "/Users/elisey/AES/test_repo_folder/arxiv-feed/test.c"
# parser = CFileParser(file_path)

# print("Component Names:")
# print(parser.extract_component_names())

# print("\nCalled Components:")
# print(parser.extract_called_components())

# print("\nCallable Components:")
# print(parser.extract_callable_components())

# print("\nImports:")
# print(parser.extract_imports())

# helper = CComponentFillerHelper("main", file_path, parser)
# print(helper.extract_component_code())
# print()
# print(helper.extract_callable_objects())
