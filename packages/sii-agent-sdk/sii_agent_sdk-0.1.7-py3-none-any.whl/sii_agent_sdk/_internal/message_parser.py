"""
Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0

消息解析器 - 将 Bridge 事件解析为类型化消息对象
"""

from typing import Any, Dict, Optional

from ..types import (
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


def parse_message(event: Dict[str, Any]) -> Optional[Message]:
    """
    将 Bridge 事件解析为 SDK Message
    
    Args:
        event: Bridge 事件字典
    
    Returns:
        解析后的 Message 对象，如果事件类型未知则返回 None
    """
    event_type = event.get("type")

    if event_type == "status":
        return StatusMessage(
            type="status",
            status=event.get("status", ""),
            message=event.get("message", ""),
            auth_type=event.get("auth_type"),
            available_tools=event.get("available_tools"),
        )

    elif event_type == "assistant_message":
        # 解析内容块
        content_data = event.get("content", [])
        content_blocks: list[ContentBlock] = []

        for block_data in content_data:
            block_type = block_data.get("type")

            if block_type == "text":
                content_blocks.append(
                    TextBlock(type="text", text=block_data.get("text", ""))
                )
            elif block_type == "tool_use":
                content_blocks.append(
                    ToolUseBlock(
                        type="tool_use",
                        id=block_data.get("id", ""),
                        name=block_data.get("name", ""),
                        input=block_data.get("input", {}),
                    )
                )

        return AssistantMessage(role="assistant", content=content_blocks)

    elif event_type == "tool_call":
        # 将 tool_call 转换为 AssistantMessage with ToolUseBlock
        return AssistantMessage(
            role="assistant",
            content=[
                ToolUseBlock(
                    type="tool_use",
                    id=event.get("tool_call_id", ""),
                    name=event.get("tool_name", ""),
                    input=event.get("args", {}),
                )
            ],
        )

    elif event_type == "tool_result":
        return ToolResultMessage(
            type="tool_result",
            tool_use_id=event.get("tool_use_id", ""),
            content=event.get("content"),
            is_error=event.get("is_error", False),
        )

    elif event_type == "completed":
        return CompletedMessage(
            type="completed", metadata=event.get("metadata", {})
        )

    elif event_type == "error":
        return ErrorMessage(type="error", error=event.get("error", {}))

    # 未知事件类型
    return None 