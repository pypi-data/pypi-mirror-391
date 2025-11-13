import litellm
import asyncio
from slimagents import Agent

def calculator(input: str) -> str:
    return eval(input)

async def main(): 
    agent = Agent(
        model="openai/gpt-4.1-mini",    
        instructions="You are a helpful assistant.",
        tools=[calculator],
    )
    async for chunk in await agent.run("What is 2 + 2?", stream=True, stream_response=True):
        if isinstance(chunk, str):
            print(chunk)
        else:
            print(chunk.metadata)
            print(len(chunk.metadata.litellm_usage))
            print(len(chunk.metadata.litellm_hidden_params))
            for hidden_param in chunk.metadata.litellm_hidden_params:
                print(hidden_param)
                print("--------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
