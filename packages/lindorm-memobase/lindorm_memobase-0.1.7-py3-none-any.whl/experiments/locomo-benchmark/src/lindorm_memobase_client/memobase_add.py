import uuid
import json
import os
import asyncio
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from lindormmemobase import LindormMemobase, ChatBlob, Config
from lindormmemobase.models.blob import OpenAICompatibleMessage, BlobType

load_dotenv()

root_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(root_dir, "config.yaml")


def string_to_uuid(s: str, salt="memobase_client") -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, s + salt))


class LindormMemobaseADD:
    def __init__(self, data_path, batch_size=2, reprocess=False):
        if os.path.exists(config_path):
            config = Config.load_config()
            self.memobase = LindormMemobase(config)
        self.batch_size = batch_size
        self.data_path = data_path
        self.data = None
        self.reprocess = reprocess
        if data_path:
            self.load_data()

    def load_data(self):
        with open(self.data_path, "r") as f:
            self.data = json.load(f)
        return self.data

    async def add_memory(self, user_id, messages, retries=3):
        real_user_id = string_to_uuid(user_id)
        blobs = [OpenAICompatibleMessage(**message) for message in messages]
        for attempt in range(retries):
            try:
                blob_ids = await self.memobase.add_blob_to_buffer(real_user_id, ChatBlob(messages=blobs))
                print(f"   ✓ 对话块 {len(blob_ids)} 已添加: {blob_ids}")

                status = await self.memobase.detect_buffer_full_or_not(user_id, BlobType.chat)
                print(f"   - 缓冲区状态: {'已满' if status['is_full'] else '未满'} "
                      f"(待处理: {len(status['buffer_full_ids'])} 个)")

                if status["is_full"]:
                    print(f"   🔄 缓冲区已满，自动处理 {len(status['buffer_full_ids'])} 个数据块...")
                    result = await self.memobase.process_buffer(
                        user_id=user_id,
                        blob_type=BlobType.chat,
                        blob_ids=status["buffer_full_ids"]
                    )
                    if result:
                        print(f"   ✅ 缓冲区处理完成")
                    else:
                        print(f"   ⚠️ 缓冲区处理返回空结果")
                return
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(1)  # Wait before retrying
                    continue
                else:
                    raise e

    async def add_memories_for_speaker(self, speaker, messages, desc):
        for i in tqdm(range(0, len(messages), self.batch_size), desc=desc):
            batch_messages = messages[i:i + self.batch_size]
            await self.add_memory(speaker, batch_messages)

    async def process_conversation(self, item, idx):
        conversation = item["conversation"]
        speaker_a = conversation["speaker_a"]
        speaker_b = conversation["speaker_b"]

        speaker_a_user_id = f"{speaker_a}_{idx}"
        speaker_b_user_id = f"{speaker_b}_{idx}"

        for key in conversation.keys():
            if key in ["speaker_a", "speaker_b"] or "date" in key or "timestamp" in key:
                continue

            date_time_key = key + "_date_time"
            timestamp = conversation[date_time_key]
            chats = conversation[key]

            messages = []
            messages_reverse = []
            for chat in chats:
                if chat["speaker"] == speaker_a:
                    messages.append(
                        {
                            "role": "user",
                            "content": chat["text"],
                            "alias": speaker_a,
                            "created_at": timestamp,
                        }
                    )
                    messages_reverse.append(
                        {
                            "role": "assistant",
                            "content": chat["text"],
                            "alias": speaker_a,
                            "created_at": timestamp,
                        }
                    )
                elif chat["speaker"] == speaker_b:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": chat["text"],
                            "alias": speaker_b,
                            "created_at": timestamp,
                        }
                    )
                    messages_reverse.append(
                        {
                            "role": "user",
                            "content": chat["text"],
                            "alias": speaker_b,
                            "created_at": timestamp,
                        }
                    )
                else:
                    raise ValueError(f"Unknown speaker: {chat['speaker']}")

            # add memories for the two users on different threads
            task_a = self.add_memories_for_speaker(
                speaker_a_user_id,
                messages,
                f"{idx} Adding Memories for {speaker_a}",
            )
            task_b = self.add_memories_for_speaker(
                speaker_b_user_id,
                messages_reverse,
                f"{idx} Adding Memories for {speaker_b}",
            )
            await asyncio.gather(task_a, task_b)

        print("Messages added successfully")

    def _process_conversation_sync(self, item, idx):
        asyncio.run(self.process_conversation(item, idx))

    def process_all_conversations(self, max_workers=10, max_samples=None):
        if not self.data:
            raise ValueError(
                "No data loaded. Please set data_path and call load_data() first."
            )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            if max_samples:
                self.data = self.data[:max_samples]
            futures = [
                executor.submit(self._process_conversation_sync, item, idx)
                for idx, item in enumerate(self.data)
            ]

            for future in tqdm(futures, desc="Processing conversations"):
                future.result()
