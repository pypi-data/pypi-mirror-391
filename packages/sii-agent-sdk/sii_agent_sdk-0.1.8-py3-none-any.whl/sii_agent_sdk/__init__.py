"""
Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0

SII Agent SDK for Python - 类似 Claude Agent SDK 的 SII 版本
"""

__version__ = "0.1.0"

# 主要 API
from .query import query
from .session import SiiAgentSession
from .session_state import ConversationTurn, SessionState

# from .client import SiiSDKClient  # TODO: 待实现

# 导出类型
from .types import (
    # 配置类型
    AuthType,
    RunModelType,
    SiiAgentOptions,
    # 消息类型
    AssistantMessage,
    CompletedMessage,
    ContentBlock,
    ErrorMessage,
    Message,
    StatusMessage,
    TextBlock,
    ToolResultBlock,
    ToolResultMessage,
    ToolUseBlock,
)

# 导出异常
from .errors import (
    AuthenticationError,
    BridgeConnectionError,
    BridgeNotFoundError,
    JSONDecodeError,
    MessageParseError,
    ProcessError,
    SiiSDKError,
    TimeoutError,
    ToolNotAllowedError,
)

__all__ = [
    # 版本
    "SiiAgentSession",
    "SessionState",
    "ConversationTurn",
    "__version__",
    # 主要 API
    "query",
    # "SiiSDKClient",  # TODO: 待实现
    # 配置
    "SiiAgentOptions",
    "AuthType",
    "RunModelType",
    # 消息类型
    "Message",
    "AssistantMessage",
    "StatusMessage",
    "ToolResultMessage",
    "CompletedMessage",
    "ErrorMessage",
    # 内容块
    "ContentBlock",
    "TextBlock",
    "ToolUseBlock",
    "ToolResultBlock",
    # 异常
    "SiiSDKError",
    "BridgeNotFoundError",
    "BridgeConnectionError",
    "ProcessError",
    "JSONDecodeError",
    "AuthenticationError",
    "TimeoutError",
    "ToolNotAllowedError",
    "MessageParseError",
] 
