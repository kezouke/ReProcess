import os
import json
from typing import Optional

from code_dependency_grapher.cdg.requests_handling.RequestManager import RequestManager
from code_dependency_grapher.utils.process_db_abs_path import process_abs_db_path


class Engine:
    """
    Manages the core functionality of the dependency graph engine, including loading/saving paths,
    initializing the request manager, and handling requests.
    
    This class abstracts away the details of managing project-specific configurations and
    interactions with external resources, providing a streamlined interface for performing actions
    such as requesting data from repositories.
    """

    def __init__(self,
                 db_abs_path: Optional[str] = None,
                 path_where_to_store_repos: Optional[str] = None):
        """
        Initializes a new instance of the Engine class.
        
        Args:
            db_abs_path (Optional[str]): Absolute path to the folder where resulting 
                JSON graphs will be stored. Can be None. In this case db path will be extracted
                from /data/path.json
            path_where_to_store_repos (Optional[str]): Absolute path where all needed repositories
                are stored or will be git-cloned. Can be None. In this case, repos are 
                clonned into /data/repos/
        """
        # Process the absolute database path, either loading it from a file or using the provided value
        self.absolute_path = process_abs_db_path(db_abs_path)
        # Initialize the request manager with the determined absolute path and the path for storing repositories
        self.request_manager = RequestManager(self.absolute_path,
                                              path_where_to_store_repos)

    def request(self, repo_url: str) -> None:
        """
        Initiates a request to fetch data from the specified repository URL.
        
        This method delegates the actual request handling to the RequestManager instance,
        passing along the repository URL for processing.
        
        Args:
            repo_url (str): The URL of the repository from which data is requested.
        """
        self.request_manager.manage_request(repo_url)
