from typing import Optional
import os
import subprocess
import logging
from code_dependency_grapher.cdg.requests_handling.RequestEnum import RequestType

# Configure logging to display errors only
logging.basicConfig(level=logging.ERROR)


class RepositoryManager:
    """
    Manages operations on a Git repository such as cloning, 
    fetching changes, and identifying modified files.
    
    Attributes:
        repo_directory (str): The directory where the 
                              repository will be stored or
                              is currently stored.
        git_url (Optional[str]): The URL of the Git repository.
                              Can be None if the repository is 
                              managed locally.
        repo_name (str): Extracted name of the repository from 
                              the URL or directory path.
        request_type (RequestType): Indicates how the repository 
                              should be processed based on its
                              state.
        updated_files (list): List of files that have been updated
                              since the last operation.
        removed_files (list): List of files that have been removed 
                              since the last operation.
    """

    def __init__(self,
                 repository_directory: str = None,
                 git_hub_url: Optional[str] = None,
                 preprocess: Optional[bool] = True) -> None:
        """
        Initializes the RepositoryManager instance.
        
        Args:
            repository_directory (str): Path to the directory where
                               the repository is or will be located.
            git_hub_url (Optional[str]): URL of the Git repository. 
                               If None, assumes the repository is 
                               managed locally.
            preprocess (Optional[str]): Flag for the initial preprocessing of the repo
        """
        self.repo_directory = repository_directory
        self.git_url = git_hub_url
        self.preprocess = preprocess

        if self.git_url:
            self.repo_name = self.git_url.split('/')[-1].split('.')[0]
        else:
            self.repo_name = self.repo_directory.split('/')[-1].split('.')[0]

        if preprocess:
            self.request_type, self.updated_files, self.removed_files, self.repo_info = self._preprocess_repo(
            )
        else:
            self.request_type = RequestType.FROM_SCRATCH
            self.updated_files = []
            self.removed_files = []
            self.repo_info = [
                "Unknown when the user passes the repo folder rather than the git url",
                "Unknown when the user passes the repo folder rather than the git url"
            ]

    def _is_repo_exists_locally(self, local_repo_path: str) -> bool:
        """
        Checks if the repository exists at the given local path.
        
        Args:
            local_repo_path (str): Path to the local repository.
            
        Returns:
            bool: True if the repository exists, False otherwise.
        """
        return os.path.exists(local_repo_path)

    def clone_repo(self) -> None:
        """
        Clones the repository from the given URL to the specified local path if it does not already exist.
        
        Args:
            repo_url (str): URL of the Git repository to clone.
            local_repo_path (str): Local path where the repository should be cloned.
        """
        if not self.preprocess:
            self.repo_directory = os.path.join(self.repo_directory,
                                               self.repo_name)
            if self._is_repo_exists_locally(self.repo_directory):
                print("Repo is already cloned.")
                return
        try:
            subprocess.run(['git', 'clone', self.git_url, self.repo_directory],
                           check=True)
            logging.info(
                f"Successfully cloned {self.git_url} into {self.repo_directory}"
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone repository: {e}")

    def fetch_remote_changes(self, local_repo_path: str) -> None:
        """
        Fetches changes from the remote repository for the given local repository path.
        
        Args:
            local_repo_path (str): Local path of the repository.
        """
        try:
            subprocess.run(['git', '-C', local_repo_path, 'fetch'], check=True)
            logging.info(f"Fetched latest changes for {local_repo_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to fetch remote changes: {e}")

    def pull_latest_changes(self, local_repo_path: str) -> None:
        """
        Pulls the latest changes from the remote repository for the given local repository path.
        
        Args:
            local_repo_path (str): Local path of the repository.
        """
        try:
            subprocess.run(['git', '-C', local_repo_path, 'pull'], check=True)
            logging.info(f"Pulled latest changes for {local_repo_path}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to pull latest changes: {e}")

    def get_changed_files(self, local_repo_path: str) -> list:
        """
        Retrieves a list of files that have changed in the local repository since the last commit.
        
        Args:
            local_repo_path (str): Local path of the repository.
            
        Returns:
            list: A list of changed file paths.
        """
        try:
            result = subprocess.run(
                ['git', '-C', local_repo_path, 'diff', '--name-status'],
                capture_output=True,
                text=True,
                check=True)
            return result.stdout.splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get changed files: {e}")
            return []

    def get_hash_and_author(self, local_repo_path) -> list:
        try:
            result = subprocess.run([
                'git', '-C', local_repo_path, 'log', '-1',
                '--pretty=format:%H%n%ae'
            ],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            return result.stdout.split('\n')
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get commit hash and author: {e}")

    def _preprocess_repo(self) -> tuple:
        """
        Preprocesses the repository by checking if it exists locally, fetching changes, and determining the type of request needed.
        
        Returns:
            tuple: A tuple containing the request type, list of updated files, and list of removed files.
        """
        local_repo_path = os.path.join(self.repo_directory, self.repo_name)

        if self._is_repo_exists_locally(local_repo_path):
            logging.info("Fetching latest changes...")
            self.fetch_remote_changes(local_repo_path)
            changed_files = self.get_changed_files(local_repo_path)
            status_file_name = [line.split('\t') for line in changed_files]
            repo_info = self.get_hash_and_author(local_repo_path)
            removed_files = [
                line[1] for line in status_file_name if line[0] == 'D'
            ]
            updated_files = [
                line[1] for line in status_file_name if line[0] != 'D'
            ]

            if changed_files:
                logging.info(
                    "Changed files detected, pulling latest changes...")
                for file in changed_files:
                    logging.info(file)
                self.pull_latest_changes(local_repo_path)
            else:
                logging.info("No changes detected.")
            return RequestType.FROM_SCRATCH, updated_files, removed_files, repo_info

        logging.info(f"Cloning {self.git_url}...")
        self.clone_repo(self.git_url, local_repo_path)
        return RequestType.FROM_SCRATCH, [], [], self.get_hash_and_author(
            local_repo_path)
