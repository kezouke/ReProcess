import uuid
import hashlib
from code_dependency_grapher.cdg.CodeComponent import CodeComponent
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapper
from code_dependency_grapher.utils.mappers.IdComponentMapper import IdComponentMapper
from code_dependency_grapher.utils.mappers.IdFileAnalyzerMapper import IdFileAnalyzerMapper
from code_dependency_grapher.utils.find_components import extract_components_from_files
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.utils.find_python_files import find_python_files
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class GraphBuilder(RepositoryProcessor):
    """
    This class is responsible for building a directed acyclic graph (DAG) representing the structure and dependencies
    within a set of Python files. It analyzes the files to identify components and their relationships, then constructs
    a DAG using these components. The resulting graph is saved within a repository container for further processing or analysis.

    Attributes:
        - None

    Methods:
        process(repository_container: RepositoryContainer): Constructs the dependency graph and populates the given repository container with the constructed graph and associated data.
    """

    def __init__(self) -> None:
        super().__init__()

    def process(self, repository_container: RepositoryContainer):
        """
        Orchestrates the construction of a dependency graph from a set of Python files contained within a repository.

        Parameters:
            repository_container (RepositoryContainer): An instance of the RepositoryContainer class that will hold the constructed dependency graph and associated data.

        Returns:
            None
        """
        # Find all Python files within the repository
        python_files = find_python_files(repository_container.repo_path)

        # Map file paths to their abstract syntax trees (ASTs)
        ast_manager = FilePathAstMapper(repository_container.repo_path,
                                        python_files)

        # Extract components from the found Python files
        file_components_map, _, package_components_names = extract_components_from_files(
            python_files, repository_container.repo_path,
            ast_manager.file_path_ast_map)

        # Map component identifiers to their corresponding components
        id_component_manager = IdComponentMapper(
            repository_container.repo_path, file_components_map)

        # Analyze files to map them to their unique identifiers and other relevant data
        id_files_manager = IdFileAnalyzerMapper(python_files, ast_manager,
                                                package_components_names,
                                                repository_container.repo_path)

        # Initialize a list to hold the constructed code components
        code_components = []

        # Construct code components based on the identified components and their relationships
        for cmp_id in id_component_manager.id_component_map:
            code_components.append(
                CodeComponent(cmp_id, repository_container.repo_path,
                              id_files_manager, ast_manager.file_path_ast_map,
                              id_component_manager.id_component_map,
                              package_components_names))

        for cmp_to_hash in code_components:
            hashId = hashlib.sha256(
                cmp_to_hash.getComponentAttribute('component_code').encode(
                    'utf-8')).hexdigest()
            id_component_manager.component_id_map[
                cmp_to_hash.getComponentAttribute('component_name')] = hashId
            cmp_to_hash.setComponentAttribute('component_id', hashId)

        # Identify external components and link internal components based on imports
        external_components_dict = {}
        all_internal_components = set(package_components_names)
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
        repository_container.code_components = code_components
        repository_container.files = [
            value for _, value in id_files_manager.id_file_map.items()
        ]
        repository_container.external_components = external_components_dict
