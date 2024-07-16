import os
from reprocess.re_processors.processor import ReProcessor
from reprocess.re_container import ReContainer


class LocalLoader(ReProcessor):

    def __init__(self, **kwargs) -> None:
        super().__init__()

    def __call__(self, repository_container: ReContainer):
        assert os.path.exists(
            repository_container.repo_path), "Repo dir does not exist"

        return {
            "repo_author": "Does not available for local repo",
            "repo_hash": "Does not available for local repo",
            "is_downloaded": True
        }
