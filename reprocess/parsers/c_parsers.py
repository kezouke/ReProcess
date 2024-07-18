from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from typing import List
import uuid
import tree_sitter_c as tsc
from tree_sitter import Language, Parser


class CFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str) -> None:
        super().__init__(file_path)
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
