from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_java as tsjava
import uuid


class JavaFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)
        self.file_id = str(uuid.uuid4())
        cutted_path = self.file_path.split(repo_name)[-1]

        JAVA_LANGUAGE = Language(tsjava.language())
        self.parser = Parser(JAVA_LANGUAGE)
        self.packages = get_import_statement_path(cutted_path)

        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        self.file_path = cutted_path[1:]

    def _find_cmp_names(self, node, class_path=""):
        components = []

        # If the node is a class declaration, extract the class name
        if node.type == 'class_declaration':
            class_name = node.child_by_field_name('name').text.decode('utf-8')
            full_class_name = f"{class_path}.{class_name}" if class_path else class_name
            components.append(full_class_name)

            # Recursively extract nested classes and methods
            class_body = node.child_by_field_name('body')
            for child in class_body.children:
                components.extend(self._find_cmp_names(child, full_class_name))

        # If the node is a method declaration, extract the method name
        elif node.type == 'method_declaration':
            method_name = node.child_by_field_name('name').text.decode('utf-8')
            full_method_name = f"{class_path}.{method_name}" if class_path else method_name
            components.append(full_method_name)

        # Recursively process children nodes, but only if we're not already inside a class or method
        for child in node.children:
            if node.type not in ['class_declaration', 'method_declaration']:
                components.extend(self._find_cmp_names(child, class_path))

        return components

    def extract_component_names(self):
        root_node = self.tree.root_node
        components = self._find_cmp_names(root_node)
        return [self.packages + "." + cmp_name for cmp_name in components]

    def _extract_called_components(node):
        components = []

        if node.type == "method_invocation":
            method_name_node = node.child_by_field_name("name")
            object_node = node.child_by_field_name("object")

            if method_name_node and object_node:
                method_name = method_name_node.text.decode("utf8").strip()
                object_name = object_node.text.decode("utf8").strip()
                components.append(f"{object_name}.{method_name}")

        for child in node.children:
            components.extend(extract_called_components(child))

        return components

    def extract_called_components(self):
        return super().extract_called_components()

    def extract_callable_components(self):
        return super().extract_callable_components()

    def _rec_import_finder(self, node):
        imports = []
        for child in node.children:
            if child.type == "import_declaration":
                scoped_identifier = None
                for grandchild in child.children:
                    if grandchild.type == "scoped_identifier":
                        scoped_identifier = grandchild.text.decode(
                            "utf8").strip()
                        imports.append(scoped_identifier)
                        break
            elif child.type == "program":
                imports.extend(self._rec_import_finder(child))

        return imports

    def extract_imports(self):
        root_node = self.tree.root_node
        return self._rec_import_finder(root_node)


class JavaComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        return super().extract_component_code()

    def extract_callable_objects(self):
        return super().extract_callable_objects()


# Usage
file_path = "/Users/elisey/AES/test_repo_folder/arxiv-feed/main.java"
parser = JavaFileParser(file_path, "arxiv-feed")

print("Component Names:")
print(parser.extract_component_names())

print("\nImports:")
print(parser.extract_imports())
