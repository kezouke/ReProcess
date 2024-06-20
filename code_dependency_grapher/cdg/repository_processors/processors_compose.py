import copy
from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class Compose:

    def __init__(self,
                 repository_container: RepositoryContainer,
                 composeList: list[RepositoryProcessor],
                 in_place: bool = True):
        self.repository_container = repository_container
        self.compose_list = composeList
        self.in_place = in_place
        self.deep_copied_repository_container = None
        if in_place:
            for processor in composeList:
                processor.process(repository_container)
        else:
            self.deep_copied_repository_container = copy.deepcopy(
                repository_container)
            for processor in composeList:
                processor.process(self.deep_copied_repository_container)

    def get_processed_container(self) -> RepositoryContainer:
        if not self.in_place:
            return self.deep_copied_repository_container
        return self.repository_container
