"""
Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0

Query API - 主要的查询接口 (参考 claude-agent-sdk-python)
"""

import json
import logging
import os
from typing import AsyncIterator, Optional

from ._internal.message_parser import parse_message
from ._internal.event_logger import log_message
from .bridge import BridgeProcess
from .errors import AuthenticationError, SiiSDKError, ToolNotAllowedError
from .session_state import ConversationTurn, SessionState
from .types import (
    AssistantMessage,
    CompletedMessage,
    ErrorMessage,
    Message,
    SiiAgentOptions,
    StatusMessage,
    TextBlock,
    ToolResultMessage,
    ToolUseBlock,
)

logger = logging.getLogger(__name__)

ASK_MODEL_DEFAULT_SYSTEM_PROMPT = (
    "You are Ask Model running inside the SII CLI environment. "
    "Answer the user's question directly and concisely using only the provided context. "
    "Do not assume tool access unless explicitly mentioned."
)

def _get_env_value(key: str, overrides: Optional[dict[str, str]] = None) -> Optional[str]:
    """获取环境变量值，优先使用用户通过 options.env 传入的覆盖值。"""
    if overrides and key in overrides and overrides[key]:
        return overrides[key]
    return os.getenv(key)


def _format_missing_env_message(required: list[str], advice: str) -> str:
    human_list = ", ".join(required)
    return (
        f"缺少必要的认证配置: {human_list}\n"
        f"请通过 SiiAgentOptions(env={{...}}) 显式传入，或预先设置对应的环境变量。\n"
        f"{advice}"
    )


def validate_auth_config(auth_type: str, env_overrides: Optional[dict[str, str]] = None) -> None:
    """
    验证认证配置是否完整

    Raises:
        ValueError: 如果配置不完整
    """
    if auth_type == 'USE_SII':
        if not (_get_env_value('SII_USERNAME', env_overrides) and _get_env_value('SII_PASSWORD', env_overrides)):
            raise ValueError(
                _format_missing_env_message(
                    ['SII_USERNAME', 'SII_PASSWORD'],
                    "示例: SiiAgentOptions(env={'SII_USERNAME': 'user', 'SII_PASSWORD': 'pass'})"
                )
            )

    elif auth_type == 'USE_OPENAI':
        if not _get_env_value('SII_OPENAI_BASE_URL', env_overrides):
            raise ValueError(
                _format_missing_env_message(
                    ['SII_OPENAI_BASE_URL'],
                    "示例: SiiAgentOptions(env={'SII_OPENAI_BASE_URL': 'https://api.openai.com/v1'})\n"
                    "若使用兼容 OpenAI 的服务，请替换为服务提供的 Base URL。"
                )
            )

        if not (_get_env_value('SII_OPENAI_API_KEY', env_overrides) or _get_env_value('OPENAI_API_KEY', env_overrides)):
            raise ValueError(
                _format_missing_env_message(
                    ['OPENAI_API_KEY (或 SII_OPENAI_API_KEY)'],
                    "示例: SiiAgentOptions(env={'OPENAI_API_KEY': 'sk-...'})"
                )
            )

    elif auth_type == 'USE_OPENAI_WITH_SII_TOOLS':
        if not _get_env_value('SII_OPENAI_BASE_URL', env_overrides):
            raise ValueError(
                _format_missing_env_message(
                    ['SII_OPENAI_BASE_URL'],
                    "示例: SiiAgentOptions(env={'SII_OPENAI_BASE_URL': 'https://api.openai.com/v1'})\n"
                    "若使用兼容 OpenAI 的服务，请替换为服务提供的 Base URL。"
                )
            )

        if not (_get_env_value('SII_OPENAI_API_KEY', env_overrides) or _get_env_value('OPENAI_API_KEY', env_overrides)):
            raise ValueError(
                _format_missing_env_message(
                    ['OPENAI_API_KEY (或 SII_OPENAI_API_KEY)'],
                    "示例: SiiAgentOptions(env={'OPENAI_API_KEY': 'sk-...'})"
                )
            )

        if not (_get_env_value('SII_USERNAME', env_overrides) and _get_env_value('SII_PASSWORD', env_overrides)):
            raise ValueError(
                _format_missing_env_message(
                    ['SII_USERNAME', 'SII_PASSWORD'],
                    "示例: SiiAgentOptions(env={'SII_USERNAME': 'user', 'SII_PASSWORD': 'pass'})"
                )
            )


def _message_to_session_turns(
    message: Message,
    session_state: Optional[SessionState],
) -> list[ConversationTurn]:
    turns: list[ConversationTurn] = []

    if isinstance(message, StatusMessage):
        return turns

    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                text = block.text.strip()
                if text:
                    turns.append(ConversationTurn(role="assistant", content=text))
            elif isinstance(block, ToolUseBlock):
                args_repr = json.dumps(block.input or {}, ensure_ascii=False)
                summary = f"[TOOL CALL] {block.name}({args_repr})"
                turn = ConversationTurn(
                    role="assistant",
                    content=summary,
                    tool_name=block.name or None,
                    tool_call_id=block.id or None,
                    metadata={"input": block.input or {}},
                )
                turns.append(turn)
                if session_state:
                    session_state.register_tool_call(block.id or "", block.name or None)

    elif isinstance(message, ToolResultMessage):
        payload = message.content
        if isinstance(payload, (dict, list)):
            content = json.dumps(payload, ensure_ascii=False)
        else:
            content = (payload or "").strip()

        tool_name = session_state.resolve_tool_name(message.tool_use_id) if session_state else None
        turns.append(
            ConversationTurn(
                role="tool",
                content=content,
                tool_name=tool_name,
                tool_call_id=message.tool_use_id or None,
                is_error=bool(message.is_error),
            )
        )

    elif isinstance(message, ErrorMessage):
        error_payload = message.error or {}
        error_text = error_payload.get("message")
        if not error_text:
            error_text = json.dumps(error_payload, ensure_ascii=False)
        turns.append(
            ConversationTurn(
                role="assistant",
                content=f"[ERROR] {error_text}",
                metadata={"error": error_payload},
            )
        )

    elif isinstance(message, CompletedMessage):
        return turns

    return turns


async def query(
    prompt: str,
    *,
    options: Optional[SiiAgentOptions] = None,
    session_state: Optional[SessionState] = None,
) -> AsyncIterator[Message]:
    """
    执行单次查询，返回异步消息迭代器
    
    参考 claude-agent-sdk-python 的 query() 函数设计，
    提供相似的 API 体验但集成 SII 特色功能。
    
    Args:
        prompt: 用户提示词
        options: 可选配置
    
    Yields:
        Message: 类型化的消息对象
    
    Raises:
        BridgeNotFoundError: 未找到 SII Bridge
        BridgeConnectionError: Bridge 连接失败
        AuthenticationError: 认证失败
        SiiSDKError: 其他错误
    
    Example:
        >>> import anyio
        >>> from sii_agent_sdk import query, SiiAgentOptions
        >>> 
        >>> async def main():
        ...     async for msg in query(
        ...         prompt="列出当前目录文件",
        ...         options=SiiAgentOptions(yolo=True, max_turns=5)
        ...     ):
        ...         print(msg)
        >>> 
        >>> anyio.run(main)
    """
    opts = options or SiiAgentOptions()

    # 仅根据参数决定认证模式，默认为 USE_SII
    auth_type = opts.auth_type or "USE_SII"
    opts.auth_type = auth_type  # type: ignore[assignment]

    # Ask 模式：如果未提供 system prompt，注入默认提示
    if opts.run_model == "ask":
        if not opts.system_prompt or not opts.system_prompt.strip():
            opts.system_prompt = ASK_MODEL_DEFAULT_SYSTEM_PROMPT

    # 验证认证配置（优先使用 options.env 中的值）
    validate_auth_config(auth_type, opts.env)

    bridge = BridgeProcess(opts)

    # 设置环境变量标识
    os.environ["SII_SDK_ENTRYPOINT"] = "python-sdk"

    try:
        # 1. 启动 Bridge 进程
        await bridge.start()

        # 2. 发送查询请求
        request_payload: dict[str, object] = {
            "prompt": prompt,
            "options": opts.to_dict(),
        }

        if session_state:
            history_payload = session_state.to_bridge_history()
            if history_payload:
                request_payload["history"] = history_payload
            if session_state.session_id:
                request_payload["session_id"] = session_state.session_id
            if session_state.environment_context:
                request_payload["environment_context"] = session_state.environment_context

        await bridge.send_request("query", request_payload)

        if session_state:
            session_state.append(ConversationTurn(role="user", content=prompt))

        # 3. 接收事件流并解析为消息
        async for event in bridge.receive_events():
            message = parse_message(event)
            if message:
                if session_state:
                    for turn in _message_to_session_turns(message, session_state):
                        session_state.append(turn)
                if getattr(opts, "log_events", True):
                    log_message(message)
                yield message

            # 4. 处理完成和错误事件
            if event.get("type") == "completed":
                if session_state:
                    metadata = event.get("metadata", {}) or {}
                    session_id = metadata.get("session_id")
                    if session_id:
                        session_state.session_id = session_id
                    environment_context = metadata.get("environment_context")
                    if environment_context:
                        session_state.environment_context = environment_context
                break
            elif event.get("type") == "error":
                error_data = event.get("error", {})
                _raise_appropriate_error(error_data)

    finally:
        # 5. 确保资源清理
        await bridge.close()


def _raise_appropriate_error(error_data: dict) -> None:
    """根据错误码抛出相应的异常"""
    code = error_data.get("code", "UNKNOWN_ERROR")
    message = error_data.get("message", "Unknown error")
    details = error_data.get("details", {})

    if code == "AUTH_FAILED":
        auth_type = details.get("auth_type")
        raise AuthenticationError(message, auth_type)
    elif code == "TOOL_NOT_ALLOWED":
        raise ToolNotAllowedError(
            details.get("tool_name", ""),
            details.get("auth_type", ""),
            details.get("required_auth"),
        )
    else:
        raise SiiSDKError(f"{code}: {message}") 
