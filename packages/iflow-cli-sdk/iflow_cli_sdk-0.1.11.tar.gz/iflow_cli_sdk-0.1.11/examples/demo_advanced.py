#!/usr/bin/env python3
"""
iFlow SDK 高级功能演示

展示复杂的多轮对话、Agent 使用和工具调用场景
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import List, Optional
from src.iflow_sdk import (
    IFlowClient, 
    IFlowOptions, 
    AssistantMessage, 
    ToolCallMessage,
    TaskFinishMessage,
    ErrorMessage,
    PermissionMode
)


class ConversationDemo:
    """高级对话演示类"""
    
    def __init__(self):
        self.client: Optional[IFlowClient] = None
        self.conversation_history: List[str] = []
        
    async def setup(self):
        """初始化客户端"""
        print("🚀 初始化 iFlow 客户端...")
        
        # 配置选项
        options = IFlowOptions(
            auto_start_process=True,    # 自动启动进程
            process_start_port=11000,   # 使用高端口避免冲突
            permission_mode=PermissionMode.AUTO,  # 自动批准工具调用
            cwd="/Users/shaoqing/PycharmProjects/iflow-cli-sdk-python"  # 设置工作目录
        )
        
        self.client = IFlowClient(options)
        await self.client.connect()
        print(f"✅ 已连接: {self.client.options.url}\n")
        
    async def cleanup(self):
        """清理资源"""
        if self.client:
            await self.client.disconnect()
            print("\n🔄 客户端已断开，进程已清理")
            
    async def send_and_receive(self, prompt: str, show_tools: bool = True) -> str:
        """发送消息并接收完整响应"""
        print(f"👤 用户: {prompt}")
        print("-" * 60)
        
        await self.client.send_message(prompt)
        
        response_text = []
        tool_calls = []
        
        print("🤖 Assistant: ", end="", flush=True)
        
        async for message in self.client.receive_messages():
            if isinstance(message, AssistantMessage):
                if message.chunk.text:
                    text = message.chunk.text
                    print(text, end="", flush=True)
                    response_text.append(text)
                    
            elif isinstance(message, ToolCallMessage):
                if show_tools:
                    if not tool_calls:  # 第一个工具调用时换行
                        print("\n")
                    print(f"   🔧 [工具调用: {message.label}]")
                    tool_calls.append(message.label)
                    
            elif isinstance(message, TaskFinishMessage):
                print("\n")
                break
                
            elif isinstance(message, ErrorMessage):
                print(f"\n❌ 错误: {message.message}")
                break
                
        full_response = "".join(response_text)
        self.conversation_history.append(f"Q: {prompt}\nA: {full_response}")
        
        return full_response
        
    async def demo_code_generation(self):
        """演示1: 复杂的代码生成任务"""
        print("\n" + "="*80)
        print("📝 演示 1: 复杂代码生成 - 创建一个完整的应用")
        print("="*80 + "\n")
        
        # 第一轮：需求分析
        await self.send_and_receive(
            "我想创建一个 Python 的任务管理系统，需要有以下功能：\n"
            "1. 添加任务（标题、描述、优先级、截止日期）\n"
            "2. 列出所有任务\n"
            "3. 标记任务完成\n"
            "4. 删除任务\n"
            "5. 按优先级或截止日期排序\n"
            "6. 数据持久化到 JSON 文件\n"
            "请先帮我设计系统架构，然后实现代码。"
        )
        
        await asyncio.sleep(2)  # 等待一下
        
        # 第二轮：细化需求
        await self.send_and_receive(
            "很好！现在请实现主要的 Task 类和 TaskManager 类，"
            "要包含完整的错误处理和类型提示。"
        )
        
        await asyncio.sleep(2)
        
        # 第三轮：添加功能
        await self.send_and_receive(
            "现在添加一个命令行界面（CLI），让用户可以交互式地使用这个系统。"
            "使用 argparse 或者简单的菜单系统都可以。"
        )
        
    async def demo_analysis_task(self):
        """演示2: 代码分析和优化"""
        print("\n" + "="*80)
        print("🔍 演示 2: 代码分析与优化")
        print("="*80 + "\n")
        
        # 提供一段需要优化的代码
        code = '''
def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates

def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
'''
        
        await self.send_and_receive(
            f"请分析以下 Python 代码的性能问题，并提供优化版本：\n```python\n{code}\n```\n"
            "要求：\n"
            "1. 指出性能瓶颈\n"
            "2. 提供时间复杂度分析\n"
            "3. 给出优化后的代码\n"
            "4. 添加适当的类型提示"
        )
        
        await asyncio.sleep(2)
        
        # 跟进问题
        await self.send_and_receive(
            "能否为优化后的代码编写单元测试？使用 pytest 框架。"
        )
        
    async def demo_project_exploration(self):
        """演示3: 项目探索和理解"""
        print("\n" + "="*80)
        print("🔎 演示 3: 项目代码探索")
        print("="*80 + "\n")
        
        # 探索当前项目
        await self.send_and_receive(
            "请分析当前项目（iflow-cli-sdk-python）的结构，"
            "告诉我：\n"
            "1. 项目的主要模块有哪些？\n"
            "2. 核心功能是什么？\n"
            "3. 有哪些主要的类和它们的职责？"
        )
        
        await asyncio.sleep(2)
        
        # 深入了解特定模块
        await self.send_and_receive(
            "详细解释一下 ACPProtocol 类的工作原理，"
            "特别是它如何处理消息的发送和接收。"
        )
        
    async def demo_debugging_scenario(self):
        """演示4: 调试场景"""
        print("\n" + "="*80)
        print("🐛 演示 4: 调试和问题解决")
        print("="*80 + "\n")
        
        buggy_code = '''
class DataProcessor:
    def __init__(self):
        self.data = []
        
    def add_item(self, item):
        self.data.append(item)
        
    def process_batch(self, items):
        for item in items:
            self.add_item(item)
            if item > 100:
                items.remove(item)  # 问题在这里
        return self.data
        
    def calculate_average(self):
        return sum(self.data) / len(self.data)
'''
        
        await self.send_and_receive(
            f"这段代码有一个隐藏的 bug，请帮我找出并修复：\n"
            f"```python\n{buggy_code}\n```\n"
            "用户报告说处理某些数据时结果不正确。"
            "请：\n"
            "1. 找出 bug\n"
            "2. 解释为什么会出现这个问题\n"
            "3. 提供修复方案\n"
            "4. 编写测试用例来验证修复"
        )
        
    async def demo_system_design(self):
        """演示5: 系统设计"""
        print("\n" + "="*80)
        print("🏗️ 演示 5: 系统架构设计")
        print("="*80 + "\n")
        
        await self.send_and_receive(
            "设计一个分布式日志收集系统，要求：\n"
            "1. 支持多个应用同时写入日志\n"
            "2. 日志要按时间和级别分类存储\n"
            "3. 提供实时查询和历史查询功能\n"
            "4. 要有容错机制\n"
            "5. 考虑性能和扩展性\n\n"
            "请提供：\n"
            "- 系统架构图（用文字描述）\n"
            "- 主要组件说明\n"
            "- 数据流程\n"
            "- 技术选型建议\n"
            "- Python 实现的核心代码框架"
        )
        
        await asyncio.sleep(2)
        
        # 深入某个组件
        await self.send_and_receive(
            "请详细实现日志收集器（Log Collector）组件，"
            "包括：\n"
            "1. 异步收集机制\n"
            "2. 批量发送优化\n"
            "3. 失败重试逻辑\n"
            "4. 背压处理"
        )
        
    async def demo_refactoring(self):
        """演示6: 代码重构"""
        print("\n" + "="*80)
        print("♻️ 演示 6: 代码重构")
        print("="*80 + "\n")
        
        legacy_code = '''
def process_user_data(users):
    result = {}
    for user in users:
        if user['age'] >= 18:
            if user['country'] == 'US':
                if user['subscription'] == 'premium':
                    result[user['id']] = {
                        'name': user['name'],
                        'email': user['email'],
                        'discount': 0.2
                    }
                else:
                    result[user['id']] = {
                        'name': user['name'],
                        'email': user['email'],
                        'discount': 0.1
                    }
            else:
                if user['subscription'] == 'premium':
                    result[user['id']] = {
                        'name': user['name'],
                        'email': user['email'],
                        'discount': 0.15
                    }
                else:
                    result[user['id']] = {
                        'name': user['name'],
                        'email': user['email'],
                        'discount': 0.05
                    }
    return result
'''
        
        await self.send_and_receive(
            f"请重构这段代码，使其更加清晰和可维护：\n"
            f"```python\n{legacy_code}\n```\n"
            "要求：\n"
            "1. 应用设计模式（如策略模式）\n"
            "2. 提高可读性和可测试性\n"
            "3. 添加类型提示\n"
            "4. 遵循 SOLID 原则\n"
            "5. 提供重构前后的对比说明"
        )


async def main():
    """主函数"""
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║       iFlow SDK 高级功能演示 - 复杂场景               ║
    ║                                                        ║
    ║  展示：多轮对话、Agent 使用、工具调用                 ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    demo = ConversationDemo()
    
    try:
        # 初始化
        await demo.setup()
        
        # 运行演示
        demos = [
            ("代码生成", demo.demo_code_generation),
            ("代码分析", demo.demo_analysis_task),
            ("项目探索", demo.demo_project_exploration),
            ("调试场景", demo.demo_debugging_scenario),
            ("系统设计", demo.demo_system_design),
            ("代码重构", demo.demo_refactoring),
        ]
        
        print("请选择演示场景：")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i}. {name}")
        print("  7. 运行所有演示")
        print("  0. 退出")
        
        choice = input("\n请输入选择 (0-7): ").strip()
        
        if choice == "0":
            print("退出演示")
        elif choice == "7":
            # 运行所有演示
            for name, demo_func in demos:
                print(f"\n{'='*80}")
                print(f"开始: {name}")
                print('='*80)
                await demo_func()
                await asyncio.sleep(3)
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            # 运行选定的演示
            idx = int(choice) - 1
            name, demo_func = demos[idx]
            await demo_func()
        else:
            print("无效的选择")
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理
        await demo.cleanup()
        
        print("\n" + "="*80)
        print("📊 演示统计")
        print("-"*80)
        print(f"✅ 对话轮数: {len(demo.conversation_history)}")
        print("✅ 展示功能:")
        print("   • 多轮对话上下文保持")
        print("   • 复杂任务分解")
        print("   • 工具调用（文件操作、代码分析等）")
        print("   • Agent 协作")
        print("   • 自动进程管理")
        print("\n✨ 演示完成！")


if __name__ == "__main__":
    asyncio.run(main())