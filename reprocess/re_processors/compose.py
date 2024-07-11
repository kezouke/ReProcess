from reprocess.re_processors.processor import ReProcessor, AsyncReProcessor
from reprocess.re_container import ReContainer
from typing import List, Union
import asyncio


class Compose:

    def __init__(self, processor_list: List[Union[ReProcessor,
                                                  AsyncReProcessor]],
                 **kwargs):
        self.processor_list = processor_list

    def __call__(self, repository_container: ReContainer):

        for processor in self.processor_list:
            if isinstance(processor, AsyncReProcessor):
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:  # No running event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                if loop.is_running():
                    result = loop.create_task(processor(repository_container))
                    repository_container = asyncio.run_coroutine_threadsafe(
                        result, loop).result()
                else:
                    repository_container = asyncio.run(
                        processor(repository_container))
            else:
                repository_container = processor(repository_container)

        return repository_container
