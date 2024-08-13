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
        self.variable_class_map = {}
        self.imports_map = self._map_imported_classes()
        self.local_component_names = self.extract_component_names()

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

    def _map_imported_classes(self):
        imports = self.extract_imports()
        imports_map = {}
        for imp in imports:
            # Extract the short class name from the import statement
            class_name = imp.split('.')[-1]
            imports_map[class_name] = imp
        return imports_map

    def _extract_called_components(self, node):
        components = []

        # Handle object creation expressions (e.g., new ClassName())
        if node.type == "object_creation_expression":
            class_name_node = node.child_by_field_name("type")
            if class_name_node:
                class_name = class_name_node.text.decode("utf8").strip()
                parent = node.parent
                if parent and parent.type == "variable_declarator":
                    variable_name_node = parent.child_by_field_name("name")
                    if variable_name_node:
                        variable_name = variable_name_node.text.decode(
                            "utf8").strip()
                        # Map the variable name to the fully qualified class type
                        full_class_name = self._get_fully_qualified_name(
                            class_name)
                        self.variable_class_map[
                            variable_name] = full_class_name
                        components.append(full_class_name)

        # Handle method invocations
        elif node.type == "method_invocation":
            method_name_node = node.child_by_field_name("name")
            object_node = node.child_by_field_name("object")

            if method_name_node and object_node:
                method_name = method_name_node.text.decode("utf8").strip()
                object_name = object_node.text.decode("utf8").strip()

                # Check if the object name is a variable mapped to a class
                class_name = self.variable_class_map.get(
                    object_name, object_name)
                full_class_name = self._get_fully_qualified_name(class_name)
                components.append(f"{full_class_name}.{method_name}")

        # Recursively process children nodes
        for child in node.children:
            components.extend(self._extract_called_components(child))

        return components

    def _get_fully_qualified_name(self, class_name):
        # Check if the class is imported
        if class_name in self.imports_map:
            return self.imports_map[class_name]
        # Check if the class is local
        for component in self.local_component_names:
            if component.endswith(f".{class_name}"):
                return component
        # Return the class name as is if not found in imports or local components
        return class_name

    def extract_called_components(self):
        return list(set(self._extract_called_components(self.tree.root_node)))

    def extract_callable_components(self):
        return self.local_component_names

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
        self.imports = []
        self.component_type = None
        self.source_code = self.file_parser.source_code.splitlines()

    def extract_component_code(self):
        # Initialize imports and component type
        self.component_type = None
        self.imports = self._get_import_statements()

        # Break down the component name to match nested structure
        name_parts = self.component_name.split(self.file_parser.packages +
                                               ".")[-1].split(".")

        # Start searching from the root node
        root_node = self.file_parser.tree.root_node

        # Search for the component node
        component_node = self._find_component_node(root_node, name_parts)

        # If found, extract the code
        if component_node:
            # Extract the relevant imports based on component usage
            used_imports = self._get_used_imports(component_node)
            # Extract the code and prepend relevant import statements
            component_code = self._extract_code_from_node(component_node)
            return "\n".join(used_imports) + "\n\n" + component_code
        else:
            return None

    def _get_import_statements(self):
        imports = []
        for child in self.file_parser.tree.root_node.children:
            if child.type == "import_declaration":
                import_statement = self._node_text(child)
                imports.append(import_statement)
        return imports

    def _get_used_imports(self, component_node):
        used_imports = set()
        called_components = self.file_parser._extract_called_components(
            component_node)
        for component in called_components:
            for imp in self.imports:
                if imp.endswith(component.split(".")[-1] + ";"):
                    used_imports.add(imp)
        return sorted(used_imports)

    def _find_component_node(self, node, name_parts):
        if node.type in ["class_declaration", "method_declaration"]:
            # Get the exact name of the class or method
            node_name = self._node_text(node.child_by_field_name("name"))
            if node_name == name_parts[0]:
                # Set the component type if a match is found
                self.component_type = "class" if node.type == "class_declaration" else "method"
                if len(name_parts) == 1:
                    return node
                else:
                    # Continue searching within the nested body
                    body_node = node.child_by_field_name("body")
                    if body_node:
                        return self._find_component_node(
                            body_node, name_parts[1:])

        # Recursively search child nodes
        for child in node.children:
            result = self._find_component_node(child, name_parts)
            if result:
                return result

        return None

    def _extract_code_from_node(self, node):
        # Extract code from the node, maintaining the original tabulation
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        code_lines = self.source_code[start_line:end_line + 1]

        # Return the code with correct indentation
        return "\n".join(code_lines)

    def _node_text(self, node):
        return node.text.decode('utf-8').strip()

    def extract_callable_objects(self):
        return super().extract_callable_objects()


# Usage
file_path = "/home/arxiv-feed/feed/main.java"
parser = JavaFileParser(file_path, "arxiv-feed")

print("Component Names:")
print(parser.extract_component_names())

print("\nImports:")
print(parser.extract_imports())

print("\nCalled components:")
print(parser.extract_called_components())

print("\nCallable components:")
print(parser.extract_callable_components())

helper = JavaComponentFillerHelper("feed.main.java.Main.Logger", file_path,
                                   parser)
print("\nComponent Code:")
print(helper.extract_component_code())
'''
Output:
Component Names:
['feed.main.java.Main', 'feed.main.java.Main.main', 'feed.main.java.Main.Logger', 'feed.main.java.Main.Logger.log']

Imports:
['utilities.MathUtils', 'services.GreetingService']

Called components:
['services.GreetingService', 'feed.main.java.Main.Logger.log', 'System.out.println', 'feed.main.java.Main.Logger', 'utilities.MathUtils', 'utilities.MathUtils.add', 'services.GreetingService.getGreeting']

Callable components:
['feed.main.java.Main', 'feed.main.java.Main.main', 'feed.main.java.Main.Logger', 'feed.main.java.Main.Logger.log']

Component Code:
import utilities.MathUtils;
import services.GreetingService;
        void log(String message) {
            System.out.println("LOG: " + message);
        }
'''
