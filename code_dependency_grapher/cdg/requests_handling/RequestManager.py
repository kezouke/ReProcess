import os
import subprocess
import logging
import uuid

from code_dependency_grapher.utils.find_root_directory import find_project_root
from code_dependency_grapher.cdg.requests_handling.RequestSession import RequestSession
from code_dependency_grapher.cdg.requests_handling.RequestEnum import RequestType


logging.basicConfig(level=logging.ERROR)

class RequestManager:
    def __init__(self, db_absolute_path,repos_dir):
        self.db_abs_path = db_absolute_path
        self.project_root = find_project_root(os.path.abspath(__file__))
        if self.project_root is None:
            raise RuntimeError("Could not find project root")
        if repos_dir:
            self.repos_dir = repos_dir
            print(self.repos_dir)
        else:
            self.repos_dir = os.path.join(self.project_root, 'code_dependency_grapher', 'data', 'repos')

    def get_repo_name(self, repo_url):
        # Extracts the repository name from the URL
        return repo_url.split('/')[-1].split('.')[0]

    def repo_exists_locally(self, local_repo_path):
        # Checks if the repository exists locally
        return os.path.exists(local_repo_path)

    def clone_repo(self, repo_url, local_repo_path):
        # Clones the repository if it does not exist locally
        try:
            subprocess.run(['git', 'clone', repo_url, local_repo_path], check=True)
            logging.info(f"Successfully cloned {repo_url} into {local_repo_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone repository: {e}")

    def fetch_remote_changes(self, local_repo_path):
        # Fetches changes from the remote repository
        try:
            subprocess.run(['git', '-C', local_repo_path, 'fetch'], check=True)
            logging.info(f"Fetched latest changes for {local_repo_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch remote changes: {e}")

    def pull_latest_changes(self, local_repo_path):
        # Pulls the latest changes from the remote repository
        try:
            subprocess.run(['git', '-C', local_repo_path, 'pull'], check=True)
            logging.info(f"Pulled latest changes for {local_repo_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to pull latest changes: {e}")

    def get_changed_files(self, local_repo_path):
        try:
            result = subprocess.run(['git', '-C', local_repo_path, 'diff', '--name-status'],
                                    capture_output=True, text=True, check=True)
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get changed files: {e}")
            return []

    def manage_request(self, repo_url):
        local_repo_path = os.path.join(self.repos_dir, self.get_repo_name(repo_url))

        if not self.repo_exists_locally(local_repo_path):
            logging.info(f"Cloning {repo_url}...")
            self.clone_repo(repo_url, local_repo_path)
            RequestSession(RequestType.FROM_SCRATCH,
                           self.db_abs_path,
                           str(uuid.uuid4()),
                           self.get_repo_name(repo_url),
                           self.repos_dir)
        else:
            logging.info("Fetching latest changes...")
            self.fetch_remote_changes(local_repo_path)
            changed_files = self.get_changed_files(local_repo_path)
            status_file_name = [line.split('\t') for line in changed_files]

            removed_files = [line[1] for line in status_file_name if line[0] == 'D']
            updated_files = [line[1] for line in status_file_name if line[0] != 'D']

            print(removed_files)
            print(updated_files)
            if changed_files:
                logging.info("Changed files detected, pulling latest changes...")
                for file in changed_files:
                    logging.info(file)
                self.pull_latest_changes(local_repo_path)
            else:
                logging.info("No changes detected.")

            RequestSession(RequestType.FROM_SCRATCH,
                           self.db_abs_path,
                           str(uuid.uuid4()),
                           self.get_repo_name(repo_url),
                           self.repos_dir,
                           updated_files,
                           removed_files)

# # Example usage
# repo_url = "https://github.com/triton-lang/triton"
# manager = RequestManager("cdscs")
# manager.manage_request(repo_url)
