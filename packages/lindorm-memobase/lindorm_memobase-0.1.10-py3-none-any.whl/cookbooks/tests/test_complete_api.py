#!/usr/bin/env python3
"""
LindormMemobase API 完整测试文件

这个测试文件覆盖了 LindormMemobase 的所有主要 API 接口。
注意：要完整运行此测试，需要：
1. 配置有效的 .env 文件（包含数据库连接和API密钥）
2. 配置 config.yaml 文件
3. 确保 Lindorm Table 和 Lindorm Search 服务正在运行

使用方法：
1. 复制 cookbooks/.env.example 到 .env 并填入实际值
2. 确保 cookbooks/config.yaml 配置正确
3. 运行测试：python test_complete_api.py
"""

import asyncio
import uuid
import os
from typing import Optional
from lindormmemobase import LindormMemobase, ConfigurationError, LindormMemobaseError
from lindormmemobase.models.blob import ChatBlob, DocBlob, BlobType, OpenAICompatibleMessage
from lindormmemobase.models.profile_topic import ProfileConfig


async def check_environment():
    """检查环境配置"""
    print("=== 环境配置检查 ===")
    
    # 检查必要的环境变量
    required_vars = ["MEMOBASE_LLM_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"⚠️  缺少必要的环境变量: {', '.join(missing_vars)}")
        print("   请复制 cookbooks/.env.example 到 .env 并填入实际值")
        return False
    
    # 检查配置文件
    config_path = "./cookbooks/config.yaml"
    if not os.path.exists(config_path):
        print(f"⚠️  配置文件不存在: {config_path}")
        return False
    
    print("✓ 环境配置检查通过")
    return True


async def test_initialization():
    """测试初始化方法"""
    print("\n=== 测试初始化方法 ===")
    
    results = []
    successful_memobase = None
    
    # 方法1：使用YAML文件加载
    try:
        memobase1 = LindormMemobase.from_yaml_file("./config.yaml")
        print("✓ YAML文件初始化成功")
        results.append(True)
        if successful_memobase is None:
            successful_memobase = memobase1
    except Exception as e:
        print(f"✗ YAML文件初始化失败: {e}")
        results.append(False)
    
    # 方法2：使用参数初始化
    try:
        memobase2 = LindormMemobase.from_config(
            language="zh",
            llm_api_key=os.environ.get("MEMOBASE_LLM_API_KEY", "test-key")
        )
        print("✓ 参数初始化成功")
        results.append(True)
        if successful_memobase is None:
            successful_memobase = memobase2
    except Exception as e:
        print(f"✗ 参数初始化失败: {e}")
        results.append(False)
    
    # 方法3：使用默认配置
    try:
        memobase3 = LindormMemobase()
        print("✓ 默认配置初始化成功")
        results.append(True)
        if successful_memobase is None:
            successful_memobase = memobase3
    except Exception as e:
        print(f"✗ 默认配置初始化失败: {e}")
        results.append(False)
    
    return successful_memobase


async def test_memory_extraction(memobase: LindormMemobase, user_id: str):
    """测试内存提取功能"""
    print("\n=== 测试内存提取功能 ===")
    
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
    
    try:
        # 提取记忆
        result = await memobase.extract_memories(
            user_id=user_id,
            blobs=[chat_blob]
        )
        print("✓ 内存提取成功")
        print(f"  提取结果类型: {type(result)}")
        return True
    except LindormMemobaseError as e:
        print(f"✗ 内存提取失败（API错误）: {e}")
        return False
    except Exception as e:
        print(f"✗ 内存提取失败（系统错误）: {e}")
        return False


async def test_user_profiles(memobase: LindormMemobase, user_id: str):
    """测试用户档案管理"""
    print("\n=== 测试用户档案管理 ===")
    
    try:
        # 获取所有用户档案
        profiles = await memobase.get_user_profiles(user_id)
        print(f"✓ 获取用户档案成功，共 {len(profiles)} 个主题")
        
        # 显示档案信息
        for profile in profiles[:3]:  # 只显示前3个
            print(f"  主题: {profile.topic}")
            subtopics_count = len(profile.subtopics)
            print(f"    包含 {subtopics_count} 个子主题")
        
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
        
        return True
    except LindormMemobaseError as e:
        print(f"✗ 用户档案管理测试失败（API错误）: {e}")
        return False
    except Exception as e:
        print(f"✗ 用户档案管理测试失败（系统错误）: {e}")
        return False


async def test_event_management(memobase: LindormMemobase, user_id: str):
    """测试事件管理"""
    print("\n=== 测试事件管理 ===")
    
    try:
        # 获取最近事件
        events = await memobase.get_events(
            user_id=user_id,
            time_range_in_days=30,
            limit=5
        )
        print(f"✓ 获取最近事件成功，共 {len(events)} 条")
        
        # 搜索事件
        search_events = await memobase.search_events(
            user_id=user_id,
            query="编程",
            limit=3,
            similarity_threshold=0.1,
            time_range_in_days=30
        )
        print(f"✓ 搜索事件成功，共 {len(search_events)} 条相关记录")
        
        return True
    except LindormMemobaseError as e:
        print(f"✗ 事件管理测试失败（API错误）: {e}")
        return False
    except Exception as e:
        print(f"✗ 事件管理测试失败（系统错误）: {e}")
        return False


async def test_context_generation(memobase: LindormMemobase, user_id: str):
    """测试上下文生成"""
    print("\n=== 测试上下文生成 ===")
    
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
        
        return True
    except LindormMemobaseError as e:
        print(f"✗ 上下文生成测试失败（API错误）: {e}")
        return False
    except Exception as e:
        print(f"✗ 上下文生成测试失败（系统错误）: {e}")
        return False


async def test_buffer_management(memobase: LindormMemobase, user_id: str):
    """测试缓冲区管理"""
    print("\n=== 测试缓冲区管理 ===")
    
    # 准备测试对话数据
    conversations = [
        ["user", "我是张三，在北京从事AI研发工作"],
        ["assistant", "您好张三！AI研发是很有前景的领域。"],
        ["user", "我平时喜欢阅读技术书籍和跑步"],
        ["assistant", "阅读和跑步都是很好的习惯！"],
        ["user", "最近在研究大语言模型的应用"],
        ["assistant", "LLM确实是当前的热点技术。"]
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

                # 检查缓冲区状态
                status = await memobase.detect_buffer_full_or_not(user_id, BlobType.chat)
                print(f"   - 缓冲区状态: {'已满' if status['is_full'] else '未满'} "
                      f"(待处理: {len(status['buffer_full_ids'])} 个)")

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
        return True
        
    except LindormMemobaseError as e:
        print(f"✗ 缓冲区管理测试失败（API错误）: {e}")
        return False
    except Exception as e:
        print(f"✗ 缓冲区管理测试失败（系统错误）: {e}")
        return False


async def main():
    """主测试函数"""
    print("LindormMemobase API 完整测试")
    print("=" * 50)
    
    # 检查环境配置
    if not await check_environment():
        print("\n⚠️  环境配置不完整，部分测试可能无法正常运行")
    
    # 创建唯一的用户ID用于测试
    user_id = f"test_user_{uuid.uuid4().hex[:8]}"
    print(f"\n测试用户ID: {user_id}")
    
    # 统计测试结果
    test_results = []
    
    try:
        # 初始化
        memobase = await test_initialization()
        if not memobase:
            print("\n✗ 初始化失败，无法继续测试")
            return
        
        print("\n✓ LindormMemobase 初始化成功")
        
        # 运行各项测试
        test_results.append(await test_memory_extraction(memobase, user_id))
        test_results.append(await test_user_profiles(memobase, user_id))
        test_results.append(await test_event_management(memobase, user_id))
        test_results.append(await test_context_generation(memobase, user_id))
        test_results.append(await test_buffer_management(memobase, user_id))
        
        # 输出测试总结
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        
        print("\n" + "=" * 50)
        print("测试总结")
        print("=" * 50)
        print(f"通过测试: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！")
        elif passed_tests > 0:
            print("⚠️ 部分测试通过")
        else:
            print("❌ 所有测试失败")
            
        print("\n注意：如果测试失败，请检查：")
        print("1. 数据库连接配置是否正确")
        print("2. API密钥是否有效")
        print("3. Lindorm服务是否正在运行")
        
    except Exception as e:
        print(f"\n测试过程中出现未预期的错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())