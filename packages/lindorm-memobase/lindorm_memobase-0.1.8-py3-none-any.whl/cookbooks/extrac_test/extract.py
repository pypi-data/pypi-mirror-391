import asyncio
from lindormmemobase import LindormMemobase, ChatBlob, Config
from lindormmemobase.models.blob import OpenAICompatibleMessage
from dotenv import load_dotenv

load_dotenv()

memobase = LindormMemobase(Config.load_config("config.yaml"))
user_id = "f5f762cb-974a-55ae-9180-ba18a46b8426"


async def extract():
    query = """```
- Maria mentioned her hobby of taking notes about local politics. [mention 9 January, 2023] // info
- Maria became friends with a fellow volunteer who shares the same interest in helping others. [mention 9 January, 2023] // event
- Maria advised John to stay strong during tough times and appreciate what he has. [mention 9 January, 2023] // info
- Maria expressed admiration for John's dedication to the community and his political goals. [mention 9 January, 2023] // info
- Maria emphasized the importance of uniting as a community to tackle problems and build a better neighborhood. [mention 9 January, 2023] // info
- John plans to attend a community meeting next week to discuss education and infrastructure upgrades. [mention 9 January, 2023, plan in 16 January, 2023] // schedule
- John experienced an unexpected incident on his way home last week. [mention 9 January, 2023, event in 2 January, 2023] // event
- User's alias is Maria, assistant is John. // info
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
