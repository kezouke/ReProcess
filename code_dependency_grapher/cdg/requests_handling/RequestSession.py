import os
from code_dependency_grapher.cdg.requests_handling.RequestEnum import RequestType
from code_dependency_grapher.cdg.GraphCreator import GraphCreator
from code_dependency_grapher.utils.find_python_files import find_python_files
from code_dependency_grapher.cdg.JsonConverter import JsonConverter


class RequestSession:

    def __init__(self,
                 mode,
                 abs_db_path,
                 request_id,
                 repo_name,
                 repos_dir,
                 repo_info,
                 updated_files=None,
                 removed_files=None) -> None:
        self.mode = mode
        self.abs_db_path = abs_db_path
        self.request_id = request_id
        self.repo_name = repo_name
        self.repos_dir = os.path.join(repos_dir, self.repo_name)
        self.repo_hash = repo_info[0]
        self.repo_author = repo_info[1]

        if mode == RequestType.FROM_SCRATCH:
            # graph builder from scratch
            python_files = find_python_files(self.repos_dir)
            graph_creator = GraphCreator(python_files, self.repos_dir)
            graph_built = graph_creator.create_from_scratch()
            JsonConverter.convert(
                os.path.join(self.abs_db_path, self.repo_name,
                             "data.json"), graph_built[0], graph_built[1],
                graph_built[2], self.repo_hash, self.repo_author)

            # print(graph_builded)
        elif mode == RequestType.UPDATE_EXISTING:
            assert updated_files is not None
            assert removed_files is not None

            # TODO: change in future
            python_files = find_python_files(self.repos_dir)
            graph_creator = GraphCreator(python_files, self.repos_dir)
            graph_built = graph_creator.create_from_scratch()
            JsonConverter.convert(
                os.path.join(self.abs_db_path, self.repo_name,
                             "data.json"), graph_built[0], graph_built[1],
                graph_built[2], self.repo_hash, self.repo_author)
