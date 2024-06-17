import os
import logging
import uuid

from code_dependency_grapher.utils.find_root_directory import find_project_root
from code_dependency_grapher.cdg.requests_handling.RequestSession import RequestSession
from code_dependency_grapher.cdg.requests_handling.RepositoryManager import RepositoryManager

logging.basicConfig(level=logging.ERROR)


class RequestManager:

    def __init__(self, db_absolute_path, repos_dir):
        self.db_abs_path = db_absolute_path
        self.project_root = find_project_root(os.path.abspath(__file__))

        if self.project_root is None:
            raise RuntimeError("Could not find project root")

        if repos_dir:
            self.repos_dir = repos_dir
        else:
            self.repos_dir = os.path.join(self.project_root,
                                          'code_dependency_grapher', 'data',
                                          'repos')
        print("Your folder is stored at:", self.repos_dir)

    def manage_request(self, git_url):
        repo_manager = RepositoryManager(self.repos_dir,
                                          git_url, True)
        RequestSession(repo_manager.request_type, self.db_abs_path,
                       str(uuid.uuid4()), repo_manager.repo_name,
                       self.repos_dir, repo_manager.repo_info,
                       repo_manager.updated_files, repo_manager.removed_files )
    def clone_repo(self, git_url):
        repo_manager = RepositoryManager(self.repos_dir,
                                         git_url, False)
        repo_manager.clone_repo(git_url,
                                 self.repos_dir)
# # Example usage
# repo_url = "https://github.com/triton-lang/triton"
# manager = RequestManager("cdscs")
# manager.manage_request(repo_url)
