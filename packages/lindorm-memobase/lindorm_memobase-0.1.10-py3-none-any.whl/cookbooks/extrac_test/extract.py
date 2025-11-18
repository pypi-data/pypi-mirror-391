import asyncio
from lindormmemobase import LindormMemobase, ChatBlob, Config
from lindormmemobase.models.blob import OpenAICompatibleMessage
from dotenv import load_dotenv

load_dotenv()

memobase = LindormMemobase(Config.load_config("config.yaml"))
user_id = "8a4d7804-703f-51e5-80bc-b387f6173a8f"


async def extract():
    query = """```
- 用户的名字是Joanna。[提及于 2022/4/15]
```"""

    # query = "- User's alias is Joanna, assistant is Nate. // info"
    blobs = [ChatBlob(messages=[OpenAICompatibleMessage(role="user", content=query)])]

    result = await memobase.extract_memories(user_id, blobs)
    print(result)
    return result


async def fetch():
    query = "What does Maria want to do"
    context = await memobase.get_conversation_context(
        user_id=user_id,
        conversation=[OpenAICompatibleMessage(role="user", content=query)],
    )
    print("Context:", context)


if __name__ == "__main__":
    # asyncio.run(extract())
    asyncio.run(fetch())
