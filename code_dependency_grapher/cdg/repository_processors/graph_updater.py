import uuid
import hashlib
from copy import deepcopy
from code_dependency_grapher.cdg.requests_handling.RepositoryManager import RepositoryManager
from code_dependency_grapher.cdg.CodeComponent import CodeComponentFiller
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapper
from code_dependency_grapher.utils.mappers.IdComponentMapper import IdComponentMapper
from code_dependency_grapher.utils.mappers.IdFileAnalyzerMapper import IdFileAnalyzerMapper
from code_dependency_grapher.utils.find_components import extract_components_from_files
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class GraphUpdater(RepositoryProcessor):
    """
    A class responsible for updating the repository's dependency graph based on changes detected in the repository.
    
    This class inherits from RepositoryProcessor and implements a call method that takes a `RepositoryContainer` instance as input.
    It processes changes in files and components, updates the repository's structure accordingly, and constructs a new dependency graph.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes the GraphUpdater.
        
        This constructor simply calls the superclass constructor.
        """
        super().__init__()

    def is_removed(self, changed_file_status: str):
        """
            Checks if a file has been removed based on its status string.
            
            :param changed_file_status: The status string of a file ('A' for added, 'M' for modified, 'D' for deleted).
            :return: True if the file has been removed, False otherwise.
            """
        return changed_file_status[0] == 'D'

    def __call__(self,
                 repository_container: RepositoryContainer,
                 inplace: bool = True):
        """
        Updates the repository's dependency graph based on changes detected in the repository.
        
        :param repository_container: The repository container holding the current state of the repository.
        """

        # Retrieve and process changed files
        changed_files = RepositoryManager(
            repository_directory=repository_container.repo_path,
            preprocess=False).get_changed_files(repository_container.repo_path)
        status_file_name = [line.split('\t') for line in changed_files]

        # Separate removed and updated files
        removed_files_relative_paths = [
            line[1] for line in status_file_name if self.is_removed(line)
        ]
        updated_files = [
            repository_container.repo_path + "/" + line[1]
            for line in status_file_name if not self.is_removed(line)
        ]
        updated_files_relative_paths = [
            line[1] for line in status_file_name if not self.is_removed(line)
        ]

        # Update the repository container's files list based on changes
        removed_file_ids = []
        updated_files_ids = []
        for file in repository_container.files:
            if file.file_path in removed_files_relative_paths:
                removed_file_ids.append(file.file_id)
            elif file.file_path in updated_files_relative_paths:
                updated_files_ids.append(file.file_id)

        temproral_files = list(
            filter(
                lambda file: file.file_id not in removed_file_ids and file.
                file_id not in updated_files_ids, repository_container.files))

        # Update the repository container's code components list based on changes
        removed_components_ids = []
        updated_components_ids = []
        for code_component in repository_container.code_components:
            if code_component.file_id in removed_file_ids:
                removed_components_ids.append(code_component.component_id)
            elif code_component.file_id in updated_files_ids:
                updated_components_ids.append(code_component.component_id)

        temporary_code_components = deepcopy(
            list(
                filter(
                    lambda code_component:
                    (code_component.component_id not in removed_components_ids
                     and code_component.component_id not in
                     updated_components_ids),
                    repository_container.code_components)))

        # Adjust linked component IDs based on changes
        changed_components_ids = set(removed_components_ids +
                                     updated_components_ids)
        for code_component in temporary_code_components:
            code_component.linked_component_ids = \
                set(code_component.linked_component_ids).difference(changed_components_ids)

        # Map file paths to their abstract syntax trees (ASTs)
        ast_manager = FilePathAstMapper(repository_container.repo_path,
                                        updated_files)

        # Extract components from the found Python files
        file_components_map, _, package_components_names = extract_components_from_files(
            updated_files, repository_container.repo_path,
            ast_manager.file_path_ast_map)

        # Map component identifiers to their corresponding components
        id_component_manager = IdComponentMapper(
            repository_container.repo_path, file_components_map)

        for code_component in temporary_code_components:
            id_component_manager.component_id_map[
                code_component.component_name] = code_component.component_id

        # Analyze files to map them to their unique identifiers and other relevant data
        id_files_manager = IdFileAnalyzerMapper(updated_files, ast_manager,
                                                package_components_names,
                                                repository_container.repo_path)

        # Initialize a list to hold the constructed code components
        code_components = []

        # Construct code components based on the identified components and their relationships
        for cmp_id in id_component_manager.id_component_map:
            code_components.append(
                CodeComponentFiller(cmp_id, repository_container.repo_path,
                                    id_files_manager,
                                    ast_manager.file_path_ast_map,
                                    id_component_manager.id_component_map,
                                    package_components_names))

        for cmp_to_hash in code_components:
            hashId = hashlib.sha256(
                (cmp_to_hash.component_name +
                 cmp_to_hash.getComponentAttribute('component_code')
                 ).encode('utf-8')).hexdigest()
            id_component_manager.component_id_map[
                cmp_to_hash.getComponentAttribute('component_name')] = hashId
            cmp_to_hash.setComponentAttribute('component_id', hashId)

        # Identify external components and link internal components based on imports
        external_components_dict = {
            v: k
            for k, v in repository_container.external_components.items()
        }

        all_packages = [
            cmp.component_name for cmp in temporary_code_components
        ]
        all_internal_components = set(package_components_names + all_packages)
        for cmp in code_components:
            cmp_imports = set(cmp.extract_imports())
            linked_components = all_internal_components.intersection(
                cmp_imports)
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

        # Populate the repository container with the constructed code components and files
        code_components = list(
            map(lambda c: c.get_code_component_container(), code_components))
        new_files = [
            value.get_file_container()
            for _, value in id_files_manager.id_file_map.items()
        ]
        external_components = {
            v: k
            for k, v in external_components_dict.items()
        }

        external_components.update(repository_container.external_components)    
        files = temproral_files + new_files
        code_components = temporary_code_components + code_components

        return {
            "external_components": external_components,
            "code_components": code_components,
            "files": files
        }
