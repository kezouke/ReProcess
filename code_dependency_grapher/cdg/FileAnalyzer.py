import ast
from typing import List, Optional, Dict
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapError

class FileAnalyzer:
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
                 file_path_ast_map: Optional[Dict[str, ast.Module]] = None,
                 imports: Optional[List[str]]= None,
                 called_components: Optional[List[str]] = None,
                 callable_components: Optional[List[str]] = None):
        """
        Initializes a new instance of the FileAnalyzer class.
        
        Args:
            file_id (str): Unique identifier for the file.
            file_path (str): Path to the file being analyzed.
            file_path_ast_map (Optional[Dict[str, ast.Module]], optional): Mapping of file paths to AST modules. Defaults to None.
            imports (Optional[List[str]], optional): List of imported modules or names. Defaults to None.
            called_components (Optional[List[str]], optional): List of components that are called within the file. Defaults to None.
            callable_components (Optional[List[str]], optional): List of components that can be called, including functions and classes. Defaults to None.
        """
        self.file_id = file_id
        self.file_path = file_path
        self.file_path_ast_map = file_path_ast_map
        self.imports = imports or self.extract_imports()
        self.called_components = called_components or self.extract_called_components()
        self.callable_components = callable_components or self.extract_callable_components()

    def extract_imports(self):
        """
        Extracts and returns a list of imported modules or names from the file.
        
        Raises:
            FilePathAstMapError: If file_path_ast_map is None.
        
        Returns:
            List[str]: List of imported modules or names.
        """
        self._validate_ast_map()

        tree = self.file_path_ast_map[self.file_path]

        imports = []

        for node in tree.body:
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.asname is not None:
                        imports.append(alias.asname)
                    else:
                        imports.append(alias.name)
        return imports

    def extract_called_components(self):
        """
        Extracts and returns a list of components that are called within the file.
        
        Raises:
            FilePathAstMapError: If file_path_ast_map is None.
        
        Returns:
            List[str]: List of called components.
        """
        self._validate_ast_map()
        
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
        
        Raises:
            FilePathAstMapError: If file_path_ast_map is None.
        
        Returns:
            List[str]: List of callable components.
        """
        self._validate_ast_map()
        
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
    
    def _validate_ast_map(self):
        """
        Validates that the file_path_ast_map attribute is not None.
        
        Raises:
            FilePathAstMapError: If file_path_ast_map is None.
        """
        if self.file_path_ast_map is None:
            raise FilePathAstMapError("file_path_ast_map is None")

    def __str__(self) -> str:
        """Returns the file path as a string representation of the object."""
        return self.file_path
    
    def __hash__(self) -> int:
        """Returns the hash value of the file path."""
        return hash(self.file_path)
