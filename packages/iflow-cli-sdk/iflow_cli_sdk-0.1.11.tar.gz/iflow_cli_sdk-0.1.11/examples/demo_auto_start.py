#!/usr/bin/env python3
"""
iFlow SDK 自动启动功能演示

这个脚本展示了 SDK 的自动进程管理功能：
1. 自动检测并启动 iFlow
2. 智能端口分配
3. 进程生命周期管理
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.iflow_sdk import IFlowClient, IFlowOptions, AssistantMessage, TaskFinishMessage

async def demo():
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         iFlow SDK 自动启动功能演示                     ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    print("📌 功能特点:")
    print("   • 自动检测 iFlow 是否安装")
    print("   • 自动启动 iFlow 进程")
    print("   • 智能查找可用端口")
    print("   • 退出时自动清理进程")
    print("\n" + "=" * 60 + "\n")
    
    # 演示1: 基本使用 - SDK 会自动处理一切
    print("📋 演示 1: 基本使用（全自动）")
    print("-" * 40)
    
    try:
        # 最简单的使用方式 - SDK 自动管理 iFlow 进程
        async with IFlowClient() as client:
            print(f"✅ 已连接到 iFlow")
            print(f"   URL: {client.options.url}")
            
            # 发送消息
            await client.send_message("1+1等于几？")
            print("📤 发送: 1+1等于几？")
            
            # 接收响应
            print("📥 响应: ", end="")
            async for msg in client.receive_messages():
                if isinstance(msg, AssistantMessage):
                    if msg.chunk.text:
                        print(msg.chunk.text, end="")
                elif isinstance(msg, TaskFinishMessage):
                    print("\n✅ 响应完成")
                    break
                    
        print("🔄 客户端关闭，iFlow 进程已自动清理\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}\n")
    
    # 演示2: 自定义配置
    print("=" * 60)
    print("\n📋 演示 2: 自定义端口配置")
    print("-" * 40)
    
    try:
        # 使用自定义端口范围
        options = IFlowOptions(
            auto_start_process=True,  # 启用自动启动
            process_start_port=10000  # 从端口 10000 开始查找
        )
        
        async with IFlowClient(options) as client:
            print(f"✅ 已连接到自定义端口")
            print(f"   URL: {client.options.url}")
            
            await client.send_message("你好")
            print("📤 发送: 你好")
            
            # 简单等待一点响应
            await asyncio.sleep(1)
            print("✅ 测试成功")
            
        print("🔄 进程已清理\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}\n")
    
    # 演示3: 连接到已存在的 iFlow
    print("=" * 60)
    print("\n📋 演示 3: 连接到已运行的 iFlow（禁用自动启动）")
    print("-" * 40)
    
    # 禁用自动启动，连接到指定端口
    options = IFlowOptions(
        auto_start_process=False,
        url="ws://localhost:8090/acp"
    )
    
    try:
        async with IFlowClient(options) as client:
            print(f"✅ 连接到已存在的 iFlow 实例")
            print(f"   URL: {client.options.url}")
            
    except Exception as e:
        print(f"⚠️ 连接失败（如果端口 8090 没有 iFlow 运行）")
        print(f"   这是预期的行为 - 禁用了自动启动")
    
    print("\n" + "=" * 60)
    print("\n✨ 演示完成！")
    print("\n📝 总结:")
    print("   1. SDK 默认会自动管理 iFlow 进程")
    print("   2. 可以自定义端口范围")
    print("   3. 可以禁用自动启动，连接到现有实例")
    print("   4. 使用 async with 语法自动清理资源")

if __name__ == "__main__":
    asyncio.run(demo())