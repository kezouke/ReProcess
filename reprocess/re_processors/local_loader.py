import os
from reprocess.re_processors.processor import ReProcessor
from reprocess.re_container import ReContainer


class LocalLoader(ReProcessor):

    def __init__(self, repo_path, **kwargs) -> None:
        self.repo_path = repo_path
        super().__init__()

    def __call__(self, repository_container: ReContainer):
        assert os.path.exists(self.repo_path), "Repo dir does not exist"

        return {
            "repo_path": self.repo_path,
            "repo_author": "Does not available for local repo",
            "repo_hash": "Does not available for local repo",
            "is_downloaded": True
        }
