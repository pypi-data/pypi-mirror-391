"""Console logging helpers for streaming agent events."""

from __future__ import annotations

import json
import logging
import re
import textwrap
from datetime import datetime

from ..types import (
    AssistantMessage,
    CompletedMessage,
    ErrorMessage,
    Message,
    StatusMessage,
    TextBlock,
    ToolResultBlock,
    ToolResultMessage,
    ToolUseBlock,
)

_LOGGER_NAME = "sii_agent_sdk.events"


def _get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _format_text(text: str, max_length: int = 10000) -> str:
    """格式化文本,移除空的 <think> 标签和多余的空行。
    
    Args:
        text: 要格式化的文本
        max_length: 最大显示长度(默认 10000 字符)
    
    Returns:
        格式化后的文本,如果超过最大长度则截断
    """
    text = re.sub(r"<think>\s*</think>\s*", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) > max_length:
        return text[:max_length] + f"\n... (共 {len(text)} 字符，已截断)"
    return text


def _format_tool_input(data: dict) -> str:
    if not data:
        return "(无参数)"
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except TypeError:
        lines: list[str] = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                try:
                    serialized = json.dumps(value, ensure_ascii=False, indent=2)
                except TypeError:
                    serialized = str(value)
                lines.append(f"{key}:\n{textwrap.indent(serialized, '  ')}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    except Exception:
        return json.dumps(data, ensure_ascii=False)


def _log_header(title: str) -> None:
    logger = _get_logger()
    separator = "=" * 80
    logger.info("\n%s", separator)
    logger.info("%s", title)
    logger.info("%s", separator)


def log_message(message: Message) -> None:
    """Log a structured view of the streaming message to the console."""

    logger = _get_logger()
    timestamp = datetime.now().strftime("%H:%M:%S")

    if isinstance(message, StatusMessage):
        lines = [f"[状态] {message.message}"]
        if message.auth_type:
            lines.append(f"  └─ 认证方式: {message.auth_type}")
        if message.available_tools:
            lines.append(f"  └─ 可用工具数: {len(message.available_tools)}")
        logger.info("\n%s", "\n".join(lines))
        return

    if isinstance(message, CompletedMessage):
        _log_header("✅ 任务完成")
        meta = message.metadata or {}
        stats = [
            "📊 执行统计:",
            f"   ├─ 对话轮数: {meta.get('turns_used', 'N/A')}",
            f"   ├─ 总耗时: {meta.get('time_elapsed', 0) / 1000:.2f} 秒",
            f"   ├─ Token 使用: {meta.get('tokens_used', 'N/A')}",
        ]
        tools = meta.get("tools_used", [])
        if tools:
            stats.append(f"   └─ 已使用工具: {', '.join(tools)}")
        logger.info("%s", "\n".join(stats))
        logger.info("%s", "-" * 80)
        return

    if isinstance(message, ErrorMessage):
        _log_header("❌ 错误")
        error = message.error or {}
        logger.info("错误码: %s", error.get("code", "UNKNOWN"))
        logger.info("错误信息: %s", error.get("message", "未知错误"))
        if "details" in error:
            logger.info("详细信息: %s", json.dumps(error["details"], ensure_ascii=False, indent=2))
        logger.info("%s", "-" * 80)
        return

    if isinstance(message, ToolResultMessage):
        lines = [
            "\n" + "─" * 80,
            f"✅ 工具执行结果 [{timestamp}]",
            "─" * 80,
            f"🔧 工具调用 ID: {message.tool_use_id}",
        ]
        if message.is_error:
            lines.append(f"❌ 错误: {message.content}")
        else:
            result = message.content or "(空结果)"
            if len(result) > 500:
                lines.append(f"结果预览: {result[:500]}...")
                lines.append(f"(完整结果共 {len(result)} 字符)")
            else:
                lines.append(f"结果: {result}")
        lines.append("-" * 80)
        logger.info("%s", "\n".join(lines))
        return

    if isinstance(message, AssistantMessage):
        _log_header(f"💬 AI 回复 [{timestamp}]")
        for block in message.content:
            if isinstance(block, TextBlock):
                text = _format_text(block.text)
                if text.strip():
                    logger.info("\n📝 文本内容:\n%s", text)
            elif isinstance(block, ToolUseBlock):
                lines = [
                    "\n🔧 工具调用",
                    f"🧰 名称: {block.name}",
                ]
                if block.id:
                    lines.append(f"🆔 调用 ID: {block.id}")
                lines.append("\n📋 参数:\n" + _format_tool_input(block.input))
                logger.info("%s", "\n".join(lines))
            elif isinstance(block, ToolResultBlock):
                lines = [
                    "\n✅ 工具结果 (内联):",
                    f"   工具 ID: {block.tool_use_id}",
                ]
                if block.is_error:
                    lines.append(f"   ❌ 错误: {block.content}")
                else:
                    content = block.content or "(空)"
                    if len(content) > 300:
                        lines.append(f"   结果: {content[:300]}... (共 {len(content)} 字符)")
                    else:
                        lines.append(f"   结果: {content}")
                logger.info("%s", "\n".join(lines))
        logger.info("%s", "-" * 80)
        return

    logger.debug("Unhandled message type: %s", type(message).__name__)