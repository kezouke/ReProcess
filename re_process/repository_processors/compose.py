from re_process.repository_processors.abstract_processor import ReProcessor
from re_process.repository_processors.repository_container import ReContainer
from typing import List


class Compose():

    def __init__(self, processor_list: List[ReProcessor], **kwargs):
        self.processor_list = processor_list

    def __call__(self, repository_container: ReContainer):

        for processor in self.processor_list:
            repository_container = processor(repository_container)

        return repository_container
