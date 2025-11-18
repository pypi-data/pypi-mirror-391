# iFlow CLI SDK Python API 参考文档

## 完整 API 索引

### 核心模块
- [`iflow_sdk.client`](#client-模块) - 客户端实现
- [`iflow_sdk.query`](#query-模块) - 便捷查询函数
- [`iflow_sdk.types`](#types-模块) - 类型定义
- [`iflow_sdk.exceptions`](#exceptions-模块) - 异常类

### 内部模块
- [`iflow_sdk._internal.protocol`](#protocol-模块) - ACP 协议实现
- [`iflow_sdk._internal.transport`](#transport-模块) - WebSocket 传输
- [`iflow_sdk._internal.file_handler`](#file_handler-模块) - 文件系统处理
- [`iflow_sdk._internal.process_manager`](#process_manager-模块) - 进程管理

---

## client 模块

### IFlowClient 类

主要的客户端类，提供与 iFlow 的完整交互功能。

```python
class IFlowClient:
    """iFlow 客户端，提供与 iFlow CLI 的双向通信"""
```

#### 构造函数

```python
def __init__(self, options: Optional[IFlowOptions] = None) -> None:
    """
    初始化 iFlow 客户端
    
    参数:
        options: 配置选项，如果为 None 则使用默认配置
    
    示例:
        client = IFlowClient()
        client = IFlowClient(IFlowOptions(debug=True))
    """
```

#### 方法

##### connect()

```python
async def connect(self) -> None:
    """
    连接到 iFlow 服务
    
    如果启用了 auto_start_process，会自动启动 iFlow 进程。
    
    异常:
        ConnectionError: 连接失败
        ProcessStartError: 进程启动失败
    
    示例:
        await client.connect()
    """
```

##### disconnect()

```python
async def disconnect(self) -> None:
    """
    断开与 iFlow 的连接
    
    如果启用了进程管理，会自动停止 iFlow 进程。
    
    示例:
        await client.disconnect()
    """
```

##### send_message()

```python
async def send_message(
    self,
    content: str,
    files: Optional[List[Union[str, Path]]] = None
) -> None:
    """
    发送消息到 iFlow
    
    参数:
        content: 消息内容
        files: 要包含的文件路径列表
    
    异常:
        NotConnectedError: 未连接
        MessageSendError: 发送失败
    
    示例:
        await client.send_message("你好")
        await client.send_message("分析这个文件", files=["main.py"])
    """
```

##### receive_messages()

```python
async def receive_messages(self) -> AsyncIterator[Message]:
    """
    接收来自 iFlow 的消息流
    
    返回:
        异步迭代器，产生各种消息类型
    
    异常:
        NotConnectedError: 未连接
        ReceiveError: 接收失败
    
    示例:
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                print(message.chunk.text)
            elif isinstance(message, TaskFinishMessage):
                break
    """
```

##### interrupt()

```python
async def interrupt(self) -> None:
    """
    中断当前正在进行的生成
    
    异常:
        NotConnectedError: 未连接
        InterruptError: 中断失败
    
    示例:
        await client.interrupt()
    """
```

##### respond_to_tool_confirmation()

```python
async def respond_to_tool_confirmation(
    self,
    request_id: int,
    option_id: str
) -> None:
    """
    响应工具确认请求
    
    参数:
        request_id: 来自 ToolConfirmationRequestMessage 的 request_id
        option_id: 选择的选项 ID（例如 "proceed_once", "proceed_always"）
    
    示例:
        await client.respond_to_tool_confirmation(
            message.request_id,
            "proceed_once"
        )
    """
```

##### cancel_tool_confirmation()

```python
async def cancel_tool_confirmation(self, request_id: int) -> None:
    """
    取消/拒绝工具确认请求
    
    参数:
        request_id: 来自 ToolConfirmationRequestMessage 的 request_id
    
    示例:
        await client.cancel_tool_confirmation(message.request_id)
    """
```

---

## query 模块

提供简单的查询函数，无需管理客户端生命周期。

### query()

```python
async def query(
    prompt: str,
    *,
    files: Optional[List[Union[str, Path]]] = None,
    agent_id: Optional[str] = None,
    sandbox_mode: bool = False,
    auth_token: Optional[str] = None,
    url: Optional[str] = None,
    timeout: float = 30.0
) -> str:
    """
    执行一次性查询并返回完整响应
    
    参数:
        prompt: 查询提示
        files: 要包含的文件列表
        agent_id: 使用的 Agent ID
        sandbox_mode: 是否使用沙盒模式
        auth_token: 认证令牌
        url: iFlow 服务 URL
        timeout: 超时时间（秒）
    
    返回:
        完整的响应文本
    
    异常:
        QueryError: 查询失败
        TimeoutError: 查询超时
    
    示例:
        response = await query("解释递归")
        response = await query("分析代码", files=["main.py"])
    """
```

### query_stream()

```python
async def query_stream(
    prompt: str,
    *,
    files: Optional[List[Union[str, Path]]] = None,
    agent_id: Optional[str] = None,
    sandbox_mode: bool = False,
    auth_token: Optional[str] = None,
    url: Optional[str] = None,
    timeout: float = 30.0
) -> AsyncIterator[str]:
    """
    执行查询并流式返回响应
    
    参数:
        prompt: 查询提示
        files: 要包含的文件列表
        agent_id: 使用的 Agent ID
        sandbox_mode: 是否使用沙盒模式
        auth_token: 认证令牌
        url: iFlow 服务 URL
        timeout: 超时时间（秒）
    
    返回:
        异步迭代器，产生响应文本片段
    
    异常:
        QueryError: 查询失败
        TimeoutError: 查询超时
    
    示例:
        async for chunk in query_stream("写一个故事"):
            print(chunk, end="")
    """
```

### query_sync()

```python
def query_sync(
    prompt: str,
    **kwargs
) -> str:
    """
    同步版本的 query 函数
    
    参数:
        prompt: 查询提示
        **kwargs: 传递给 query() 的其他参数
    
    返回:
        完整的响应文本
    
    示例:
        response = query_sync("你好")
    """
```

---

## types 模块

### IFlowOptions

```python
@dataclass
class IFlowOptions:
    """iFlow 客户端配置选项"""
    
    # 连接配置
    url: str = "ws://localhost:8090/acp"
    cwd: str = field(default_factory=lambda: os.getcwd())
    mcp_servers: List[McpServer] = field(default_factory=list)
    
    # 权限控制
    approval_mode: ApprovalMode = ApprovalMode.YOLO
    auto_approve_types: List[str] = field(default_factory=lambda: ["edit", "fetch"])
    
    # 会话配置
    session_settings: Optional[SessionSettings] = None
    hooks: Optional[List[Hook]] = None
    commands: Optional[List[Command]] = None
    agents: Optional[List[Agent]] = None
    
    # 文件系统访问
    file_access: bool = False
    file_allowed_dirs: Optional[List[str]] = None
    file_read_only: bool = False
    file_max_size: int = 10 * 1024 * 1024  # 10MB
    
    # 进程管理
    auto_start_process: bool = True
    process_start_port: int = 8090
    
    # 性能配置
    timeout: float = 30.0
    log_level: str = "INFO"
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### ApprovalMode

```python
class ApprovalMode(str, Enum):
    """审批模式枚举 - 控制 iFlow 工具调用的审批行为
    
    这个模式控制 iFlow 如何处理工具调用权限：
    - DEFAULT: iFlow 会为每个工具调用请求用户确认（通过 ACP 协议）
    - AUTO_EDIT: iFlow 自动执行所有工具，不请求确认
    - YOLO: 自动执行所有工具，并在错误时自动回退
    - PLAN: 仅允许只读工具，阻止写操作
    
    注意：SDK 通过 session_settings.permission_mode 将此模式传递给 iFlow。
    iFlow 的 CoreToolScheduler 根据此模式决定是否调用 requestPermission()。
    """
    
    DEFAULT = "default"      # 请求每个工具的确认（调用 requestPermission）
    AUTO_EDIT = "autoEdit"   # 自动执行所有工具（无 requestPermission）
    YOLO = "yolo"            # 自动执行并自动回退
    PLAN = "plan"            # 仅允许只读工具
```

### SessionSettings

```python
@dataclass
class SessionSettings:
    """会话高级设置"""
    
    allowed_tools: Optional[List[str]] = None  # 允许的工具列表
    system_prompt: Optional[str] = None  # 系统提示词
    model: Optional[str] = None  # 使用的模型
    max_turns: Optional[int] = None  # 最大轮次数
    disallowed_tools: Optional[List[str]] = None  # 禁用的工具列表
    add_dirs: Optional[List[str]] = None  # 额外的工作目录
```

### McpServer

```python
@dataclass
class McpServer:
    """MCP (Model Context Protocol) 服务器配置"""
    
    name: str  # 服务器名称
    transport: Literal["stdio", "sse", "ipc"]  # 传输方式
    command: Optional[str] = None  # 启动命令（stdio/ipc）
    args: Optional[List[str]] = None  # 命令参数
    url: Optional[str] = None  # 服务器URL（sse）
    env: Optional[Dict[str, str]] = None  # 环境变量
```

### HookEventType

```python
class HookEventType(str, Enum):
    """钩子事件类型"""
    
    BEFORE_PROMPT = "beforePrompt"  # 提示词发送前
    AFTER_RESPONSE = "afterResponse"  # 响应后
    TOOL_CALL = "toolCall"  # 工具调用时
    ERROR = "error"  # 错误发生时
```

### Hook

```python
@dataclass
class Hook:
    """生命周期钩子配置"""
    
    event: HookEventType  # 事件类型
    command: str  # 执行的命令
    description: Optional[str] = None  # 钩子描述
    async_exec: bool = False  # 是否异步执行
```

### Command

```python
@dataclass
class Command:
    """自定义命令配置"""
    
    name: str  # 命令名称
    description: str  # 命令描述
    execute: str  # 执行的命令或脚本
    args: Optional[List[str]] = None  # 命令参数
```

### Agent

```python
@dataclass
class Agent:
    """专用代理配置"""
    
    id: str  # 代理ID
    name: str  # 代理名称
    description: str  # 代理描述
    system_prompt: Optional[str] = None  # 系统提示词
    tools: Optional[List[str]] = None  # 可用工具
    model: Optional[str] = None  # 使用的模型
    temperature: Optional[float] = None  # 温度参数
```

### 消息类型

#### UserMessage

```python
@dataclass
class UserMessage:
    """用户输入消息"""
    content: str
    files: Optional[List[str]] = None
    timestamp: Optional[datetime] = None
```

#### AgentInfo

```python
@dataclass
class AgentInfo:
    """代理信息，从 iFlow 的 agentId 解析。
    
    包含从 iFlow 协议提取的核心代理识别字段。
    """
    
    # 核心字段
    agent_id: str                           # 来自 iFlow ACP 的原始 agentId
    agent_index: Optional[int] = None       # 任务中的代理索引
    task_id: Optional[str] = None           # 来自 agentId 的任务/调用 ID
    timestamp: Optional[int] = None         # 创建/事件时间戳
    
    @classmethod
    def parse_agent_id(cls, agent_id: str) -> Dict[str, Optional[str]]:
        """解析 iFlow agentId 格式。
        
        iFlow 生成的 agentId 格式：subagent-[taskId|instanceId]-{index}-{timestamp}
        
        Args:
            agent_id: 来自 iFlow 的代理 ID 字符串
            
        Returns:
            包含解析组件的字典：task_id, agent_index, timestamp
            
        Examples:
            >>> AgentInfo.parse_agent_id("subagent-task-abc123-2-1735123456789")
            {'task_id': 'task-abc123', 'agent_index': '2', 'timestamp': '1735123456789'}
        """
    
    @classmethod
    def from_acp_data(cls, acp_data: Dict[str, Any]) -> Optional['AgentInfo']:
        """从 ACP session_update 数据创建 AgentInfo。
        
        Args:
            acp_data: 包含 agentId 和其他字段的完整 ACP 消息数据
            
        Returns:
            AgentInfo 实例，如果未找到有效代理数据则返回 None
        """
    
    @classmethod 
    def from_agent_id_only(cls, agent_id: str) -> Optional['AgentInfo']:
        """仅从代理 ID 创建最小的 AgentInfo。
        
        当只有 agentId 可用时很有用（最常见的情况）。
        
        Args:
            agent_id: 来自 iFlow 的代理 ID 字符串
            
        Returns:
            包含从 agentId 解析字段的 AgentInfo 实例
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，排除 None 值。
        
        Returns:
            仅包含非 None 字段的字典表示
        """
```

#### AssistantMessage

```python
@dataclass
class AssistantMessage:
    """AI 助手响应消息"""
    chunk: AssistantMessageChunk
    agent_id: Optional[str] = None
    agent_info: Optional[AgentInfo] = None
```

#### TextChunk

```python
@dataclass
class TextChunk:
    """文本片段"""
    text: str
    type: str = "text"
```

#### ToolCallMessage

```python
@dataclass
class ToolCallMessage:
    """工具调用消息"""
    id: str
    label: str
    icon: Icon
    status: ToolCallStatus
    tool_name: Optional[str] = None  # 协议中新增的字段
    content: Optional[ToolCallContent] = None
    locations: Optional[List[ToolCallLocation]] = None
    confirmation: Optional[ToolCallConfirmation] = None
    agent_id: Optional[str] = None
    agent_info: Optional[AgentInfo] = None
    
    # 运行时动态添加的字段（通过 client.py）
    args: Optional[Dict[str, Any]] = None      # 工具参数（动态添加）
    output: Optional[str] = None               # 工具输出（动态添加）
```

#### ToolCallStatus

```python
class ToolCallStatus(Enum):
    """工具调用状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

#### ToolResponseMessage

```python
@dataclass
class ToolResponseMessage:
    """工具响应消息"""
    tool_id: str
    result: Any
    error: Optional[str] = None
```

#### TaskFinishMessage

```python
@dataclass
class TaskFinishMessage:
    """任务完成消息"""
    stop_reason: Optional[StopReason] = None  # 停止原因枚举
```

#### StopReason

```python
class StopReason(str, Enum):
    """停止原因枚举"""
    END_TURN = "end_turn"  # 模型完成响应
    MAX_TOKENS = "max_tokens"  # 达到最大令牌限制
    REFUSAL = "refusal"  # 代理拒绝继续
    CANCELLED = "cancelled"  # 客户端取消
    ERROR = "error"  # 执行出错
```

#### PlanMessage

```python
@dataclass
class PlanMessage:
    """任务计划消息"""
    entries: List[PlanEntry]  # 计划条目列表
```

#### PlanEntry

```python
@dataclass
class PlanEntry:
    """计划条目"""
    content: str  # 任务内容
    priority: Literal["high", "medium", "low"]  # 优先级
    status: Literal["pending", "in_progress", "completed"]  # 状态
```

#### TokenUsage

```python
@dataclass
class TokenUsage:
    """令牌使用统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
```

#### ErrorMessage

```python
@dataclass
class ErrorMessage:
    """错误消息"""
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
```

#### InterruptMessage

```python
@dataclass
class InterruptMessage:
    """中断消息"""
    reason: str
    timestamp: Optional[datetime] = None
```

---

## exceptions 模块

### 异常类层次

```python
IFlowError  # 基础异常类
├── ConnectionError  # 连接相关错误
│   ├── NotConnectedError  # 未连接
│   └── ConnectionTimeoutError  # 连接超时
├── ProcessError  # 进程相关错误
│   ├── ProcessStartError  # 启动失败
│   └── ProcessNotFoundError  # iFlow 未安装
├── ProtocolError  # 协议相关错误
│   ├── InitializationError  # 初始化失败
│   ├── AuthenticationError  # 认证失败
│   └── SessionError  # 会话错误
├── MessageError  # 消息相关错误
│   ├── MessageSendError  # 发送失败
│   └── ReceiveError  # 接收失败
└── PermissionError  # 权限相关错误
```

### 使用示例

```python
from src.iflow_sdk._errors import (
    IFlowError,
    ConnectionError,
    ProcessNotFoundError
)

try:
    async with IFlowClient() as client:
        await client.send_message("Hello")
except ProcessNotFoundError:
    print("请先安装 iFlow: npm install -g @ifloworg/cli")
except ConnectionError as e:
    print(f"连接失败: {e}")
except IFlowError as e:
    print(f"iFlow 错误: {e}")
```

---

## protocol 模块

### ACPProtocol 类

实现 Agent Communication Protocol。

```python
class ACPProtocol:
    """ACP 协议实现"""
    
    async def initialize(
        self,
        version: int = 1,
        client_info: Optional[Dict] = None
    ) -> Dict:
        """初始化协议连接"""
    
    async def authenticate(
        self,
        method: str = "iflow",
        token: Optional[str] = None
    ) -> Dict:
        """认证连接"""
    
    async def create_session(
        self,
        cwd: Optional[str] = None,
        agent_id: Optional[str] = None
    ) -> str:
        """创建新会话，返回会话 ID"""
    
    async def send_prompt(
        self,
        content: str,
        files: Optional[List[Dict]] = None
    ) -> None:
        """发送提示到会话"""
    
    async def interrupt_session(self) -> None:
        """中断当前会话"""
    
    async def handle_permission_request(
        self,
        request: Dict
    ) -> str:
        """处理权限请求"""
```

---

## transport 模块

### WebSocketTransport 类

WebSocket 传输层实现。

```python
class WebSocketTransport:
    """WebSocket 传输层"""
    
    def __init__(
        self,
        url: str,
        timeout: float = 30.0,
        ping_interval: float = 10.0,
        max_message_size: int = 10 * 1024 * 1024
    ):
        """初始化传输层"""
    
    async def connect(self) -> None:
        """建立 WebSocket 连接"""
    
    async def disconnect(self) -> None:
        """断开连接"""
    
    async def send(self, data: Dict) -> None:
        """发送数据"""
    
    async def receive(self) -> Dict:
        """接收数据"""
    
    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
```

---

## file_handler 模块

### FileHandler 类

处理文件系统操作请求。

```python
class FileHandler:
    """文件系统处理器"""
    
    def __init__(
        self,
        allowed_directories: List[str],
        read_only: bool = False,
        file_size_limit: int = 10 * 1024 * 1024
    ):
        """初始化文件处理器"""
    
    async def handle_read(
        self,
        path: str
    ) -> str:
        """处理文件读取请求"""
    
    async def handle_write(
        self,
        path: str,
        content: str
    ) -> None:
        """处理文件写入请求"""
    
    async def handle_list(
        self,
        directory: str
    ) -> List[str]:
        """处理目录列表请求"""
    
    def is_path_allowed(
        self,
        path: str
    ) -> bool:
        """检查路径是否在白名单中"""
```

---

## process_manager 模块

### IFlowProcessManager 类

管理 iFlow CLI 进程生命周期。

```python
class IFlowProcessManager:
    """iFlow 进程管理器"""
    
    def __init__(
        self,
        start_port: int = 8090,
        max_port_attempts: int = 10
    ):
        """
        初始化进程管理器
        
        参数:
            start_port: 起始端口号
            max_port_attempts: 最大端口尝试次数
        """
    
    async def start(self) -> str:
        """
        启动 iFlow 进程
        
        返回:
            WebSocket URL
        
        异常:
            ProcessNotFoundError: iFlow 未安装
            ProcessStartError: 启动失败
        """
    
    async def stop(self) -> None:
        """
        停止 iFlow 进程
        
        优雅关闭，先发送 SIGTERM，等待后发送 SIGKILL。
        """
    
    def is_running(self) -> bool:
        """检查进程是否运行中"""
    
    @staticmethod
    def find_iflow() -> Optional[str]:
        """
        查找 iFlow 可执行文件路径
        
        返回:
            iFlow 路径，如果未找到返回 None
        """
    
    @staticmethod
    def find_available_port(
        start_port: int,
        max_attempts: int = 10
    ) -> Optional[int]:
        """
        查找可用端口
        
        参数:
            start_port: 起始端口
            max_attempts: 最大尝试次数
        
        返回:
            可用端口号，如果未找到返回 None
        """
```

---

## 完整使用示例

### 基础查询

```python
import asyncio
from src.iflow_sdk import query, query_stream

# 简单查询
async def simple_query():
    response = await query("什么是 Python?")
    print(response)

# 流式查询
async def stream_query():
    async for chunk in query_stream("写一个冒泡排序"):
        print(chunk, end="", flush=True)

asyncio.run(simple_query())
```

### 高级客户端

```python
from src.iflow_sdk import IFlowClient, IFlowOptions, ApprovalMode, AgentInfo
from src.iflow_sdk import AssistantMessage, ToolCallMessage, TaskFinishMessage

async def advanced_client():
    options = IFlowOptions(
        auto_start_process=True,
        approval_mode=ApprovalMode.YOLO,  # 默认：自动执行并回退
        log_level="INFO"
    )
    
    async with IFlowClient(options) as client:
        # 发送带文件的消息
        await client.send_message(
            "分析这些文件的代码质量",
            files=["src/main.py", "src/utils.py"]
        )
        
        # 处理响应
        async for message in client.receive_messages():
            if isinstance(message, AssistantMessage):
                print(message.chunk.text, end="")
                
                # 显示代理信息
                if message.agent_info:
                    print(f"\n[代理 {message.agent_info.agent_index} - 任务 {message.agent_info.task_id}]")
            
            elif isinstance(message, ToolCallMessage):
                print(f"\n🔧 工具: {message.label}")
                
                # 显示代理和工具信息
                if message.agent_info:
                    print(f"   代理: {message.agent_info.agent_id}")
                if hasattr(message, 'args') and message.args:
                    print(f"   参数: {message.args}")
            
            elif isinstance(message, TaskFinishMessage):
                if message.stop_reason:
                    print(f"\n✅ 完成: {message.stop_reason.value}")
                else:
                    print("\n✅ 任务完成")
                break

asyncio.run(advanced_client())
```

### AgentInfo 使用示例

```python
from src.iflow_sdk import AgentInfo

# 解析 iFlow 代理 ID
agent_id = "subagent-task-abc123-2-1735123456789"
agent_info = AgentInfo.from_agent_id_only(agent_id)

print(f"代理 ID: {agent_info.agent_id}")
print(f"任务 ID: {agent_info.task_id}")
print(f"代理索引: {agent_info.agent_index}")
print(f"时间戳: {agent_info.timestamp}")

# 转换为字典
info_dict = agent_info.to_dict()
print(f"字典格式: {info_dict}")

# 从 ACP 数据创建（模拟）
acp_data = {
    "agentId": "subagent-task-def456-1-1735123457000",
    "timestamp": 1735123457000
}
agent_info_from_acp = AgentInfo.from_acp_data(acp_data)
print(f"从 ACP 创建: {agent_info_from_acp}")
```

### 使用新协议特性

```python
from src.iflow_sdk import IFlowClient, IFlowOptions
from src.iflow_sdk.types import (
    ApprovalMode, SessionSettings, McpServer,
    Hook, HookEventType, Command, Agent
)

async def protocol_features():
    # 配置 MCP 服务器
    mcp_servers = [
        McpServer(
            name="filesystem",
            transport="stdio",
            command="mcp-server-filesystem",
            args=["--allowed-dirs", "/tmp"]
        )
    ]
    
    # 配置会话设置
    session_settings = SessionSettings(
        allowed_tools=["read_file", "write_file"],
        system_prompt="You are a helpful coding assistant",
        max_turns=100
    )
    
    # 配置钩子
    hooks = [
        Hook(
            event=HookEventType.BEFORE_PROMPT,
            command="echo 'Starting prompt'",
            description="Log before prompt"
        ),
        Hook(
            event=HookEventType.AFTER_RESPONSE,
            command="notify-send 'Task completed'",
            async_exec=True
        )
    ]
    
    # 配置自定义命令
    commands = [
        Command(
            name="test",
            description="Run tests",
            execute="pytest",
            args=["--verbose"]
        )
    ]
    
    # 配置专用代理
    agents = [
        Agent(
            id="coder",
            name="Code Assistant",
            description="Specialized coding agent",
            system_prompt="You are an expert programmer",
            tools=["edit_file", "run_code"],
            model="claude-3-5-sonnet-20241022"
        )
    ]
    
    # 创建客户端配置
    options = IFlowOptions(
        mcp_servers=mcp_servers,
        session_settings=session_settings,
        hooks=hooks,
        commands=commands,
        agents=agents,
        approval_mode=ApprovalMode.YOLO  # 默认模式：自动执行并回退
    )
    
    async with IFlowClient(options) as client:
        await client.send_message("Help me write a Python script")
        
        async for message in client.receive_messages():
            # 处理消息...
            pass

asyncio.run(protocol_features())
```

### 错误处理

```python
from src.iflow_sdk import IFlowClient
from src.iflow_sdk._errors import (
    ProcessNotFoundError,
    ConnectionTimeoutError,
    IFlowError
)

async def safe_client():
    try:
        async with IFlowClient() as client:
            await client.send_message("Hello")
            
            async for message in client.receive_messages():
                # 处理消息
                pass
                
    except ProcessNotFoundError:
        print("请安装 iFlow: npm install -g @ifloworg/cli")
    
    except ConnectionTimeoutError:
        print("连接超时，请检查 iFlow 服务")
    
    except IFlowError as e:
        print(f"iFlow 错误: {e}")
    
    except Exception as e:
        print(f"未预期的错误: {e}")

asyncio.run(safe_client())
```

### 自定义权限处理

```python
from src.iflow_sdk import IFlowClient, IFlowOptions, ApprovalMode
from src.iflow_sdk import ToolConfirmationRequestMessage

async def custom_permissions():
    options = IFlowOptions(
        approval_mode=ApprovalMode.DEFAULT  # 请求用户确认每个工具
    )
    
    async with IFlowClient(options) as client:
        await client.send_message("创建一个配置文件")
        
        async for message in client.receive_messages():
            if isinstance(message, ToolConfirmationRequestMessage):
                # 自定义逻辑
                tool_kind = message.tool_call.kind
                
                if tool_kind in ["delete", "move"]:
                    # 拒绝危险操作
                    await client.cancel_tool_confirmation(message.request_id)
                    print(f"拒绝: {tool_kind} 操作")
                else:
                    # 批准其他请求
                    await client.respond_to_tool_confirmation(
                        message.request_id,
                        "proceed_once"
                    )
                    print(f"批准: {tool_kind} 操作")
            # ... 处理其他消息

asyncio.run(custom_permissions())
```

---

## 版本历史

### v0.3.0 (当前版本)
- 实现完整 ACP 协议扩展支持
- 添加 SessionSettings 高级会话配置
- 支持 MCP (Model Context Protocol) 服务器
- 添加生命周期钩子系统
- 支持自定义命令和专用代理
- 完全对齐 iFlow 的 ApprovalMode（DEFAULT/AUTO_EDIT/YOLO/PLAN）
- 移除 SDK 侧的 PermissionMode，使用 iFlow 的 ApprovalMode
- 默认模式改为 YOLO（自动执行并回退）
- 新增工具确认 API：respond_to_tool_confirmation() 和 cancel_tool_confirmation()
- 支持 StopReason 和改进 Plan 消息处理

### v0.2.0
- 添加自动进程管理功能
- 支持智能端口分配
- 改进错误处理和日志
- 添加更多示例代码

### v0.1.0
- 初始版本
- 基础 ACP 协议支持
- 简单查询和流式响应
- 文件包含功能

---

## 许可证

MIT License