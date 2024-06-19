class RepositoryContainer:

    def __init__(self, repo_name: str, repo_path: str, db_path: str) -> None:

        self.code_components = []
        self.files = []
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.db_path = db_path
