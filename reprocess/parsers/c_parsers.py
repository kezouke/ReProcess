from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from typing import List
import tree_sitter_c as tsc
from tree_sitter import Language, Parser

CHUNK_QUERY = """
    [
        (struct_specifier
            body: (field_declaration_list)) @struct
        (enum_specifier
            body: (enumerator_list)) @enum
        (union_specifier
            body: (field_declaration_list)) @union
        (function_definition) @function
    ]
""".strip()


class CFileParser(TreeSitterFileParser):
    """
    Concrete implementation of TreeSitterFileParser for parsing C files.
    
    Inherits from TreeSitterFileParser and overrides methods to parse C files specifically.
    """

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        """Initializes the Tree-sitter parser with the C language grammar."""
        # Load the compiled language grammar for C
        C_LANGUAGE = Language(tsc.language())
        self.parser = Parser(C_LANGUAGE)

        # Read the file content and parse it
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        # Adjust the file path relative to the repository
        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.file_path = cutted_path[1:]

    def extract_component_names(self):
        """
        Extracts names of components (functions, structs) and variables defined in the C file.
        
        Returns:
            List[str]: List of component names and variables.
        """
        components = []
        variables = []

        def visit_node(node):
            """Visits a node in the AST and extracts component names and variables."""
            # Extract function names
            if node.type == "function_definition":
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node:
                    func_name = func_node.text.decode('utf-8')
                    components.append(func_name)

            # Extract struct names and fields
            elif node.type == "struct_specifier":
                struct_node = node.child_by_field_name("name")
                if struct_node:
                    struct_name = struct_node.text.decode("utf-8")
                else:
                    struct_name = 'typedef'
                components.append(struct_name)
                body = node.child_by_field_name("body")
                if body:
                    for struct_node in body.children:
                        if struct_node.type == "field_declaration":
                            field_name = struct_node.child_by_field_name(
                                "declarator").text.decode('utf-8')
                            components.append(f"{struct_name}.{field_name}")

            # Extract variables (using the logic from the previous code)
            if node.type == 'init_declarator':  # Variable declaration with initialization
                declarator = node.child_by_field_name('declarator')
                if declarator:
                    variable_name = declarator.text.decode('utf8')
                    variables.append(variable_name)
            elif node.type == 'declarator' and node.parent.type != 'function_declarator':  # General variable declarator
                variable_name = node.text.decode('utf8')
                variables.append(variable_name)
            elif node.type == 'parameter_declaration':  # Function parameters
                declarator = node.child_by_field_name('declarator')
                if declarator:
                    variable_name = declarator.text.decode('utf8')
                    variables.append(variable_name)

        def traverse_tree(node):
            """Recursively traverses the AST starting from the given node."""
            visit_node(node)
            for child in node.children:
                traverse_tree(child)

        # Start traversal from the root node
        traverse_tree(self.tree.root_node)

        # Replace hyphens with underscores for component names
        modules = [component.replace("-", "_") for component in components]

        # Combine components and variables
        all_identifiers = modules + variables

        return all_identifiers

    def extract_called_components(self) -> List[str]:
        """
        Extracts names of components called within the C file.
        
        Returns:
            List[str]: List of names of called components.
        """
        called_components = set()

        def visit_node(node):
            """Visits a node in the AST and identifies called components."""
            if node.type == "call_expression":
                func_node = node.child_by_field_name("function")
                if func_node:
                    called_components.add(func_node.text.decode('utf-8'))
            elif node.type == "field_expression":
                field_node = node.child_by_field_name("field")
                if field_node:
                    called_components.add(field_node.text.decode('utf-8'))

        def traverse_tree(node):
            """Recursively traverses the AST starting from the given node."""
            visit_node(node)
            for child in node.children:
                traverse_tree(child)

        traverse_tree(self.tree.root_node)

        return list(called_components)

    def extract_callable_components(self):
        """
        Extracts names of callable components defined in the C file.
        
        Returns:
            List[str]: List of names of callable components.
        """
        callable_components = set()

        def visit_node(node):
            if node.type == "function_definition":
                func_node = node.child_by_field_name(
                    "declarator").child_by_field_name("declarator")
                if func_node:
                    func_name = func_node.text.decode('utf-8')
                    callable_components.add(func_name)
            elif node.type == "struct_specifier":
                struct_node = node.child_by_field_name("name")
                if struct_node:
                    struct_name = struct_node.text.decode('utf-8')
                else:
                    struct_name = 'typedef'
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
        """
        Extracts import statements from the C file.
        
        Returns:
            List[str]: List of import statements found in the file.
        """
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
    """
    Concrete implementation of TreeSitterComponentFillerHelper for filling component details in C files.
    
    Inherits from TreeSitterComponentFillerHelper and overrides methods to fill component details specifically for C files.
    """

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: 'TreeSitterFileParser') -> None:

        self.struct_variable_types = {
        }  # Dictionary to store variable to struct type mappings
        self.current_scope = []
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        """
        Extracts the code of the specified component from the C file.
        
        Returns:
            str: The extracted code of the component.
        """

        def extract_imports_from_source():
            """Extracts import statements from the source code."""
            imports = []
            for node in self.file_parser.tree.root_node.children:
                if node.type == "preproc_include":
                    include_node = node.child_by_field_name("path")
                    if include_node:
                        imports.append(
                            self.file_parser.source_code[node.start_byte:node.
                                                         end_byte])
            return imports

        imports_code = "".join(extract_imports_from_source())

        code = self._extract_code_without_imports()
        return imports_code + "\n" + code

    def extract_callable_objects(self):
        """
        Extracts callable objects defined within the component.
        
        Returns:
            List[str]: List of callable object names.
        """
        code = self.extract_component_code()
        tree = self.file_parser.parser.parse(bytes(code, "utf8"))
        called_components = set()

        def _extract_components(node, components, struct_vars):
            """Recursively extracts callable objects from the AST."""
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
                struct_node = node.child(0).child_by_field_name('name')
                if struct_node:
                    struct_name = struct_node.text.decode('utf-8')
                else:
                    struct_name = 'typedef'
                var_name = node.child(1).text.decode('utf-8')
                struct_vars[var_name] = struct_name
            # Recursively go through all child nodes
            for child in node.children:
                _extract_components(child, components, struct_vars)

        root_node = tree.root_node
        struct_vars = {}
        _extract_components(root_node, called_components, struct_vars)
        return list(called_components)

    def _extract_code_without_imports(self):

        component_name_splitted = self.component_name.split(".")

        def visit_node(node):
            """Visits a node in the AST and checks if it matches the specified component."""
            # Check if the node is a function definition
            if node.type == "function_definition" and node.child_by_field_name("declarator"):
                self.component_type = "function"
                func_node = node.child_by_field_name("declarator").child_by_field_name("declarator")
                if func_node and func_node.text.decode('utf-8') == component_name_splitted[0]:
                    return node

            # Check if the node is a struct
            elif node.type == "struct_specifier" and node.child_by_field_name("name"):
                struct_name = node.child_by_field_name("name").text.decode('utf-8')
                if struct_name == component_name_splitted[0]:
                    self.component_type = "structure"
                    return node

            # Check if the node is a variable declaration
            elif node.type == "init_declarator":  # Variable declaration with initialization
                declarator = node.child_by_field_name('declarator')
                if declarator and declarator.text.decode('utf8') == component_name_splitted[0]:
                    self.component_type = "variable"
                    return node
            elif node.type == "declarator" and node.parent.type != "function_declarator":  # General variable declarator
                if node.text.decode('utf8') == component_name_splitted[0]:
                    self.component_type = "variable"
                    return node

        def traverse_tree(node):
            """Recursively traverses the AST to find the specified component."""
            result_node = visit_node(node)
            if result_node:
                return result_node
            for child in node.children:
                result_node = traverse_tree(child)
                if result_node:
                    return result_node

        root_node = self.file_parser.tree.root_node
        found_node = traverse_tree(root_node)
        
        if found_node:
            extracted_code = self.file_parser.source_code[found_node.start_byte:found_node.end_byte]
            
            # Handle struct fields if necessary
            if self.component_type == "structure" and len(component_name_splitted) > 1:
                self.component_type = "structure_field"
                field_name = component_name_splitted[1]
                field_code = self._extract_field_code(found_node, field_name)
                if field_code:
                    return f"struct {component_name_splitted[0]} {{\n{field_code}\n}}"
            
            return extracted_code
        return ""

    def _extract_field_code(self, struct_node, field_name):
        """
        Extracts the code of a specific field within a structure.
        
        Args:
            struct_node (Node): The AST node representing the structure.
            field_name (str): The name of the field to extract.
        
        Returns:
            str: The extracted code of the field, or an empty string if not found.
        """
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

    def extract_signature(self):
        C_LANGUAGE = Language(tsc.language())
        parser = Parser(C_LANGUAGE)
        query = C_LANGUAGE.query(CHUNK_QUERY)
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
