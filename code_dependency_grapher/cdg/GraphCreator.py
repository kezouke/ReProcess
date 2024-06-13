import uuid
import hashlib
from code_dependency_grapher.cdg.CodeComponent import CodeComponent
from code_dependency_grapher.utils.mappers.FilePathAstMapper import FilePathAstMapper
from code_dependency_grapher.utils.mappers.IdComponentMapper import IdComponentMapper
from code_dependency_grapher.utils.mappers.IdFileAnalyzerMapper import IdFileAnalyzerMapper
from code_dependency_grapher.utils.find_components import extract_components_from_files


class GraphCreator:
    """
    Creates a dependency graph for a set of Python files.
    
    This class orchestrates the process of analyzing Python files to identify components,
    their relationships, and dependencies, ultimately constructing a directed acyclic graph
    (DAG) that represents the code's structure and interdependencies.
    """

    def __init__(self, python_files, repos_dir):
        """
        Initializes a new instance of the GraphCreator class.
        
        Args:
            python_files (list): A list of file paths to Python files that should be analyzed.
        """
        self.python_files = python_files  # Store the list of Python files to analyze
        self.repos_dir = repos_dir

    def create_from_scratch(self):
        """
        Constructs a dependency graph from scratch for the given Python files.
        
        This method initializes various mappers and managers needed to analyze the files,
        extract components, and establish their relationships and dependencies.
        
        Returns:
            Tuple[list, dict]: A tuple containing a list of CodeComponent instances representing
                               the nodes of the graph and a dictionary mapping file paths to FileAnalyzer
                               instances representing the edges between nodes.
        """
        # Create an instance of FilePathAstMapper to parse the Python files into ASTs
        ast_manager = FilePathAstMapper(self.repos_dir, self.python_files)

        # Extract components from the files using the ASTs
        file_components_map, _, package_components_names = \
            extract_components_from_files(self.python_files,
                                          self.repos_dir,
                                          ast_manager.file_path_ast_map)

        # Initialize IdComponentMapper to manage component IDs and their mappings
        id_component_manager = IdComponentMapper(self.repos_dir,
                                                 file_components_map)

        # Initialize IdFileAnalyzerMapper to manage file analyzers and their mappings
        id_files_manager = IdFileAnalyzerMapper(self.python_files, ast_manager,
                                                package_components_names,
                                                self.repos_dir)

        # Initialize a list to hold CodeComponent instances
        code_components = []

        # Populate the list of CodeComponent instances using the IdComponentMapper
        for idx in id_component_manager.id_component_map:
            code_components.append(
                CodeComponent(idx, self.repos_dir, id_files_manager,
                              ast_manager.file_path_ast_map,
                              id_component_manager.id_component_map,
                              package_components_names))

        # Link components based on their imports and dependencies
        external_components_dict = {}

        for cmp_to_hash in code_components:
            hashId = hashlib.sha256(
                cmp_to_hash.getComponentAttribute('component_code').encode(
                    'utf-8')).hexdigest()
            id_component_manager.component_id_map[
                cmp_to_hash.getComponentAttribute('component_name')] = hashId 
            cmp_to_hash.setComponentAttribute('component_id', hashId)

        for cmp in code_components:
            all_internal_components = set(package_components_names)
            cmp_imports = set(cmp.extract_imports())
            linked_components = all_internal_components.intersection(
                cmp_imports)

            external_components = cmp_imports.difference(linked_components)
            for l_cmp in linked_components:
                l_cmp_id = id_component_manager.component_id_map[l_cmp]
                cmp.linked_component_ids.append(l_cmp_id)

            for a_cmp in external_components:
                idx = external_components_dict.get(a_cmp, None)
                if idx is None:
                    idx = str(uuid.uuid4())
                    external_components_dict[a_cmp] = idx
                cmp.external_component_ids.append(idx)

        # Return the list of CodeComponent instances and the file-to-analyzer mapping
        return code_components, id_files_manager.id_file_map, external_components_dict