# iFlow Python SDK

[![PyPI Version](https://img.shields.io/pypi/v/iflow-cli-sdk)](https://pypi.org/project/iflow-cli-sdk/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![WebSocket Protocol](https://img.shields.io/badge/protocol-ACP%20v1-orange)](docs/protocol.md)

[English](README.md) | [中文](README_CN.md)

一个强大的 Python SDK，使用代理通信协议（ACP）与 iFlow CLI 进行交互。构建具有对话、工具执行和子代理编排完全控制的 AI 驱动应用程序。

**✨ 核心特性：SDK 自动管理 iFlow 进程 - 无需手动配置！**

## 功能特性

- 🚀 **自动进程管理** - 零配置设置！SDK 自动启动和管理 iFlow CLI
- 🔌 **智能端口检测** - 自动查找可用端口，无冲突
- 🔄 **双向通信** - 实时流式传输消息和响应
- 🛠️ **工具调用管理** - 通过细粒度权限处理和控制工具执行
- 🤖 **子代理支持** - 通过 `agent_id` 传播跟踪和管理多个 AI 代理
- 📋 **任务规划** - 接收和处理结构化任务计划
- 🔍 **原始数据访问** - 调试和检查协议级消息
- ⚡ **异步支持** - 现代异步 Python，完整类型提示
- 🎯 **简单和高级 API** - 从一行查询到复杂对话管理
- 📦 **完整 ACP v1 协议** - 代理通信协议的完整实现
- 🚦 **高级审批模式** - 包括 DEFAULT、AUTO_EDIT、YOLO 和 PLAN 模式
- 🔗 **MCP 服务器集成** - 支持模型上下文协议服务器
- 🪝 **生命周期钩子** - 在对话的不同阶段执行命令
- 🎮 **会话设置** - 对模型行为和工具的细粒度控制
- 🤖 **自定义代理** - 定义具有自定义提示和工具的专用代理

## 安装

### 1. 安装 iFlow CLI

如果您还没有安装 iFlow CLI：

**Mac/Linux/Ubuntu:**
```bash
bash -c "$(curl -fsSL https://gitee.com/iflow-ai/iflow-cli/raw/main/install.sh)"
```

**Windows:**
```bash
npm install -g @iflow-ai/iflow-cli@latest
```

### 2. 安装 SDK

**从 PyPI 安装（推荐）：**

```bash
pip install iflow-cli-sdk
```

**或从源代码安装：**

```bash
git clone https://github.com/yourusername/iflow-cli-sdk-python.git
cd iflow-cli-sdk-python
pip install -e .
```

## 快速开始

SDK **自动管理 iFlow 进程** - 无需手动设置！

### 默认用法（自动进程管理）

```python
import asyncio
from iflow_sdk import IFlowClient

async def main():
    # SDK 自动：
    # 1. 检测 iFlow 是否已安装
    # 2. 如果未运行则启动 iFlow 进程
    # 3. 查找可用端口
    # 4. 退出时清理
    async with IFlowClient() as client:
        await client.send_message("Hello, iFlow!")
        
        async for message in client.receive_messages():
            print(message)
            # 处理消息...

asyncio.run(main())
```

**无需手动启动 iFlow！** SDK 为您处理一切。

### 高级：手动进程控制

如果您需要自己管理 iFlow：

```python
import asyncio
from iflow_sdk import IFlowClient, IFlowOptions

async def main():
    # 禁用自动进程管理
    options = IFlowOptions(
        auto_start_process=False,
        url="ws://localhost:8090/acp"  # 连接到现有的 iFlow
    )
    
    async with IFlowClient(options) as client:
        await client.send_message("Hello, iFlow!")

asyncio.run(main())
```

**注意：** 手动模式需要您单独启动 iFlow：
```bash
iflow --experimental-acp --port 8090
```

### 简单示例

#### 简单查询

```python
import asyncio
from iflow_sdk import query

async def main():
    response = await query("法国的首都是哪里？")
    print(response)  # "法国的首都是巴黎。"

asyncio.run(main())
```

#### 交互式对话

```python
import asyncio
from iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage

async def chat():
    async with IFlowClient() as client:
        await client.send_message("解释量子计算")
        
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                print(message.chunk.text, end="", flush=True)
            elif isinstance(message, TaskFinishMessage):
                break

asyncio.run(chat())
```

#### 工具调用控制与代理信息

```python
import asyncio
from iflow_sdk import IFlowClient, IFlowOptions, ApprovalMode, ToolCallMessage, TaskFinishMessage, AgentInfo

async def main():
    options = IFlowOptions(approval_mode=ApprovalMode.YOLO)  # 默认：自动执行并回退
    
    async with IFlowClient(options) as client:
        await client.send_message("创建一个名为 test.txt 的文件")
        
        async for message in client.receive_messages():
            if isinstance(message, ToolCallMessage):
                print(f"请求的工具: {message.tool_name}")
                print(f"工具状态: {message.status}")
                
                # 访问代理信息
                if message.agent_info:
                    print(f"代理 ID: {message.agent_info.agent_id}")
                    print(f"任务 ID: {message.agent_info.task_id}")
                    print(f"代理索引: {message.agent_info.agent_index}")
                
                # 访问工具执行详情（动态添加）
                if hasattr(message, 'args'):
                    print(f"工具参数: {message.args}")
                if hasattr(message, 'output'):
                    print(f"工具输出: {message.output}")
                    
            elif isinstance(message, TaskFinishMessage):
                break

asyncio.run(main())
```

#### 使用 AgentInfo

```python
import asyncio
from iflow_sdk import AgentInfo, IFlowClient, AssistantMessage, CreateAgentConfig, IFlowOptions, ToolCallMessage


async def agent_info_example():
    # 创建Agent配置
    agents = [
        CreateAgentConfig(
            agentType="code-reviewer",
            name="reviewer",
            description="Code review specialist",
            whenToUse="For code review and quality checks",
            allowedTools=["fs", "grep"],
            allowedMcps=["eslint", "prettier"],
            systemPrompt="You are a code review expert.",
            proactive=False,
            location="project"
        ),
        CreateAgentConfig(
            agentType="test-writer",
            name="tester",
            description="Test writing specialist",
            whenToUse="For writing unit and integration tests",
            allowedTools=["fs", "bash"],
            systemPrompt="You are a test writing expert.",
            location="project"
        )
    ]

    print(f"  配置的Agents:")
    for agent in agents:
        print(f"    - {agent.name} ({agent.agentType}): {agent.description}")
        print(f"      位置: {agent.location}, 主动: {agent.proactive}")

    options = IFlowOptions(agents=agents)

    # Use in conversation
    async with IFlowClient(options) as client:
        await client.send_message("$test-writer 写一个单测")

        async for message in client.receive_messages():
            if isinstance(message, ToolCallMessage):
                print(f"tool_name: {message.tool_name}")
                
                # 检查动态添加的 output 属性是否存在
                if hasattr(message, 'output') and message.output:
                    print(f"工具执行结果output: {message.output}")
                
                # 检查动态添加的 args 属性是否存在
                if hasattr(message, 'args') and message.args:
                    print(f"工具参数args: {message.args}")
                    
            elif isinstance(message, AssistantMessage):
                print(message.chunk.text, end="", flush=True)


asyncio.run(agent_info_example())
```

#### 高级协议特性

```python
import asyncio
from iflow_sdk import IFlowClient, IFlowOptions, AgentInfo
from iflow_sdk.types import (
    ApprovalMode, SessionSettings, McpServer, EnvVariable,
    HookCommand, HookEventConfig, HookEventType, CommandConfig, CreateAgentConfig
)

async def advanced_features():
    # 配置 MCP 服务器以扩展功能
    mcp_servers = [
        McpServer(
            name="filesystem",
            command="mcp-server-filesystem",
            args=["--allowed-dirs", "/workspace"],
            env=[EnvVariable(name="DEBUG", value="1")]
        )
    ]
    
    # 配置会话设置以进行细粒度控制
    session_settings = SessionSettings(
        allowed_tools=["read_file", "write_file", "execute_code"],
        system_prompt="你是一位专业的 Python 开发者",
        max_turns=100
    )
    
    # 设置生命周期钩子
    hooks = {
        HookEventType.PRE_TOOL_USE: [HookEventConfig(
            hooks=[HookCommand(
                command="echo '正在处理请求...'",
                timeout=5
            )]
        )]
    }
    
    # 定义自定义命令
    commands = [
        CommandConfig(
            name="test",
            content="pytest --verbose"
        )
    ]
    
    # 定义专用代理
    agents = [
        CreateAgentConfig(
            agentType="python-expert",
            whenToUse="用于 Python 开发任务",
            allowedTools=["edit_file", "run_python", "debug"],
            systemPrompt="你是一位专注于编写清晰、高效代码的 Python 专家",
            name="Python 专家",
            description="专注于 Python 开发"
        )
    ]
    
    options = IFlowOptions(
        mcp_servers=mcp_servers,
        session_settings=session_settings,
        hooks=hooks,
        commands=commands,
        agents=agents
        # approval_mode 默认为 YOLO（自动执行并回退）
    )
    
    async with IFlowClient(options) as client:
        await client.send_message("帮我优化这段 Python 代码")
        # 处理响应...

asyncio.run(advanced_features())
```

## API 参考

### 核心类

- **`IFlowClient`**: 双向通信的主客户端
- **`IFlowOptions`**: 配置选项
- **`RawDataClient`**: 访问原始协议数据

### 消息类型

- **`AssistantMessage`**: AI 助手响应，包含可选的代理信息
- **`ToolCallMessage`**: 工具执行请求，包含执行详情（tool_name, args, output）和代理信息
- **`PlanMessage`**: 带优先级和状态的结构化任务计划
- **`TaskFinishMessage`**: 带停止原因的任务完成信号 (end_turn, max_tokens, refusal, cancelled)

### 代理信息

- **`AgentInfo`**: 从 iFlow 的 agentId 格式提取的代理元数据（agent_id, task_id, agent_index, timestamp）

### 便捷函数

- `query(prompt)`: 简单同步查询
- `query_stream(prompt)`: 流式响应
- `query_sync(prompt)`: 带超时的同步查询

## 项目结构

```
iflow-sdk-python/
├── src/iflow_sdk/
│   ├── __init__.py          # 公共 API 导出
│   ├── client.py            # 主 IFlowClient 实现
│   ├── query.py             # 简单查询函数
│   ├── types.py             # 类型定义和消息
│   ├── raw_client.py        # 原始协议访问
│   └── _internal/
│       ├── protocol.py      # ACP 协议处理器
│       ├── transport.py     # WebSocket 传输层
│       └── launcher.py      # iFlow 进程管理
├── tests/                   # 测试套件
│   ├── test_basic.py        # 基础功能测试
│   └── test_protocol.py     # 协议合规性测试
├── examples/                # 使用示例
│   ├── comprehensive_demo.py
│   ├── quick_start.py
│   └── advanced_client.py
└── docs/                    # 文档
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行覆盖率测试
pytest tests/ --cov=src/iflow_sdk

# 运行特定测试
pytest tests/test_basic.py
```

### 代码质量

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/

# 检查样式
flake8 src/ tests/
```

## 协议支持

SDK 实现了代理通信协议（ACP）v1 并支持完整的扩展功能，包括：

- **会话管理**：创建、加载和管理带有高级设置的对话会话
- **消息类型**：
  - `agent_message_chunk` - 助手响应
  - `agent_thought_chunk` - 内部推理
  - `tool_call` / `tool_call_update` - 工具执行生命周期
  - `plan` - 带优先级的结构化任务规划
  - `user_message_chunk` - 用户消息回显
  - `stop_reason` - 任务完成原因（end_turn、max_tokens、refusal、cancelled）
- **身份验证**：内置 iFlow 身份验证并支持令牌
- **文件系统访问**：可配置限制的读/写文件权限
- **子代理支持**：完整的 `agent_id` 跟踪和管理
- **高级功能**：
  - **MCP 服务器**：集成模型上下文协议服务器以扩展功能
  - **审批模式**：DEFAULT、AUTO_EDIT、YOLO（默认，自动执行并回退）、PLAN 模式
  - **会话设置**：控制允许的工具、系统提示、模型选择
  - **生命周期钩子**：在对话的不同阶段执行命令
  - **自定义命令**：定义和执行自定义命令
  - **专用代理**：创建具有特定专业知识和工具访问权限的代理

## 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解指南。

## 许可证

本项目根据 MIT 许可证授权 - 详情请参阅 [LICENSE](LICENSE) 文件。


---

用 ❤️ 为 AI 开发社区构建