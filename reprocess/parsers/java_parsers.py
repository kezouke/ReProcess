from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_java as tsjava


class JavaFileParser(TreeSitterFileParser):
    """
    Concrete implementation of TreeSitterFileParser for parsing Java files.
    
    Inherits from TreeSitterFileParser and overrides methods to parse Java files specifically.
    """

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        """
        Initializes the Tree-sitter parser with the Java language grammar.
        
        Reads the file content and parses it into an AST. Also adjusts the file path relative to the repository.
        """
        cutted_path = self.file_path.split(self.repo_name)[-1]

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
        """
        Recursively finds component names within the AST starting from the given node.
        
        Args:
            node: The current AST node being processed.
            class_path: The path of the class currently being processed.
            
        Returns:
            List[str]: List of component names found.
        """
        components = []

        # If the node is a class declaration, extract the class name
        if node.type == 'class_declaration':
            class_name = self._node_text(node.child_by_field_name('name'))
            full_class_name = f"{class_path}.{class_name}" if class_path else class_name
            components.append(full_class_name)

            # Recursively extract nested classes and methods
            class_body = node.child_by_field_name('body')
            for child in class_body.children:
                components.extend(self._find_cmp_names(child, full_class_name))

        # If the node is a method declaration, extract the method name
        elif node.type == 'method_declaration':
            method_name = self._node_text(node.child_by_field_name('name'))
            full_method_name = f"{class_path}.{method_name}" if class_path else method_name
            components.append(full_method_name)

        # Recursively process children nodes, but only if we're not already inside a class or method
        for child in node.children:
            if node.type not in ['class_declaration', 'method_declaration']:
                components.extend(self._find_cmp_names(child, class_path))

        return components

    def extract_component_names(self):
        """
        Extracts names of components (classes and methods) defined in the Java file.
        
        Returns:
            List[str]: List of component names.
        """
        root_node = self.tree.root_node
        components = self._find_cmp_names(root_node)
        return [self.packages + "." + cmp_name for cmp_name in components]

    def _map_imported_classes(self):
        """
        Maps imported classes to their fully qualified names based on import statements.
        
        Returns:
            dict: Mapping of class names to their fully qualified names.
        """
        imports = self.extract_imports()
        imports_map = {imp.split('.')[-1]: imp for imp in imports}
        return imports_map

    def _rec_called_components_finder(self, node):
        """
        Recursively extracts names of components called within the Java file starting from the given node.
        
        Args:
            node: The current AST node being processed.
            
        Returns:
            List[str]: List of names of called components.
        """
        components = []

        # Handle object creation expressions (e.g., new ClassName())
        if node.type == "object_creation_expression":
            class_name_node = node.child_by_field_name("type")
            if class_name_node:
                class_name = self._node_text(class_name_node)
                parent = node.parent
                if parent and parent.type == "variable_declarator":
                    variable_name_node = parent.child_by_field_name("name")
                    if variable_name_node:
                        variable_name = self._node_text(variable_name_node)
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
                method_name = self._node_text(method_name_node)
                object_name = self._node_text(object_node)

                # Check if the object name is a variable mapped to a class
                class_name = self.variable_class_map.get(
                    object_name, object_name)
                full_class_name = self._get_fully_qualified_name(class_name)
                components.append(f"{full_class_name}.{method_name}")

        # Recursively process children nodes
        for child in node.children:
            components.extend(self._rec_called_components_finder(child))

        return components

    def _get_fully_qualified_name(self, class_name):
        """
        Retrieves the fully qualified name of a given class.
        
        Args:
            class_name: The simple name of the class.
            
        Returns:
            str: The fully qualified name of the class.
        """
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
        """
        Extracts names of components called within the Java file.
        
        Returns:
            List[str]: List of names of called components.
        """
        return list(
            set(self._rec_called_components_finder(self.tree.root_node)))

    def extract_callable_components(self):
        """
        Extracts names of callable components defined within the Java file.
        
        Returns:
            List[str]: List of names of callable components.
        """
        return self.local_component_names

    def _rec_import_finder(self, node):
        """
        Recursively finds import statements within the AST starting from the given node.
        
        Args:
            node: The current AST node being processed.
            
        Returns:
            List[str]: List of import statements found.
        """
        imports = []
        for child in node.children:
            if child.type == "import_declaration":
                for grandchild in child.children:
                    if grandchild.type == "scoped_identifier":
                        imports.append(self._node_text(grandchild))
                        break
            elif child.type == "program":
                imports.extend(self._rec_import_finder(child))

        return imports

    def extract_imports(self):
        """
        Extracts import statements from the Java file.
        
        Returns:
            List[str]: List of import statements found in the file.
        """
        root_node = self.tree.root_node
        return self._rec_import_finder(root_node)

    def _node_text(self, node):
        """
        Extracts the text content of a given AST node.
        
        Args:
            node: The AST node whose text content is to be extracted.
            
        Returns:
            str: The text content of the node.
        """
        return node.text.decode('utf-8').strip()


class JavaComponentFillerHelper(TreeSitterComponentFillerHelper):
    """
    Helper class for extracting Java component code using Tree-sitter.
    
    Extends TreeSitterComponentFillerHelper to provide functionality specific to Java.
    """

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        """
        Extracts the code of the specified Java component along with its required imports.
        
        Returns:
            str: The extracted code of the component including necessary imports.
        """
        component_name_splitted = self.component_name.split(
            self.file_parser.packages)[-1].split(".")[1:]
        self.imports = self._get_import_statements()

        self.component_node = self._find_component_node(
            self.file_parser.tree.root_node, component_name_splitted)

        if self.component_node:
            used_imports = self._get_used_imports(self.component_node)
            component_code = self._node_to_code_string(self.component_node)
            return "\n".join(used_imports) + "\n\n" + component_code
        return ""

    def _get_import_statements(self):
        """
        Extracts all import statements from the Java file.
        
        Returns:
            List[str]: List of import statements found in the file.
        """
        return [
            self._node_text(child)
            for child in self.file_parser.tree.root_node.children
            if child.type == "import_declaration"
        ]

    def _get_used_imports(self, component_node):
        """
        Identifies and returns imports used within the specified component node.
        
        Args:
            component_node: The AST node representing the component.
            
        Returns:
            List[str]: Sorted list of imports used by the component.
        """
        used_imports = set()
        called_components = self.file_parser._rec_called_components_finder(
            component_node)
        for component in called_components:
            for imp in self.imports:
                if imp.endswith(component.split(".")[-1] + ";"):
                    used_imports.add(imp)
        return sorted(used_imports)

    def _find_component_node(self, node, name_parts):
        """
        Recursively finds the AST node corresponding to the specified component.
        
        Args:
            node: The current AST node being processed.
            name_parts: List of component names to match against.
            
        Returns:
            Optional[ts.Node]: The AST node representing the component, or None if not found.
        """
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

    def _node_to_code_string(self, node):
        """
        Extracts the source code corresponding to the given AST node.
        
        Args:
            node: The AST node whose source code is to be extracted.
            
        Returns:
            str: The extracted source code with original indentation preserved.
        """
        # Extract code from the node, maintaining the original tabulation
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        code_lines = self.source_code[start_line:end_line + 1]

        # Return the code with correct indentation
        return "\n".join(code_lines)

    def _node_text(self, node):
        """
        Extracts the text content of a given AST node.
        
        Args:
            node: The AST node whose text content is to be extracted.
            
        Returns:
            str: The text content of the node.
        """
        return node.text.decode('utf-8').strip()

    def extract_callable_objects(self):
        """
        Extracts names of callable objects defined within the component code.
        
        Returns:
            List[str]: List of names of callable objects.
        """
        return list(
            set(
                self.file_parser._rec_called_components_finder(
                    self.component_node)))
