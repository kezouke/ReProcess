import os
import subprocess

class RequestManager:

    def __init__(self, db_absolute_path):
        self.db_abs_path = db_absolute_path

    def get_repo_name(self, repo_url):
        # Extracts the repository name from the URL
        return repo_url.split('/')[-1].split('.')[0]

    def repo_exists_locally(self, local_repo_path):
        # Checks if the repository exists locally
        return os.path.exists(local_repo_path)

    def clone_repo(self):
        # Clones the repository if it does not exist locally
        subprocess.run(['git', 'clone', self.repo_url, self.local_repo_path], check=True)

    def fetch_remote_changes(self, local_repo_path):
        # Fetches changes from the remote repository
        subprocess.run(['git', '-C', local_repo_path, 'fetch'], check=True)

    def get_changed_files(self, local_repo_path):
        # Compares local and remote branches to find changed files
        result = subprocess.run(['git', '-C', local_repo_path, 'diff', '--name-only', 'HEAD', 'origin/master'],
                                capture_output=True, text=True)
        return result.stdout.splitlines()

    def manage_request(self, repo_url):
        local_repo_path = f'../data/repos/{self.get_repo_name(repo_url)}'

        if not self.repo_exists_locally(local_repo_path):
            print(f"Cloning {self.repo_url}...")
            self.clone_repo()
        else:
            print("Fetching latest changes...")
            self.fetch_remote_changes()
            changed_files = self.get_changed_files()
            if changed_files:
                print("Changed files:")
                for file in changed_files:
                    print(file)
            else:
                print("No changes detected.")

# Example usage
repo_url = "https://github.com/example/repo.git"
manager = RequestManager(repo_url)
manager.manage_request()
