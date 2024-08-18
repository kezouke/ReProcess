from reprocess.re_processors.processor import AsyncReProcessor, ReProcessor
from reprocess.re_container import ReContainer
from reprocess.re_processors import Compose
import asyncio


class ExampleAsyncProcessorA(AsyncReProcessor):

    async def __call__(self, repository_container: ReContainer):
        # Simulate asynchronous processing
        await asyncio.sleep(1)
        print("A")
        # Example: update an attribute in the repository container
        return {"example_attr_a": "a"}


class ExampleAsyncProcessorB(AsyncReProcessor):

    async def __call__(self, repository_container: ReContainer):
        # Simulate asynchronous processing
        await asyncio.sleep(1)
        print("B")
        # Example: update an attribute in the repository container
        return {"example_attr_b": "b"}


class ExampleSyncProcessorA(ReProcessor):

    def __call__(self, repository_container: ReContainer):
        print("C")
        return {"example_attr_c": "c"}


def main():
    container = ReContainer("", "", "")
    async_processor1 = ExampleAsyncProcessorA()
    async_processor2 = ExampleAsyncProcessorB()
    sync_processor = ExampleSyncProcessorA()

    combined_compose = Compose(
        [async_processor1, async_processor2, sync_processor])

    updated_container = combined_compose(container)
    print(updated_container.__dict__)


main()
