from reprocess.re_processors.processor import AsyncReProcessor
from reprocess.re_container import ReContainer
from reprocess.re_processors import AsyncCompose
import asyncio


class ExampleAsyncProcessorA(AsyncReProcessor):

    async def __call__(self, repository_container: ReContainer):
        # Simulate asynchronous processing
        await asyncio.sleep(1)
        # Example: update an attribute in the repository container
        return {"example_attr_a": "a"}


class ExampleAsyncProcessorB(AsyncReProcessor):

    async def __call__(self, repository_container: ReContainer):
        # Simulate asynchronous processing
        await asyncio.sleep(1)
        # Example: update an attribute in the repository container
        return {"example_attr_b": "b"}


async def main():
    container = ReContainer("", "", "")
    async_processor1 = ExampleAsyncProcessorA()
    async_processor2 = ExampleAsyncProcessorB()
    compose = AsyncCompose([async_processor1, async_processor2])

    updated_container = await compose(container)
    print(updated_container.__dict__)


asyncio.run(main())
