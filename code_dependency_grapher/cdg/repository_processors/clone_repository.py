import os
from code_dependency_grapher.cdg.requests_handling.RepositoryManager import RepositoryManager
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class CloneRepository(RepositoryProcessor):

    def __init__(self, git_url: str):
        self.git_url = git_url

    def __call__(self, repository_container: RepositoryContainer):
        store_repo_path = os.path.dirname(repository_container.repo_path)
        repo_manager = RepositoryManager(store_repo_path, self.git_url, False)
        repo_manager.clone_repo()
        repo_info = repo_manager.get_hash_and_author(
            repository_container.repo_path)
        repository_container.repo_author = repo_info[1]
        repository_container.repo_hash = repo_info[0]
