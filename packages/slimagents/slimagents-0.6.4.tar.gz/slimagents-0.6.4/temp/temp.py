import litellm
import asyncio

async def main(): 
    response = await litellm.acompletion(
        model="openai/gpt-4.1-mini",    
        # model="gemini/gemini-2.0-flash-lite-001",    
        messages=[
            {"role": "user", "content": "Hello"}
        ],
    )
    print(response.choices[0].message.content)

if __name__ == "__main__":
    asyncio.run(main())
