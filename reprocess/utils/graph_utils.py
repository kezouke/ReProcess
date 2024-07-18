import uuid
import hashlib
from reprocess.code_component import CodeComponentContainer
from reprocess.parsers.tree_sitter_parser import TreeSitterComponentFillerHelper
from reprocess.file_analyzer import FileContainer
from reprocess.parsers.python_parsers import PythonFileParser, PythonComponentFillerHelper
from typing import List


def create_parsers_map(python_files, repo_name):
    """Creates a map of Python file parsers."""
    return {file: PythonFileParser(file, repo_name) for file in python_files}


def extract_components(python_parsers_map):
    """Extracts component names and fillers from the parsers."""
    component_names = []
    component_fillers = {}
    for file, parser in python_parsers_map.items():
        code_components_names = parser.extract_component_names()
        component_names.extend(code_components_names)
        for cmp in code_components_names:
            component_fillers[cmp] = PythonComponentFillerHelper(
                cmp, file, parser)
    return component_names, component_fillers


def map_files_to_ids(python_parsers_map):
    """Maps files to their respective IDs."""
    id_files_map = {}
    for file in python_parsers_map.values():
        id_files_map[file.file_id] = FileContainer(
            file_id=file.file_id,
            file_path=file.file_path,
            imports=file.extract_imports(),
            called_components=file.extract_called_components(),
            callable_components=file.extract_callable_components(),
        )
    return id_files_map


def construct_code_components(
        component_filler_helpers: List[TreeSitterComponentFillerHelper]):
    """Constructs code components from component filler helpers."""
    code_components = []
    for helper in component_filler_helpers:
        component = CodeComponentContainer(
            component_id=helper.component_id,
            component_name=helper.component_name,
            component_code=helper.component_code,
            linked_component_ids=[],
            external_component_ids=[],
            file_id=helper.file_id,
            called_objects=helper.extract_callable_objects(),
            component_type=helper.component_type)
        code_components.append(component)

    # Compute hashes for components and update IDs
    for component in code_components:
        hash_id = hashlib.sha256(
            (component.component_name +
             component.getComponentAttribute('component_code')
             ).encode('utf-8')).hexdigest()
        component.setComponentAttribute('component_id', hash_id)

    return code_components


def link_components(code_components, component_id_map,
                    package_components_names):
    """Links components and identifies external components."""
    external_components_dict = {}
    all_internal_components = set(package_components_names)

    for component in code_components:
        component_imports = set(component.called_objects)
        linked_components = all_internal_components.intersection(
            component_imports)
        external_components = component_imports.difference(linked_components)

        for linked_component in linked_components:
            component.linked_component_ids.append(
                component_id_map[linked_component])

        for external_component in external_components:
            if external_component not in external_components_dict:
                external_components_dict[external_component] = str(
                    uuid.uuid4())
            component.external_component_ids.append(
                external_components_dict[external_component])

    return external_components_dict
