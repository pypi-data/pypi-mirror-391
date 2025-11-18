"""
Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0

类型定义 - 参考 claude-agent-sdk-python 的设计
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

# ============================================================================
# 认证类型 (与 SII-CLI 保持一致)
# ============================================================================

AuthType = Literal[
    "USE_SII",                      # SII 平台认证
    "USE_OPENAI",                   # OpenAI API Key
    "USE_OPENAI_WITH_SII_TOOLS",   # 混合模式：OpenAI + SII Tools
]

# 运行模型类型
RunModelType = Literal[
    "agent",   # 默认：使用完整的 SII-CLI Agent Prompt + 工具
    "ask",     # 轻量：仅使用用户提供的 System Prompt（或默认 Ask Prompt）
]

# ============================================================================
# 配置类型
# ============================================================================


def _get_default_model() -> str:
    """
    获取默认模型，优先从环境变量 SII_OPENAI_MODEL 读取
    如果环境变量为空，则使用 anthropic/claude-sonnet-4.5
    """
    return os.environ.get("SII_OPENAI_MODEL", "").strip() or "GLM-4.6"


@dataclass
class SiiAgentOptions:
    """SII Agent 配置选项 (参考 Claude SDK 的 ClaudeAgentOptions)"""

    # 基础配置
    system_prompt: Optional[str] = None
    max_turns: int = 10
    allowed_tools: Optional[List[str]] = None
    cwd: Optional[Union[Path, str]] = None

    # SII 特色配置
    auth_type: AuthType = "USE_SII"
    yolo: bool = False
    log_events: bool = True
    run_model: RunModelType = "agent"

    # 高级配置
    timeout_ms: int = 120000
    model: Optional[str] = field(default_factory=_get_default_model)  # 从环境变量读取，默认 Claude Sonnet 4.5
    temperature: Optional[float] = None

    # 环境变量
    env: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """序列化为 Bridge 请求格式"""
        return {
            k: str(v) if isinstance(v, Path) else v
            for k, v in self.__dict__.items()
            if v is not None and k != "env"
        }


# ============================================================================
# 内容块类型 (参考 Claude SDK ContentBlock)
# ============================================================================


@dataclass
class TextBlock:
    """文本内容块"""

    type: Literal["text"] = "text"
    text: str = ""


@dataclass
class ToolUseBlock:
    """工具使用块 (参考 Claude SDK ToolUseBlock)"""

    type: Literal["tool_use"] = "tool_use"
    id: str = ""
    name: str = ""
    input: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResultBlock:
    """工具结果块 (参考 Claude SDK ToolResultBlock)"""

    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str = ""
    content: Optional[str] = None
    is_error: Optional[bool] = None


ContentBlock = Union[TextBlock, ToolUseBlock, ToolResultBlock]

# ============================================================================
# 消息类型 (参考 Claude SDK Message 体系)
# ============================================================================


@dataclass
class AssistantMessage:
    """助手消息 (参考 Claude SDK AssistantMessage)"""

    role: Literal["assistant"] = "assistant"
    content: List[ContentBlock] = field(default_factory=list)


@dataclass
class StatusMessage:
    """状态消息 (SII 特色)"""

    type: Literal["status"] = "status"
    status: str = ""
    message: str = ""
    auth_type: Optional[str] = None
    available_tools: Optional[List[str]] = None


@dataclass
class ToolResultMessage:
    """工具结果消息"""

    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str = ""
    content: Optional[str] = None
    is_error: bool = False


@dataclass
class CompletedMessage:
    """完成消息 (参考 Claude SDK ResultMessage)"""

    type: Literal["completed"] = "completed"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorMessage:
    """错误消息"""

    type: Literal["error"] = "error"
    error: Dict[str, Any] = field(default_factory=dict)


# 联合类型
Message = Union[AssistantMessage, ToolResultMessage, StatusMessage, CompletedMessage, ErrorMessage] 
