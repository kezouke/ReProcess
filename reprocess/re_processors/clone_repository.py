import os
from reprocess.requests_handling.repository_manager import ReManager
from reprocess.re_processors.processor import ReProcessor
from reprocess.re_container import ReContainer


class CloneRepository(ReProcessor):

    def __init__(self, git_url: str = None, **kwargs):
        self.git_url = git_url

    def __call__(self, repository_container: ReContainer):
        store_repo_path = os.path.dirname(repository_container.repo_path)
        repo_manager = ReManager(store_repo_path, self.git_url)
        repo_info = repo_manager.update_or_clone_repo()

        return {
            "repo_author": repo_info[1],
            "repo_hash": repo_info[0],
            "not_empty": True
        }
