from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_java as tsjava

CHUNK_QUERY = """
    [
        (class_declaration) @class
        (interface_declaration) @interface
        (enum_declaration) @enum
        (method_declaration) @method
    ]
""".strip()


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
        self.language = JAVA_LANGUAGE

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
        Recursively finds component names (classes, methods) and variables (global, local)
        within the AST starting from the given node.
        
        Args:
            node: The current AST node being processed.
            class_path: The path of the class currently being processed.
            
        Returns:
            List[str]: List of component names (classes, methods) and variable names (global, local).
        """
        components = []

        # If the node is a class declaration, extract the class name
        if node.type == 'class_declaration':
            class_name = self._node_text(node.child_by_field_name('name'))
            full_class_name = f"{class_path}.{class_name}" if class_path else class_name
            components.append(full_class_name)

            # Recursively extract nested classes, methods, and variables
            class_body = node.child_by_field_name('body')
            for child in class_body.children:
                components.extend(self._find_cmp_names(child, full_class_name))

        # If the node is a method declaration, extract the method name
        elif node.type == 'method_declaration':
            method_name = self._node_text(node.child_by_field_name('name'))
            full_method_name = f"{class_path}.{method_name}" if class_path else method_name
            components.append(full_method_name)

            # Check for local variables inside the method
            method_body = node.child_by_field_name('body')
            if method_body:
                for child in method_body.children:
                    if child.type == 'local_variable_declaration':
                        for var_child in child.children:
                            if var_child.type == 'variable_declarator':
                                var_name = self._node_text(
                                    var_child.child_by_field_name('name'))
                                components.append(
                                    f"{full_method_name}.{var_name}")

        # If the node is a field declaration, extract global (class-level) variables
        elif node.type == 'field_declaration':
            for child in node.children:
                if child.type == 'variable_declarator':
                    var_name = self._node_text(
                        child.child_by_field_name('name'))
                    components.append(f"{class_path}.{var_name}")

        # Recursively process children nodes
        for child in node.children:
            if node.type not in [
                    'class_declaration', 'method_declaration',
                    'field_declaration'
            ]:
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

        # Track class name for static method calls
        if node.type == "class_declaration":
            class_name_node = node.child_by_field_name("name")
            if class_name_node:
                self.current_class_name = self._node_text(class_name_node)

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

        # Handle method invocations (non-static and static)
        elif node.type == "method_invocation":
            method_name_node = node.child_by_field_name("name")
            object_node = node.child_by_field_name("object")

            if method_name_node:
                method_name = self._node_text(method_name_node)

                # Handle chained method calls like System.out.println
                if object_node and object_node.type == "field_access":
                    full_object_name = self._recursively_resolve_field_access(
                        object_node)
                    components.append(f"{full_object_name}.{method_name}")
                else:
                    # Handle static method calls (e.g., ClassName.method())
                    if object_node:
                        object_name = self._node_text(object_node)
                        class_name = self.variable_class_map.get(
                            object_name, object_name)
                        full_class_name = self._get_fully_qualified_name(
                            class_name)
                        components.append(f"{full_class_name}.{method_name}")
                    else:
                        # No explicit object, could be a static method call
                        if self.current_class_name:
                            class_name = self._get_fully_qualified_name(
                                self.current_class_name)
                            components.append(f"{class_name}.{method_name}")

        # Recursively process children nodes
        for child in node.children:
            components.extend(self._rec_called_components_finder(child))

        return components

    def _recursively_resolve_field_access(self, node):
        """
        Recursively resolves field_access nodes to handle chained calls like System.out.
        
        Args:
            node: The AST node representing a field access.
            
        Returns:
            str: The fully resolved field access as a single string.
        """
        parts = []
        while node and node.type == "field_access":
            field_name_node = node.child_by_field_name("field")
            object_node = node.child_by_field_name("object")
            if field_name_node:
                parts.insert(0, self._node_text(field_name_node))
            if object_node and object_node.type == "field_access":
                node = object_node  # Move up the chain
            else:
                if object_node:
                    parts.insert(0, self._node_text(object_node))
                break
        return ".".join(parts)

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
        else:
            raise Exception("Component was not found")

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
        Recursively finds the AST node corresponding to the specified component (class, method, or variable).
        
        Args:
            node: The current AST node being processed.
            name_parts: List of component names to match against.
                        Example: ['SampleClass', 'anotherMethod', 'variableName']
            
        Returns:
            Optional[ts.Node]: The AST node representing the component, or None if not found.
        """

        # Check if the current node is a class or method declaration
        if node.type in ["class_declaration", "method_declaration"]:
            node_name = self._node_text(node.child_by_field_name("name"))

            # If the name matches, continue searching for the next part in name_parts
            if node_name == name_parts[0]:
                self.component_type = "class" if node.type == "class_declaration" else "method"
                if len(name_parts) == 1:
                    return node  # Found the class or method
                else:
                    # Continue searching within the class or method body
                    body_node = node.child_by_field_name("body")
                    if body_node:
                        return self._find_component_node(
                            body_node, name_parts[1:])

        # Check if the current node is a field declaration (class-level/global variables)
        elif node.type == "field_declaration" and len(name_parts) == 1:
            for child in node.children:
                if child.type == "variable_declarator":
                    var_name = self._node_text(
                        child.child_by_field_name("name"))
                    if var_name == name_parts[0]:
                        self.component_type = "variable"
                        return child  # Found the class-level variable

        # Check if the current node is a method declaration and search for local variables
        elif node.type == "method_declaration" and len(name_parts) > 1:
            method_name = self._node_text(node.child_by_field_name("name"))
            if method_name == name_parts[0]:
                body_node = node.child_by_field_name("body")
                if body_node:
                    # Search for local variables in the method body
                    return self._find_component_node(body_node, name_parts[1:])

        # Check for local variable declarations in method body
        elif node.type == "local_variable_declaration" and len(
                name_parts) == 1:
            for child in node.children:
                if child.type == "variable_declarator":
                    var_name = self._node_text(
                        child.child_by_field_name("name"))
                    if var_name == name_parts[0]:
                        self.component_type = "variable"
                        return child  # Found the local variable

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
        lines = self.source_code.splitlines()
        code_lines = lines[start_line:end_line + 1]

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
        Extracts names of callable objects and variables defined within the component code.
        
        Returns:
            List[str]: List of names of callable objects and variables.
        """
        # Extract callable objects (method invocations, function calls, etc.)
        callable_objects = set(
            self.file_parser._rec_called_components_finder(
                self.component_node))

        # Extract variable references (identifiers) within the component node
        variables = set()
        self._extract_variables(self.component_node, variables)
        variables_sorted = set()
        for variable in variables:
            for cmp in self.file_parser.extract_component_names():
                if cmp.split(
                        ".")[-1] == variable and self.component_name != cmp:
                    variables_sorted.add(cmp)

        callable_objs = set()
        for cmp in callable_objects:
            if cmp != self.component_name:
                callable_objs.add(cmp)

        # Combine callable objects and variables into a single list
        return list(callable_objs.union(variables_sorted))

    def _extract_variables(self, node, variables):
        """
        Recursively finds variable references (identifiers) within the given node.

        Args:
            node: The current AST node being processed.
            variables: A set to collect found variable names.
        """
        if node.type == "identifier":
            # Assuming the identifier is not part of a method invocation
            variables.add(self._node_text(node))

        # Recursively search all child nodes for more variable references
        for child in node.children:
            self._extract_variables(child, variables)

    def extract_signature(self):
        JAVA_LANGUAGE = Language(tsjava.language())
        parser = Parser(JAVA_LANGUAGE)
        query = JAVA_LANGUAGE.query(CHUNK_QUERY)
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
