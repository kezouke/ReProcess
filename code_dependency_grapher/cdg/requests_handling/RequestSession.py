import os
from code_dependency_grapher.cdg.requests_handling.RequestEnum import RequestType
from code_dependency_grapher.cdg.GraphCreator import GraphCreator
from code_dependency_grapher.utils.find_python_files import find_python_files
from code_dependency_grapher.utils.find_root_directory import find_project_root


class RequestSession:
    def __init__(self, 
                 mode,
                 abs_db_path, 
                 request_id, 
                 repo_name) -> None:
        self.mode = mode
        self.abs_db_path = abs_db_path
        self.request_id = request_id
        self.repo_name = repo_name

        self.project_root = find_project_root(os.path.abspath(__file__))
        self.repos_dir = os.path.join(self.project_root,
                                      'code_dependency_grapher', 
                                      'data', 
                                      'repos',
                                      self.repo_name)


        if mode == RequestType.FROM_SCRATCH:
            # graph builder from scratch
            python_files = find_python_files(self.repos_dir)
            graph_creator = GraphCreator(python_files)
            graph_builded = graph_creator.create_from_scratch()
            print(graph_builded)
        elif mode == RequestType.UPDATE_EXISTING:
            # TODO:
            # graph builder to update existing tree
            pass 