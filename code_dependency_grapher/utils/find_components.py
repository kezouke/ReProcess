import ast
from typing import Dict, List, Tuple
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapError
from code_dependency_grapher.utils.import_path_extractor import get_import_statement_path

def extract_components(file_path: str,
                       file_path_ast_map: Dict[str, ast.Module]) -> List[str]:
    """
    Extracts the names of all ClassDef and FunctionDef components from a given file.
    
    Args:
        file_path (str): The path to the file to analyze.
        file_path_ast_map (Dict[str, ast.Module]): A dictionary mapping file paths to their corresponding AST Module objects.
    
    Raises:
        FilePathAstMapError: If file_path_ast_map is None.
    
    Returns:
        List[str]: A list of names of the components found in the file.
    """
    if file_path_ast_map is None:
        raise FilePathAstMapError("file_path_ast_map is None")
    
    tree = file_path_ast_map[file_path]
    components = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef):
            components.append(node.name)

    return components

def extract_components_from_files(file_paths: List[str],
                                  file_path_ast_map: Dict[str, ast.Module]) -> Tuple[Dict[str, List[str]], List[str], List[str]]:
    """
    Extracts components from multiple files and organizes them into different lists and dictionaries.
    
    Args:
        file_paths (List[str]): A list of file paths to analyze.
        file_path_ast_map (Dict[str, ast.Module]): A dictionary mapping file paths to their corresponding AST Module objects.
    
    Returns:
        Tuple[Dict[str, List[str]], List[str], List[str]]: A tuple containing:
            - A dictionary mapping each file path to a list of component names found in that file.
            - A list of all unique component names across all files.
            - A list of all unique component names prefixed with their package/module paths.
    """
    file_components_map = {}
    components_names = []
    package_components_names = []

    base_path = "data/repos/"

    for file_path in file_paths:
        components = extract_components(file_path, file_path_ast_map)
        cutted_path = file_path.split(base_path)[-1]
        packages = get_import_statement_path(cutted_path)
        modules = [f"{packages}.{component}" for component in components]

        file_components_map[file_path] = components
        components_names.extend(components)
        package_components_names.extend(modules)

    return file_components_map, components_names, package_components_names
