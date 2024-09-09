from reprocess.parsers.tree_sitter_parser import TreeSitterFileParser, TreeSitterComponentFillerHelper
from tree_sitter import Language, Parser
from reprocess.utils.import_path_extractor import get_import_statement_path
import tree_sitter_php as tsphp


class PhpFileParser(TreeSitterFileParser):

    def __init__(self, file_path: str, repo_name: str) -> None:
        super().__init__(file_path, repo_name)

    def _initialize_parser(self):
        """Initializes the Tree-sitter parser with the PHP language grammar."""
        PHP_LANGUAGE = Language(tsphp.language_php())
        self.parser = Parser(PHP_LANGUAGE)

        # Read the file content and parse it
        with open(self.file_path, 'r', encoding='utf-8') as file:
            self.source_code = file.read()
            self.tree = self.parser.parse(bytes(self.source_code, "utf8"))

        # Adjust the file path relative to the repository
        cutted_path = self.file_path.split(self.repo_name)[-1]
        self.packages = get_import_statement_path(
            cutted_path.replace(".php", ""))
        self.file_path = cutted_path[1:]

    def extract_component_names(self):
        """Extracts the names of all classes, methods, and functions in the PHP file."""
        class_stack = []  # Stack to maintain nested class hierarchy
        component_names = []

        def traverse(node):
            nonlocal class_stack, component_names

            # Check for class declarations
            if node.type == 'class_declaration':
                class_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                if class_stack:
                    full_class_name = f"{class_stack[-1]}.{class_name}"
                else:
                    full_class_name = class_name
                class_stack.append(full_class_name)
                component_names.append(full_class_name)

            # Check for method declarations within a class
            if node.type == 'method_declaration':
                method_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                if class_stack:
                    full_method_name = f"{class_stack[-1]}.{method_name}"
                    component_names.append(full_method_name)

            # Check for standalone functions
            if node.type == 'function_definition':
                function_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                component_names.append(function_name)

            # Recursively visit children of the current node
            for child in node.children:
                traverse(child)

            # Pop class stack when leaving a class scope
            if node.type == 'class_declaration':
                class_stack.pop()

        # Start traversal from the root node of the tree
        root_node = self.tree.root_node
        traverse(root_node)

        # Prepend package path to each component name
        component_names = [f"{self.packages}.{cmp}" for cmp in component_names]

        return component_names

    def extract_callable_components(self):
        pass

    def extract_called_components(self):
        """Extracts all components inside the PHP file that are being called."""
        class_stack = []  # Stack to maintain class hierarchy
        variable_types = {}  # Dictionary to map variable names to their types
        called_components = []

        def resolve_variable_type(var_name):
            """Resolves the type of the variable by checking the variable_types dict."""
            return variable_types.get(var_name, var_name)

        def traverse(node, current_class=None):
            nonlocal class_stack, variable_types, called_components

            # Handle class declaration
            if node.type == 'class_declaration':
                class_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                class_stack.append(class_name)
                current_class = class_name

            # Handle method or function declaration
            if node.type == 'method_declaration' or node.type == 'function_definition':
                method_name = node.child_by_field_name('name').text.decode(
                    'utf-8')
                if current_class:
                    full_method_name = f"{current_class}.{method_name}"
                else:
                    full_method_name = method_name
                called_components.append(full_method_name)

                # Process parameters and map variable names to their types
                parameters = node.child_by_field_name('parameters')
                if parameters:
                    for param in parameters.named_children:
                        param_name_node = param.child_by_field_name('name')
                        param_type_node = param.child_by_field_name('type')
                        if param_name_node and param_type_node:
                            param_name = param_name_node.text.decode('utf-8')
                            param_type = param_type_node.text.decode('utf-8')
                            variable_types[param_name] = param_type

            # Handle variable assignment (e.g., $this->logger = $logger;)
            if node.type == 'assignment_expression':
                left = node.child_by_field_name('left')
                right = node.child_by_field_name('right')

                # Check if left side is a member access (e.g., $this->logger)
                if left and left.type == 'member_access_expression':
                    left_var = left.child_by_field_name('name').text.decode(
                        'utf-8')
                    if right and right.type == 'variable_name':
                        right_var = right.text.decode('utf-8')
                        variable_types[
                            f"$this->{left_var}"] = resolve_variable_type(
                                right_var)

            # Handle method call expressions (e.g., $this->logger->log())
            if node.type == 'member_call_expression':
                object_node = node.child_by_field_name('object')
                method_node = node.child_by_field_name('name')
                if object_node and method_node:
                    object_name = object_node.text.decode('utf-8')
                    method_name = method_node.text.decode('utf-8')
                    resolved_object = resolve_variable_type(object_name)
                    full_call = f"{resolved_object}.{method_name}"
                    called_components.append(full_call)

            # Handle object creation (e.g., $logger = new Logger();)
            if node.type == 'object_creation_expression':
                c = None
                for c in node.children:
                    if c.type == "name":
                        class_name_node = c
                variable_node = node.prev_named_sibling  # The variable being assigned
                if class_name_node and variable_node and variable_node.type == 'variable_name':
                    var_name = variable_node.text.decode('utf-8')
                    class_name = class_name_node.text.decode('utf-8')
                    called_components.append(f"{class_name}.__construct")
                    variable_types[var_name] = class_name

            # Traverse children
            for child in node.named_children:
                traverse(child, current_class)

            # Handle leaving a class scope
            if node.type == 'class_declaration':
                class_stack.pop()

        # Start traversal from the root node
        root_node = self.tree.root_node
        traverse(root_node)

        return list(set(called_components))

    def extract_imports(self):
        pass


class PhpComponentFillerHelper(TreeSitterComponentFillerHelper):

    def __init__(self, component_name: str, component_file_path: str,
                 file_parser: TreeSitterFileParser) -> None:
        super().__init__(component_name, component_file_path, file_parser)

    def extract_component_code(self):
        pass

    def extract_callable_objects(self):
        pass
