#!/usr/bin/env python3
"""演示 iFlow SDK 自动启动功能

这个脚本展示了如何使用 iFlow SDK 的自动进程管理功能。
SDK 会自动：
1. 检测 iFlow 是否已安装
2. 启动 iFlow 进程（如果没有运行）
3. 找到可用端口
4. 在退出时自动清理进程
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import logging

from src.iflow_sdk import IFlowClient, IFlowOptions

# 设置日志级别以查看详细信息
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


async def example_auto_start():
    """演示自动启动功能"""
    
    print("=" * 60)
    print("iFlow SDK 自动启动演示")
    print("=" * 60)
    
    # 方式 1: 使用默认设置（自动启动）
    print("\n📋 方式 1: 默认设置（自动启动）")
    print("当检测到 iFlow 未运行时，SDK 会自动启动它")
    
    try:
        # 默认会自动启动 iFlow
        async with IFlowClient() as client:
            print("✅ 客户端已连接!")
            print("   iFlow 进程已自动启动（如果之前未运行）")
            
            # 发送测试消息
            await client.send_message("Hello, iFlow! 这是自动启动的演示。")
            print("✅ 消息已发送")
            
            # 等待一些响应
            timeout = 5
            print(f"   等待响应 ({timeout}秒)...")
            
            try:
                async with asyncio.timeout(timeout):
                    async for message in client.receive_messages():
                        print(f"   收到消息: {type(message).__name__}")
                        # 处理几条消息后退出
                        break
            except asyncio.TimeoutError:
                print("   超时，继续...")
                
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print("\n✨ 客户端已关闭，iFlow 进程已自动清理")
    
    # 方式 2: 自定义端口
    print("\n" + "=" * 60)
    print("📋 方式 2: 自定义端口")
    
    options = IFlowOptions(
        auto_start_process=True,
        process_start_port=9500,  # 使用自定义起始端口
    )
    
    try:
        async with IFlowClient(options) as client:
            print(f"✅ 客户端已连接到自定义端口!")
            print(f"   URL: {client.options.url}")
            
            await client.send_message("使用自定义端口的测试")
            print("✅ 消息已发送")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 方式 3: 禁用自动启动
    print("\n" + "=" * 60)
    print("📋 方式 3: 禁用自动启动")
    print("当你想连接到已经运行的 iFlow 实例时")
    
    options = IFlowOptions(
        auto_start_process=False,  # 禁用自动启动
        url="ws://localhost:8090/acp"  # 指定已运行的 iFlow URL
    )
    
    try:
        async with IFlowClient(options) as client:
            print("✅ 连接到已运行的 iFlow 实例")
            await client.send_message("连接到现有实例")
            
    except Exception as e:
        print(f"⚠️ 预期的错误（如果 iFlow 未在该端口运行）: {type(e).__name__}")


async def example_process_manager():
    """直接使用进程管理器"""
    
    print("\n" + "=" * 60)
    print("直接使用进程管理器")
    print("=" * 60)
    
    from src.iflow_sdk._internal.process_manager import IFlowProcessManager, IFlowNotInstalledError
    
    try:
        # 创建进程管理器
        manager = IFlowProcessManager(start_port=10000)
        
        # 使用上下文管理器自动管理生命周期
        async with manager as pm:
            print(f"✅ iFlow 进程已启动")
            print(f"   URL: {pm.url}")
            print(f"   端口: {pm.port}")
            
            # 进程会在这里运行
            await asyncio.sleep(2)
            
        print("✅ iFlow 进程已自动停止")
        
    except IFlowNotInstalledError as e:
        print(f"❌ iFlow 未安装:\n{e}")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         iFlow SDK 自动启动功能演示                     ║
    ║                                                        ║
    ║  SDK 会自动管理 iFlow 进程的生命周期                  ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # 运行演示
    asyncio.run(example_auto_start())
    asyncio.run(example_process_manager())
    
    print("\n" + "=" * 60)
    print("✨ 演示完成!")
    print("=" * 60)
    print("\n重要功能:")
    print("1. ✅ 自动检测 iFlow 是否安装")
    print("2. ✅ 自动启动 iFlow 进程")
    print("3. ✅ 自动查找可用端口")
    print("4. ✅ 退出时自动清理进程")
    print("5. ✅ 支持自定义端口范围")
    print("6. ✅ 可以禁用自动启动功能")