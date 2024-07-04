from typing import Optional, List
import os
import subprocess
import logging

# Configure logging to display errors only
logging.basicConfig(level=logging.ERROR)


class ReManager:
    """
    Manages operations on a Git repository such as cloning 
    and retrieving repository information.
    
    Attributes:
        repo_directory (str): The directory where the repository will be stored.
        git_url (Optional[str]): The URL of the Git repository.
        repo_name (str): Extracted name of the repository from the URL.
    """

    def __init__(self, repository_directory: str,
                 git_url: Optional[str]) -> None:
        """
        Initializes the ReManager instance.
        
        Args:
            repository_directory (str): Path to the directory where the repository will be located.
            git_url (Optional[str]): URL of the Git repository.
        """
        self.repo_directory = repository_directory
        self.git_url = git_url

        if self.git_url:
            self.repo_name = self.git_url.split('/')[-1].split('.')[0]
            self.repo_directory = os.path.join(self.repo_directory,
                                               self.repo_name)
        else:
            raise ValueError("Git URL must be provided")

    def _is_repo_exists_locally(self) -> bool:
        """
        Checks if the repository exists at the given local path.
        
        Returns:
            bool: True if the repository exists, False otherwise.
        """
        return os.path.exists(self.repo_directory)

    def clone_repo(self) -> None:
        """
        Clones the repository from the given URL to the specified local path if it does not already exist.
        """
        if self._is_repo_exists_locally():
            print("Repository is already cloned.")
            return

        try:
            subprocess.run(['git', 'clone', self.git_url, self.repo_directory],
                           check=True)
            logging.info(
                f"Successfully cloned {self.git_url} into {self.repo_directory}"
            )
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone repository: {e}")
            raise

    def get_hash_and_author(self) -> List[str]:
        """
        Retrieves the latest commit hash and author from the local repository.
        
        Returns:
            list: A list containing the latest commit hash and author email.
        """
        try:
            result = subprocess.run([
                'git', '-C', self.repo_directory, 'log', '-1',
                '--pretty=format:%H%n%ae'
            ],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            return result.stdout.split('\n')
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get commit hash and author: {e}")
            raise
