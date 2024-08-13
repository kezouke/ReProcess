import subprocess
import logging
from copy import deepcopy
from reprocess.re_processors.processor import ReProcessor
from reprocess.re_container import ReContainer
from reprocess.utils.graph_utils import construct_code_components, link_components, create_parsers_map, extract_components, map_files_to_ids


class GraphUpdater(ReProcessor):
    """
    A class responsible for updating the repository's dependency graph based on changes detected in the repository.

    This class inherits from RepositoryProcessor and implements a call method that takes a `RepositoryContainer` instance as input.
    It processes changes in files and components, updates the repository's structure accordingly, and constructs a new dependency graph.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initializes the GraphUpdater.
        """
        super().__init__()

    def _get_changed_files(self, local_repo_path: str) -> list:
        """
        Retrieves a list of files that have changed in the local repository since the last commit.

        Args:
            local_repo_path (str): Local path of the repository.

        Returns:
            list: A list of changed file paths.
        """
        try:
            result = subprocess.run([
                'git', '-C', local_repo_path, 'diff', '--cached',
                '--name-status'
            ],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            print(result.stdout)
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get changed files: {e}")
            return []

    def is_removed(self, changed_file_status: str) -> bool:
        """
        Checks if a file has been removed based on its status string.

        Args:
            changed_file_status (str): The status string of a file ('A' for added, 'M' for modified, 'D' for deleted).

        Returns:
            bool: True if the file has been removed, False otherwise.
        """
        return changed_file_status[0] == 'D'

    def _separate_file_changes(self, changed_files):
        """
        Separates changed files into removed and updated categories.

        Args:
            changed_files (list): List of changed files with their statuses.

        Returns:
            tuple: Lists of removed file paths and updated file paths.
        """
        status_file_name = [line.split('\t') for line in changed_files]
        removed_files_relative_paths = [
            line[1] for line in status_file_name if self.is_removed(line)
        ]
        updated_files_relative_paths = [
            line[1] for line in status_file_name if not self.is_removed(line)
        ]
        print(removed_files_relative_paths)
        print(updated_files_relative_paths)
        return removed_files_relative_paths, updated_files_relative_paths

    def _filter_repository_files(self, repository_container,
                                 removed_files_relative_paths,
                                 updated_files_relative_paths):
        """
        Filters the repository container's files based on removed and updated paths.

        Args:
            repository_container (ReContainer): The repository container instance.
            removed_files_relative_paths (list): List of removed file paths.
            updated_files_relative_paths (list): List of updated file paths.

        Returns:
            tuple: Lists of temporary files, removed file IDs, and updated file IDs.
        """
        removed_file_ids = []
        updated_files_ids = []
        for file in repository_container.files:
            if file.file_path in removed_files_relative_paths:
                removed_file_ids.append(file.file_id)
            elif file.file_path in updated_files_relative_paths:
                updated_files_ids.append(file.file_id)

        temporary_files = list(
            filter(
                lambda file: file.file_id not in removed_file_ids and file.
                file_id not in updated_files_ids, repository_container.files))
        return temporary_files, removed_file_ids, updated_files_ids

    def _filter_repository_components(self, repository_container,
                                      removed_file_ids, updated_files_ids):
        """
        Filters the repository container's code components based on removed and updated file IDs.

        Args:
            repository_container (ReContainer): The repository container instance.
            removed_file_ids (list): List of removed file IDs.
            updated_files_ids (list): List of updated file IDs.

        Returns:
            tuple: Lists of temporary code components, removed component IDs, and updated component IDs.
        """
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

        return temporary_code_components, removed_components_ids, updated_components_ids

    def _adjust_linked_component_ids(self, temporary_code_components,
                                     removed_components_ids,
                                     updated_components_ids):
        """
        Adjusts the linked component IDs in the temporary code components list.

        Args:
            temporary_code_components (list): List of temporary code components.
            removed_components_ids (list): List of removed component IDs.
            updated_components_ids (list): List of updated component IDs.
        """
        changed_components_ids = set(removed_components_ids +
                                     updated_components_ids)
        for code_component in temporary_code_components:
            code_component.linked_component_ids = set(
                code_component.linked_component_ids).difference(
                    changed_components_ids)

    def _process_updated_files(self, repository_container, updated_files):
        """
        Processes the updated files by mapping and constructing code components and linking them.

        Args:
            repository_container (ReContainer): The repository container instance.
            updated_files (list): List of updated file paths.

        Returns:
            tuple: Updated AST manager, component manager, file manager, package components, and external components dictionary.
        """
        parsers_map = create_parsers_map(updated_files,
                                         repository_container.repo_name)

        component_names, component_fillers = extract_components(parsers_map)
        code_components = construct_code_components(
            list(component_fillers.values()))
        component_id_map = {
            component.component_name: component.component_id
            for component in code_components
        }
        id_files_map = map_files_to_ids(parsers_map)
        external_components_dict = link_components(code_components,
                                                   component_id_map,
                                                   component_names)

        return id_files_map, external_components_dict, code_components

    def _merge_updated_with_existing(self, repository_container,
                                     temporary_files, new_files,
                                     temporary_code_components,
                                     new_code_components,
                                     external_components_dict):
        """
        Merges the updated components and files with the existing ones in the repository container.

        Args:
            repository_container (ReContainer): The repository container instance.
            temporary_files (list): List of temporary files.
            new_files (list): List of new files.
            temporary_code_components (list): List of temporary code components.
            new_code_components (list): List of new code components.
            external_components_dict (dict): Dictionary of external components.
        
        Returns:
            dict: Updated repository container content.
        """
        external_components_dict.update(
            repository_container.external_components)
        files = temporary_files + new_files
        code_components = temporary_code_components + new_code_components
        return {
            "external_components": external_components_dict,
            "code_components": code_components,
            "files": files
        }

    def __call__(self,
                 repository_container: ReContainer,
                 inplace: bool = True):
        """
        Updates the repository's dependency graph based on changes detected in the repository.

        Args:
            repository_container (ReContainer): The repository container holding the current state of the repository.
        """
        # Retrieve and process changed files
        changed_files = self._get_changed_files(repository_container.repo_path)
        removed_files_relative_paths, updated_files_relative_paths = self._separate_file_changes(
            changed_files)

        # Filter repository container's files and components
        temporary_files, removed_file_ids, updated_files_ids = self._filter_repository_files(
            repository_container, removed_files_relative_paths,
            updated_files_relative_paths)
        temporary_code_components, removed_components_ids, updated_components_ids = self._filter_repository_components(
            repository_container, removed_file_ids, updated_files_ids)

        # Adjust linked component IDs
        self._adjust_linked_component_ids(temporary_code_components,
                                          removed_components_ids,
                                          updated_components_ids)

        # Process updated files and update repository container
        updated_files = [
            repository_container.repo_path + "/" + path
            for path in updated_files_relative_paths
        ]

        id_files_map, external_components_dict, new_code_components = self._process_updated_files(
            repository_container, updated_files)

        # Construct code components for updated files
        new_files = list(id_files_map.values())
        new_code_components

        return self._merge_updated_with_existing(repository_container,
                                                 temporary_files, new_files,
                                                 temporary_code_components,
                                                 new_code_components,
                                                 external_components_dict)
