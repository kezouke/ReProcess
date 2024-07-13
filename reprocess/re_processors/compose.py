from reprocess.re_processors.processor import ReProcessor, AsyncReProcessor
from reprocess.re_container import ReContainer
from typing import List, Union


class Compose:

    def __init__(self, processor_list: List[Union[ReProcessor,
                                                  AsyncReProcessor]],
                 **kwargs):
        self.processor_list = processor_list

    def __call__(self, repository_container: ReContainer):

        for processor in self.processor_list:
            if isinstance(processor, AsyncReProcessor):
                repository_container = processor.run_synchronously(
                    repository_container)
            else:
                repository_container = processor(repository_container)

        return repository_container
