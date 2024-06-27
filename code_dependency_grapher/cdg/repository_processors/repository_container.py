class RepositoryContainer:

    def __init__(self, repo_name: str, repo_path: str, db_path: str) -> None:

        self.external_components = {}
        self.code_components = []
        self.files = []
        self.repo_author = ""
        self.repo_hash = ""
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.db_path = db_path

    def __eq__(self, other) -> bool:
        if isinstance(other, RepositoryContainer):
            self_attrs = vars(self)
            other_attrs = vars(other)

            if self_attrs.keys() != other_attrs.keys():
                return False

            for key in self_attrs.keys():
                if key not in other_attrs or self_attrs[key] != other_attrs[
                        key]:
                    return False
            return True
        else:
            return False
