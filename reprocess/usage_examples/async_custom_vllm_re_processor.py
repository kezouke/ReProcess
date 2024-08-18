from reprocess.re_processors.processor import AsyncVLLMReProcessor
from reprocess.re_container import ReContainer
from reprocess.re_processors import Compose


class ExampleAsyncVLLMProcessorA(AsyncVLLMReProcessor):

    async def __call__(self, repository_container: ReContainer):
        json_data = {
            "min_tokens": 50,
            "max_tokens": 1000,
            "stop": '"',
            "prompt": "What is your favourite weather?"
        }
        result = await self.llm.get_response(json_data)
        return {"llm_result": result}


def main():
    print("Please don't forget to set up 'LLM_URL' env variable!")

    container = ReContainer("", "", "")
    async_processor1 = ExampleAsyncVLLMProcessorA()

    combined_compose = Compose([async_processor1])

    updated_container = combined_compose(container)
    print(updated_container.__dict__)


main()
