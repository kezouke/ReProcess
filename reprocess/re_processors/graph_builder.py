from reprocess.re_processors.processor import ReProcessor
from reprocess.utils.find_python_files import find_python_files
from reprocess.re_container import ReContainer
from reprocess.utils.graph_utils import map_files_and_components, construct_code_components, link_components


class GraphBuilder(ReProcessor):
    """
    This class is responsible for building a directed acyclic graph (DAG) representing the structure and dependencies
    within a set of Python files. It analyzes the files to identify components and their relationships, then constructs
    a DAG using these components. The resulting graph is saved within a repository container for further processing or analysis.

    Attributes:
        - None

    Methods:
        process(repository_container: RepositoryContainer): Constructs the dependency graph and populates the given repository container with the constructed graph and associated data.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__()

    def __call__(self, repository_container: ReContainer):
        """
        Orchestrates the construction of a dependency graph from a set of Python files contained within a repository.

        Parameters:
            repository_container (RepositoryContainer): An instance of the RepositoryContainer class that will hold the constructed dependency graph and associated data.

        Returns:
            None
        """
        if not repository_container.is_downloaded:
            return dict()

        # Find all Python files within the repository
        python_files = find_python_files(repository_container.repo_path)

        # Map file paths to their abstract syntax trees (ASTs)
        ast_manager, id_component_manager, id_files_manager, package_components_names = \
        map_files_and_components(repository_container.repo_path, python_files)

        # Construct code components
        code_components = construct_code_components(
            id_component_manager, id_files_manager, ast_manager,
            package_components_names, repository_container.repo_path)

        # Link components
        external_components_dict = link_components(code_components,
                                                   id_component_manager,
                                                   package_components_names)

        # Populate the repository container with the constructed code components and files
        code_components = list(
            map(lambda c: c.get_code_component_container(), code_components))
        files = [
            value.get_file_container()
            for _, value in id_files_manager.id_file_map.items()
        ]

        return {
            "code_components": code_components,
            "files": files,
            "external_components": external_components_dict
        }
