import copy
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer
from typing import List


class Compose(RepositoryProcessor):

    def __init__(self,
                 processor_list: List[RepositoryProcessor],
                 inplace: bool = False):
        self.processor_list = processor_list
        self.inplace = inplace

    def __call__(self, repository_container: RepositoryContainer):
        active_container = repository_container if self.in_place \
                            else copy.deepcopy(repository_container)

        for processor in self.processor_list:
            processor(active_container)

        return active_container