from code_dependency_grapher.cdg.repository_processors.abstract_processor import RepositoryProcessor
from code_dependency_grapher.cdg.repository_processors.repository_container import RepositoryContainer


class Compose:

    def __init__(self,repository_container: RepositoryContainer,composeList: list[RepositoryProcessor]):
        for processor in composeList:
            processor.process(repository_container)