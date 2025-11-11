import asyncio
from lindormmemobase import LindormMemobase
from lindormmemobase.models.blob import ChatBlob, BlobType, OpenAICompatibleMessage


async def buffer_management_demo():
    """完整的缓冲区管理演示"""

    # 初始化
    memobase = LindormMemobase.from_yaml_file("./config.yaml")
    user_id = "buffer_demo_user"
    print("=== 缓冲区管理演示 ===\n")
    # 1. 准备测试对话数据
    conversations = [
        ["user", "我是张三，在北京从事AI研发工作"],
        ["assistant", "您好张三！AI研发是很有前景的领域。"],
        ["user", "我希望能在这个领域有所突破"],
        ["assistant", "相信您一定可以的！"],
        ["user", "周末计划去图书馆学习新技术"],
        ["assistant", "充实的周末安排！"]
    ]

    # 2. 批量添加对话到缓冲区
    print("1. 批量添加对话到缓冲区...")
    blob_ids = []

    for i in range(0, len(conversations), 2):  # 每2条消息一个对话块
        if i + 1 < len(conversations):
            # 创建对话块
            chat_blob = ChatBlob(
                messages=[
                    OpenAICompatibleMessage(role=conversations[i][0], content=conversations[i][1]),
                    OpenAICompatibleMessage(role=conversations[i + 1][0], content=conversations[i + 1][1])
                ],
                type=BlobType.chat
            )

            # 添加到缓冲区
            blob_id = await memobase.add_blob_to_buffer(user_id, chat_blob)
            blob_ids.append(blob_id)
            print(f"   ✓ 对话块 {len(blob_ids)} 已添加: {blob_id}")

            # 每添加一个对话块就检查缓冲区状态
            status = await memobase.detect_buffer_full_or_not(user_id, BlobType.chat)
            print(f"   - 缓冲区状态: {'已满' if status['is_full'] else '未满'} "
                  f"(待处理: {len(status['buffer_full_ids'])} 个)")

            if status["is_full"]:
                print(f"   🔄 缓冲区已满，自动处理 {len(status['buffer_full_ids'])} 个数据块...")
                result = await memobase.process_buffer(
                    user_id=user_id,
                    blob_type=BlobType.chat,
                    blob_ids=status["buffer_full_ids"]
                )

                if result:
                    print(f"   ✅ 缓冲区处理完成")
                else:
                    print(f"   ⚠️ 缓冲区处理返回空结果")

            print()  # 空行分隔

    # 3. 处理剩余的缓冲区数据
    print("2. 检查并处理剩余缓冲区数据...")
    final_status = await memobase.detect_buffer_full_or_not(user_id, BlobType.chat)

    if final_status["buffer_full_ids"]:
        print(f"   发现 {len(final_status['buffer_full_ids'])} 个未处理的数据块")
        result = await memobase.process_buffer(user_id, BlobType.chat)
        if result:
            print("   ✅ 剩余数据处理完成")
    else:
        print("   ℹ️ 没有剩余的未处理数据")

    # 4. 验证处理结果
    print("\n3. 验证处理结果...")

    # 获取用户档案
    profiles = await memobase.get_user_profiles(user_id)
    print(f"   生成用户档案: {len(profiles)} 个主题")

    for profile in profiles:
        print(f"   📝 主题: {profile.topic}")
        for subtopic, entry in profile.subtopics.items():
            print(f"      └── {subtopic}: {entry.content}")

    # 获取事件
    events = await memobase.get_events(user_id, time_range_in_days=7, limit=10)
    print(f"\n   生成事件记录: {len(events)} 条")
    for event in events[:3]:  # 只显示前3条
        print(f"   📅 {event['content']}")

    # 5. 演示搜索功能
    print("\n4. 搜索相关记忆...")
    search_results = await memobase.search_events(
        user_id=user_id,
        query="技术学习",
        limit=3,
        similarity_threshold=0.1
    )

    print(f"   找到 {len(search_results)} 条相关记录:")
    for result in search_results:
        similarity = result.get('similarity', 0)
        print(f"   🔍 (相似度: {similarity:.2f}) {result['content']}")

    print(f"\n✨ 缓冲区管理演示完成！用户 {user_id} 的记忆系统已建立")


# 运行演示
if __name__ == "__main__":
    asyncio.run(buffer_management_demo())