class RepositoryContainer:

    def __init__(self, repo_name: str, repo_path: str, repo_author: str, repo_hash:str,
                 db_path: str) -> None:

        self.code_components = []
        self.files = []
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.db_path = db_path
        self.repo_author = repo_author
        self.repo_hash = repo_hash
