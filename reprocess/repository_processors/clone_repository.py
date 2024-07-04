import os
from reprocess.requests_handling.repository_manager import RepositoryManager
from reprocess.repository_processors.abstract_processor import RepositoryProcessor
from reprocess.repository_processors.repository_container import RepositoryContainer


class CloneRepository(ReProcessor):

    def __init__(self, git_url: str = None, **kwargs):
        self.git_url = git_url

    def __call__(self, repository_container: ReContainer):
        store_repo_path = os.path.dirname(repository_container.repo_path)
        repo_manager = RepositoryManager(store_repo_path, self.git_url, False)
        repo_manager.clone_repo()
        repo_info = repo_manager.get_hash_and_author(
            repository_container.repo_path)

        return {
            "repo_author": repo_info[1],
            "repo_hash": repo_info[0],
            "is_downloaded": True
        }
