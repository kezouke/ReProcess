from reprocess.re_processors.processor import ReProcessor
from reprocess.utils.find_code_files import find_code_files
from reprocess.re_container import ReContainer
from reprocess.utils.graph_utils import construct_code_components, link_components, create_parsers_map, extract_components, map_files_to_ids, get_residual_cmp


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
            dict: Contains code components, files, and external components.
        """
        if not repository_container.not_empty:
            return {}

        files = find_code_files(repository_container.repo_path)
        parsers_map = create_parsers_map(files, repository_container.repo_name)

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

        file_cmp_map = {}
        files = list(id_files_map.values())
        for cmp in code_components:
            file_cmp_map.setdefault(cmp.file_id, []).append(cmp)
        residual_components = get_residual_cmp(files, file_cmp_map,
                                               repository_container.repo_path)

        return {
            "code_components": code_components + residual_components,
            "files": files,
            "external_components": external_components_dict
        }
