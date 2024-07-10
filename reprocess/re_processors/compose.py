from reprocess.re_processors.processor import ReProcessor, AsyncReProcessor
from reprocess.re_container import ReContainer
from typing import List
from copy import deepcopy
import asyncio


class Compose():

    def __init__(self, processor_list: List[ReProcessor], **kwargs):
        self.processor_list = processor_list

    def __call__(self, repository_container: ReContainer):

        for processor in self.processor_list:
            repository_container = processor(repository_container)

        return repository_container


class AsyncCompose:

    def __init__(self, processor_list: List[AsyncReProcessor], **kwargs):
        self.processor_list = processor_list

    async def __call__(self, repository_container: ReContainer):
        tasks = [
            processor(deepcopy(repository_container))
            for processor in self.processor_list
        ]
        results = await asyncio.gather(*tasks)

        # Merge the results back into the original container
        for result in results:
            if isinstance(result, dict):
                for key, value in result.items():
                    setattr(repository_container, key, value)
            else:
                raise TypeError(
                    f"Processor returned a non-dictionary result: {result}")

        return repository_container
