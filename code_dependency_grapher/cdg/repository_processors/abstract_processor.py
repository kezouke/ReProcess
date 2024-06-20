from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from abc import ABC, abstractmethod


class RepositoryProcessor(ABC):

    @abstractmethod
    def __call__(self, repository_container: RepositoryContainer):
        pass
