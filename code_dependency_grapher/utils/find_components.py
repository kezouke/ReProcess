import ast
from typing import Dict
from .mappers.FilePathAstMapper import FilePathAstMapError


def extract_components(file_path,
                       file_path_ast_map: Dict[str, ast.Module]):
    
    if file_path_ast_map is None:
        raise FilePathAstMapError("file_path_ast_map is None")
    
    tree = file_path_ast_map[file_path]
    components = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef):
            components.append(node.name)

    return components


def extract_components_from_files(file_paths):
    file_components_map = {}
    components_names = []
    package_components_names = []
    
    for file_path in file_paths:
        components = extract_components(file_path)
        
        modules = [f"{packages}.{component}" for component in components]

        file_components_map[file_path] = components
        components_names.extend(components)
        package_components_names.extend(modules)

    return file_components_map, \
            components_names, \
            package_components_names