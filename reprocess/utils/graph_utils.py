import uuid
import hashlib
import multiprocessing as mp
import logging
import traceback
import os
from reprocess.code_component import CodeComponentContainer
from reprocess.parsers.tree_sitter_parser import TreeSitterComponentFillerHelper
from reprocess.file_analyzer import FileContainer
from reprocess.parsers.python_parsers import PythonFileParser, PythonComponentFillerHelper
from reprocess.parsers.c_parsers import CFileParser, CComponentFillerHelper
from reprocess.parsers.cpp_parsers import CppFileParser, CppComponentFillerHelper
from reprocess.parsers.java_parsers import JavaFileParser, JavaComponentFillerHelper
from reprocess.parsers.go_parsers import GoFileParser, GoComponentFillerHelper
from reprocess.parsers.java_script_parsers import JavaScriptFileParser, JavaScriptComponentFillerHelper
from reprocess.parsers.typescript_parser import TypeScriptFileParser, TypeScriptComponentFillerHelper
from typing import List

#TODO: Add custom way for logs
log_file_name = 'logs.txt'
log_file_path = os.path.join(os.getcwd(), log_file_name)

logging.basicConfig(
    filename=log_file_name,          # Log file
    level=logging.ERROR,          # Log only errors and above
    format='%(asctime)s - %(levelname)s - %(message)s\n'
)
logger = logging.getLogger(__name__)



def create_parsers_map(files, repo_name):
    """Creates a map of file parsers based on file extension."""
    parsers_map = {}
    for file in files:
        if file.endswith('.py'):
            parsers_map[file] = PythonFileParser(file, repo_name)
        elif file.endswith('.c'):
            parsers_map[file] = CFileParser(file, repo_name)
        elif file.endswith('.cpp'):
            parsers_map[file] = CppFileParser(file, repo_name)
        elif file.endswith('.java'):
            parsers_map[file] = JavaFileParser(file, repo_name)
        elif file.endswith('.go'):
            parsers_map[file] = GoFileParser(file, repo_name)
        elif file.endswith('.js'):
            parsers_map[file] = JavaScriptFileParser(file, repo_name)
        elif file.endswith('.ts'):
            parsers_map[file] = TypeScriptFileParser(file, repo_name)
    return parsers_map


def extract_components(parsers_map):
    """Extracts component names and fillers from the parsers."""
    component_names = []
    component_fillers = {}
    for file, parser in parsers_map.items():
        try:
            code_components_names = parser.extract_component_names()
            component_names.extend(code_components_names)
            for cmp in code_components_names:
                try:
                    if file.endswith('.py'):
                        component_fillers[cmp] = PythonComponentFillerHelper(cmp, file, parser)
                    elif file.endswith('.c'):
                        component_fillers[cmp] = CComponentFillerHelper(cmp, file, parser)
                    elif file.endswith('.cpp'):
                        component_fillers[cmp] = CppComponentFillerHelper(cmp, file, parser)
                    elif file.endswith('.java'):
                        component_fillers[cmp] = JavaComponentFillerHelper(cmp, file, parser)
                    elif file.endswith('.go'):
                        component_fillers[cmp] = GoComponentFillerHelper(cmp, file, parser)
                    elif file.endswith('.js'):
                        component_fillers[cmp] = JavaScriptComponentFillerHelper(cmp, file, parser)
                    elif file.endswith('.ts'):
                        component_fillers[cmp] = TypeScriptComponentFillerHelper(cmp, file, parser)
                except Exception as e:
                    logger.exception(f"Error processing component '{cmp}' in file '{file}': {e}")
                    # Optionally, print the error to the console for immediate feedback
                    print(f"Error processing component '{cmp}' in file '{file}': {e}. Check {log_file_path} for details.")
        except Exception as e:
            logger.exception(f"Error extracting components from file '{file}': {e}")
            # Optionally, print the error to the console for immediate feedback
            print(f"Error extracting components from file '{file}': {e}. Check {log_file_path} for details.")
    return component_names, component_fillers


def map_files_to_ids(parsers_map):
    """Maps files to their respective IDs."""
    id_files_map = {}
    for file in parsers_map.values():
        try:
            id_files_map[file.file_id] = FileContainer(
                file_id=file.file_id,
                file_path=file.file_path,
                imports=file.extract_imports(),
                called_components=file.extract_called_components(),
                callable_components=file.extract_callable_components(),
                code_formatted=file.code_formatted
            )
        except Exception as e:
            logger.exception(f"Error extracting components from file '{file}': {e}")
            # Optionally, print the error to the console for immediate feedback
            print(f"Error while mapping file to ids '{file.file_path}': {e}. Check {log_file_path} for details.")
    return id_files_map


def get_residual_cmp(files, file_cmp_map, repo_path):

    def normalize_code(code):
        code = code.replace("'", "").replace('"', "").replace('\\', '').replace(' ', '')
        code = "\n".join(line.strip() for line in code.splitlines() if line.strip())
        return code

    residuals = []
    for file in files:
        code = file.code_formatted
        file_lines = code.splitlines()

        if file.file_id in file_cmp_map:
            all_cmp_lines = []
            for cmp in file_cmp_map[file.file_id]:
                component_code = cmp.component_code
                normalized_component_code = normalize_code(component_code)
                all_cmp_lines.extend(normalized_component_code.splitlines())

            file_lines = [line for line in file_lines if normalize_code(line) not in all_cmp_lines]

        cleaned_code = "\n".join([line for line in file_lines if line.strip()])

        residual_name = f"file_{file.file_id}_residual"
        residual_id = hashlib.sha256((residual_name + cleaned_code).encode('utf-8')).hexdigest()
        residual_cmp = CodeComponentContainer(
            component_id=residual_id,
            component_name=residual_name,
            component_code=cleaned_code,
            linked_component_ids=[],
            external_component_ids=[],
            file_id=file.file_id,
            called_objects=[],
            component_type="residual"
        )
        residuals.append(residual_cmp)
    return residuals


def construct_code_components_worker(helper_data):
    """Constructs code components from simplified helper data."""
    component_id, component_name, component_code, file_id, component_type, callable_objects = helper_data

    component = CodeComponentContainer(
        component_id=component_id,
        component_name=component_name,
        component_code=component_code,
        linked_component_ids=[],
        external_component_ids=[],
        file_id=file_id,
        called_objects=callable_objects,
        component_type=component_type
    )
    return component


def construct_code_components(component_filler_helpers: List[TreeSitterComponentFillerHelper]):
    """Constructs code components from component filler helpers in parallel."""
    simplified_helper_data = [
        (
            helper.component_id,
            helper.component_name,
            helper.component_code,
            helper.file_id,
            helper.component_type,
            helper.extract_callable_objects()
        )
        for helper in component_filler_helpers
    ]

    with mp.Pool(processes=mp.cpu_count()) as pool:
        code_components = pool.map(construct_code_components_worker, simplified_helper_data)

    for component in code_components:
        hash_id = hashlib.sha256((component.component_name + component.getComponentAttribute('component_code')).encode('utf-8')).hexdigest()
        component.setComponentAttribute('component_id', hash_id)

    return code_components


def link_components(code_components, component_id_map, package_components_names):
    """Links components and identifies external components."""
    external_components_dict = {}
    all_internal_components = set(package_components_names)

    for component in code_components:
        component_imports = set(component.called_objects)
        linked_components = all_internal_components.intersection(component_imports)
        external_components = component_imports.difference(linked_components)

        for linked_component in linked_components:
            component.linked_component_ids.append(component_id_map[linked_component])

        for external_component in external_components:
            if external_component not in external_components_dict:
                external_components_dict[external_component] = str(uuid.uuid4())
            component.external_component_ids.append(external_components_dict[external_component])

    return external_components_dict