import uuid
import hashlib
from reprocess.code_component import CodeComponentFiller
from reprocess.utils.mappers.file_path_ast_mapper import FilePathAstMapper
from reprocess.utils.mappers.id_component_mapper import IdComponentMapper
from reprocess.utils.mappers.id_file_analyzer_mapper import IdFileAnalyzerMapper
from reprocess.utils.find_components import extract_components_from_files


def map_files_and_components(repo_path, python_files):
    # Map file paths to their abstract syntax trees (ASTs)
    ast_manager = FilePathAstMapper(repo_path, python_files)

    # Extract components from the found Python files
    file_components_map, _, package_components_names = extract_components_from_files(
        python_files, repo_path, ast_manager.file_path_ast_map)

    # Map component identifiers to their corresponding components
    id_component_manager = IdComponentMapper(repo_path, file_components_map)

    # Analyze files to map them to their unique identifiers and other relevant data
    id_files_manager = IdFileAnalyzerMapper(python_files, ast_manager,
                                            package_components_names,
                                            repo_path)

    return ast_manager, id_component_manager, id_files_manager, package_components_names


def construct_code_components(id_component_manager, id_files_manager,
                              ast_manager, package_components_names,
                              repo_path):
    code_components = []

    # Construct code components based on the identified components and their relationships
    for cmp_id in id_component_manager.id_component_map:
        code_components.append(
            CodeComponentFiller(cmp_id, repo_path, id_files_manager,
                                ast_manager.file_path_ast_map,
                                id_component_manager.id_component_map,
                                package_components_names))

    # Compute hashes for components and update IDs
    for cmp_to_hash in code_components:
        hash_id = hashlib.sha256(
            (cmp_to_hash.component_name +
             cmp_to_hash.getComponentAttribute('component_code')
             ).encode('utf-8')).hexdigest()
        id_component_manager.component_id_map[
            cmp_to_hash.getComponentAttribute('component_name')] = hash_id
        cmp_to_hash.setComponentAttribute('component_id', hash_id)

    return code_components


def link_components(code_components, id_component_manager,
                    package_components_names):
    external_components_dict = {}

    all_internal_components = set(package_components_names)
    for cmp in code_components:
        cmp_imports = set(cmp.extract_imports())
        linked_components = all_internal_components.intersection(cmp_imports)
        external_components = cmp_imports.difference(linked_components)

        for l_cmp in linked_components:
            l_cmp_id = id_component_manager.component_id_map[l_cmp]
            cmp.linked_component_ids.append(l_cmp_id)

        for e_cmp in external_components:
            e_id = external_components_dict.get(e_cmp, None)
            if e_id is None:
                e_id = str(uuid.uuid4())
                external_components_dict[e_cmp] = e_id
            cmp.external_component_ids.append(e_id)

    return external_components_dict
