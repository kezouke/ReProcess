from abc import ABC, abstractmethod


class Mapper(ABC):
    """
    Abstract base class for mappers.
    """

    def __init__(self, repos_dir):
        self.repos_dir = repos_dir
        self.mapping = {}

    @abstractmethod
    def generate_mapping(self):
        """
        Abstract method to be implemented by subclasses to generate mappings.
        """
        pass

    def get_mapping(self):
        """
        Returns the generated mapping.
        """
        return self.mapping