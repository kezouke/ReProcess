import copy
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from typing import List


class Compose(RepositoryProcessor):

    def __init__(self,
                 processor_list: List[RepositoryProcessor],
                 inplace: bool = True):
        self.processor_list = processor_list
        # self.inplace = inplace

    def __call__(self, repository_container: RepositoryContainer):

        for processor in self.processor_list:
            repository_container = processor(repository_container)

        return dict()
