#!/usr/bin/env python3
"""
LindormMemobase API 综合测试文件

这个测试文件覆盖了 LindormMemobase 的所有主要 API 接口：
1. 初始化方法
2. 内存提取
3. 用户档案管理
4. 事件管理
5. 上下文生成
6. 缓冲区管理

使用方法：
1. 确保已配置 config.yaml 和 .env 文件
2. 运行测试：python test_comprehensive_api.py
"""

import asyncio
import uuid
import os
from typing import List
from lindormmemobase import LindormMemobase
from lindormmemobase.models.blob import ChatBlob, DocBlob, BlobType, OpenAICompatibleMessage
from lindormmemobase.models.profile_topic import ProfileConfig


async def test_initialization():
    """测试初始化方法"""
    print("=== 测试初始化方法 ===")
    
    # 方法1：使用默认配置
    try:
        memobase1 = LindormMemobase()
        print("✓ 默认配置初始化成功")
    except Exception as e:
        print(f"✗ 默认配置初始化失败: {e}")
    
    # 方法2：从YAML文件加载
    try:
        memobase2 = LindormMemobase.from_yaml_file("./config.yaml")
        print("✓ YAML文件初始化成功")
    except Exception as e:
        print(f"✗ YAML文件初始化失败: {e}")
    
    # 方法3：使用参数初始化
    try:
        memobase3 = LindormMemobase.from_config(
            language="zh"
        )
        print("✓ 参数初始化成功")
    except Exception as e:
        print(f"✗ 参数初始化失败: {e}")
    
    print()


async def test_memory_extraction(memobase: LindormMemobase, user_id: str):
    """测试内存提取功能"""
    print("=== 测试内存提取功能 ===")
    
    # 创建测试数据
    chat_blob = ChatBlob(
        messages=[
            OpenAICompatibleMessage(
                role="user",
                content="我是李四，今年30岁，是一名软件工程师，居住在上海。我喜欢编程、阅读和技术分享。"
            ),
            OpenAICompatibleMessage(
                role="assistant",
                content="很高兴认识您，李四！软件工程师是个很有挑战性的职业。"
            )
        ]
    )
    
    doc_blob = DocBlob(
        content="项目进展报告：本周完成了用户管理系统的设计和数据库搭建，下周计划开始前端开发。",
        type=BlobType.doc
    )
    
    try:
        # 提取记忆
        result = await memobase.extract_memories(
            user_id=user_id,
            blobs=[chat_blob]
        )
        print("✓ 内存提取成功")
        print(f"  提取结果: {result}")
    except Exception as e:
        print(f"✗ 内存提取失败: {e}")
    
    print()


async def test_user_profiles(memobase: LindormMemobase, user_id: str):
    """测试用户档案管理"""
    print("=== 测试用户档案管理 ===")
    
    try:
        # 获取所有用户档案
        profiles = await memobase.get_user_profiles(user_id)
        print(f"✓ 获取用户档案成功，共 {len(profiles)} 个主题")
        
        # 显示档案信息
        for profile in profiles[:3]:  # 只显示前3个
            print(f"  主题: {profile.topic}")
            for subtopic, entry in list(profile.subtopics.items())[:2]:  # 只显示前2个子主题
                print(f"    {subtopic}: {entry.content}")
        
        # 获取特定主题的档案
        specific_profiles = await memobase.get_user_profiles(
            user_id=user_id,
            topics=["基本信息", "AI助手偏好"]
        )
        print(f"✓ 获取特定主题档案成功，共 {len(specific_profiles)} 个主题")
        
        # 根据对话获取相关档案
        conversation = [
            OpenAICompatibleMessage(
                role="user",
                content="我想了解一些编程学习的建议"
            )
        ]
        
        relevant_profiles = await memobase.get_relevant_profiles(
            user_id=user_id,
            conversation=conversation,
            max_profiles=3
        )
        print(f"✓ 获取相关档案成功，共 {len(relevant_profiles)} 个相关主题")
        
        # 搜索档案
        search_profiles = await memobase.search_profiles(
            user_id=user_id,
            query="软件工程师",
            max_results=2
        )
        print(f"✓ 搜索档案成功，共 {len(search_profiles)} 个匹配结果")
        
    except Exception as e:
        print(f"✗ 用户档案管理测试失败: {e}")
    
    print()


async def test_event_management(memobase: LindormMemobase, user_id: str):
    """测试事件管理"""
    print("=== 测试事件管理 ===")
    
    try:
        # 获取最近事件
        events = await memobase.get_events(
            user_id=user_id,
            time_range_in_days=30,
            limit=5
        )
        print(f"✓ 获取最近事件成功，共 {len(events)} 条")
        
        # 显示事件信息
        for event in events[:3]:  # 只显示前3条
            print(f"  事件: {event['content'][:50]}...")
        
        # 搜索事件
        search_events = await memobase.search_events(
            user_id=user_id,
            query="编程",
            limit=3,
            similarity_threshold=0.1,
            time_range_in_days=30
        )
        print(f"✓ 搜索事件成功，共 {len(search_events)} 条相关记录")
        
        # 显示搜索结果
        for event in search_events:
            similarity = event.get('similarity', 0)
            print(f"  相似度 {similarity:.2f}: {event['content'][:50]}...")
            
    except Exception as e:
        print(f"✗ 事件管理测试失败: {e}")
    
    print()


async def test_context_generation(memobase: LindormMemobase, user_id: str):
    """测试上下文生成"""
    print("=== 测试上下文生成 ===")
    
    try:
        # 创建对话历史
        conversation = [
            OpenAICompatibleMessage(
                role="user",
                content="我最近在学习Python编程，有什么好的建议吗？"
            )
        ]
        
        # 生成上下文
        context = await memobase.get_conversation_context(
            user_id=user_id,
            conversation=conversation,
            max_token_size=1000,
            prefer_topics=["基本信息", "AI助手偏好"],
            time_range_in_days=30,
            profile_event_ratio=0.7
        )
        print("✓ 上下文生成成功")
        print(f"  上下文长度: {len(context)} 字符")
        print(f"  上下文预览: {context[:200]}...")
        
    except Exception as e:
        print(f"✗ 上下文生成测试失败: {e}")
    
    print()


async def test_buffer_management(memobase: LindormMemobase, user_id: str):
    """测试缓冲区管理"""
    print("=== 测试缓冲区管理 ===")
    
    # 准备测试对话数据
    conversations = [
        ["user", "我是张三，在北京从事AI研发工作"],
        ["assistant", "您好张三！AI研发是很有前景的领域。"],
        ["user", "我平时喜欢阅读技术书籍和跑步"],
        ["assistant", "阅读和跑步都是很好的习惯！"],
        ["user", "最近在研究大语言模型的应用"],
        ["assistant", "LLM确实是当前的热点技术。"],
        ["user", "我希望能在这个领域有所突破"],
        ["assistant", "相信您一定可以的！"],
        ["user", "周末计划去图书馆学习新技术"],
        ["assistant", "充实的周末安排！"]
    ]
    
    blob_ids = []
    
    try:
        # 批量添加对话到缓冲区
        print("1. 批量添加对话到缓冲区...")
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

        # 处理剩余的缓冲区数据
        print("2. 检查并处理剩余缓冲区数据...")
        final_status = await memobase.detect_buffer_full_or_not(user_id, BlobType.chat)

        if final_status["buffer_full_ids"]:
            print(f"   发现 {len(final_status['buffer_full_ids'])} 个未处理的数据块")
            result = await memobase.process_buffer(user_id, BlobType.chat)
            if result:
                print("   ✅ 剩余数据处理完成")
        else:
            print("   ℹ️ 没有剩余的未处理数据")
            
        print("✓ 缓冲区管理测试完成")
        
    except Exception as e:
        print(f"✗ 缓冲区管理测试失败: {e}")
    
    print()


async def main():
    """主测试函数"""
    print("开始 LindormMemobase API 综合测试\n")
    
    # 创建唯一的用户ID用于测试
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    print(f"测试用户ID: {user_id}\n")
    
    try:
        # 检查环境变量
        llm_api_key = os.environ.get("MEMOBASE_LLM_API_KEY")
        if not llm_api_key:
            print("警告: 未设置 MEMOBASE_LLM_API_KEY 环境变量，部分测试可能失败")
        
        # 初始化
        memobase = LindormMemobase.from_yaml_file("./config.yaml")
        print("✓ LindormMemobase 初始化成功\n")
        
        # 运行各项测试
        await test_initialization()
        await test_memory_extraction(memobase, user_id)
        await test_user_profiles(memobase, user_id)
        await test_event_management(memobase, user_id)
        await test_context_generation(memobase, user_id)
        await test_buffer_management(memobase, user_id)
        
        print("=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())