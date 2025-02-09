import ast
from typing import List, Optional, Dict
from dataclasses import dataclass
from reprocess.utils.import_path_extractor import get_import_statement_path


@dataclass
class FileContainer:
    """
    Encapsulates information about a specific Python file, including its unique identifier, path, imports, called components, and callable components.
    
    Attributes:
        file_id (str): Unique identifier for the file.
        file_path (str): Path to the file.
        imports (List[str]): List of imported modules or names.
        called_components (List[str]): List of components that are called within the file.
        callable_components (List[str]): List of components that can be called, including functions and classes.
    """

    def __init__(self, file_id: str, file_path: str, imports: List[str],
                 called_components: List[str], callable_components: List[str],
                 code_formatted: str) -> None:
        """
        Initializes a new instance of the FileContainer class.
        
        Parameters:
            file_id (str): Unique identifier for the file.
            file_path (str): Path to the file.
            imports (List[str]): List of imported modules or names.
            called_components (List[str]): List of components that are called within the file.
            callable_components (List[str]): List of components that can be called, including functions and classes.
        """
        self.file_id = file_id
        self.file_path = file_path
        self.imports = imports
        self.called_components = called_components
        self.callable_components = callable_components
        self.code_formatted = code_formatted

    def __str__(self) -> str:
        """Returns the file path as a string representation of the object."""
        return self.file_path

    def __hash__(self) -> int:
        """Returns the hash value of the file path."""
        return hash(self.file_path)

    def __eq__(self, other) -> bool:
        if isinstance(other, FileContainer):
            self_attrs = vars(self)
            other_attrs = vars(other)

            if self_attrs.keys() != other_attrs.keys():
                return False

            for key in self_attrs.keys():
                if key not in other_attrs or self_attrs[key] != other_attrs[
                        key]:
                    return False
            return True
        else:
            return False


class FileFiller:
    """
    Analyzes a Python file to extract various components such as imports, called components, and callable components.
    
    Attributes:
        file_id (str): Unique identifier for the file.
        file_path (str): Path to the file being analyzed.
        file_path_ast_map (Optional[Dict[str, ast.Module]]): Mapping of file paths to AST modules.
        imports (List[str]): List of imported modules or names.
        called_components (List[str]): List of components that are called within the file.
        callable_components (List[str]): List of components that can be called, including functions and classes.
    """

    def __init__(self,
                 file_id: str,
                 file_path: str,
                 repos_dir: str,
                 file_path_ast_map: Optional[Dict[str, ast.Module]] = None,
                 package_components_names: Optional[List[str]] = None,
                 imports: Optional[List[str]] = None,
                 called_components: Optional[List[str]] = None,
                 callable_components: Optional[List[str]] = None,
                 deparse: bool = False):
        """
        Initializes a new instance of the FileAnalyzer class.
        
        Args:
            file_id (str): Unique identifier for the file.
            file_path (str): Path to the file being analyzed.
            file_path_ast_map (Optional[Dict[str, ast.Module]], optional): Mapping of file paths to AST modules. Defaults to None.
            imports (Optional[List[str]], optional): List of imported modules or names. Defaults to None.
            called_components (Optional[List[str]], optional): List of components that are called within the file. Defaults to None.
            callable_components (Optional[List[str]], optional): List of components that can be called, including functions and classes. Defaults to None.
            deparse: Optional[bool] = False
        """
        self.file_id = file_id
        self.file_path = "/".join(
            file_path.split(f'{repos_dir}')[1].split("/")[1:])
        # print(f'original path: {self.file_path}')
        self.file_path_ast_map = file_path_ast_map
        self.package_components_names = package_components_names
        if deparse:
            self.imports = imports
            self.called_components = called_components
            self.callable_components = callable_components
        else:
            self.imports = self.extract_imports()
            self.called_components = self.extract_called_components()
            self.callable_components = self.extract_callable_components()

    def extract_imports(self):
        """
        Extracts and returns a list of imported modules or names from the file.
                
        Returns:
            List[str]: List of imported modules or names.
        """

        tree = self.file_path_ast_map[self.file_path]
        imports = []

        def handle_import_from(node):
            if node.names[0].name == '*':
                module = get_wildcard_module(node)
                for cmp in self.package_components_names:
                    if cmp.startswith(module):
                        imports.append(cmp.split(".")[-1])
            else:
                append_aliases(node)

        def get_wildcard_module(node):
            if node.level > 0:
                current_package = get_import_statement_path(self.file_path)
                splitted_package = current_package.split(".")
                del splitted_package[-node.level:]
                splitted_package.append(node.module)
                return '.'.join(splitted_package)
            return node.module

        def append_aliases(node):
            for alias in node.names:
                imports.append(alias.asname if alias.asname else alias.name)

        for node in tree.body:
            if isinstance(node, ast.Import):
                append_aliases(node)
            elif isinstance(node, ast.ImportFrom):
                handle_import_from(node)

        return imports

    def extract_called_components(self):
        """
        Extracts and returns a list of components that are called within the file.
        
        Returns:
            List[str]: List of called components.
        """
        tree = self.file_path_ast_map[self.file_path]

        called_components = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_components.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_components.add(node.func.attr)

        return list(called_components)

    def extract_callable_components(self):
        """
        Extracts and returns a list of components that can be called, including functions and classes.
        
        Returns:
            List[str]: List of callable components.
        """
        tree = self.file_path_ast_map[self.file_path]

        callable_components = set()

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                callable_components.add(node.name)
            elif isinstance(node, ast.ClassDef):
                callable_components.add(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                callable_components.add(node.name)

        return list(callable_components)

    def __str__(self) -> str:
        """Returns the file path as a string representation of the object."""
        return self.file_path

    def __hash__(self) -> int:
        """Returns the hash value of the file path."""
        return hash(self.file_path)

    def get_file_container(self) -> FileContainer:
        return FileContainer(self.file_id, self.file_path, self.imports,
                             self.called_components, self.callable_components)
