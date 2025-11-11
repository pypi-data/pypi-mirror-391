"""
Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0

异常定义 - 参考 claude-agent-sdk-python 的异常体系
"""

from typing import Any, Dict, Optional


class SiiSDKError(Exception):
    """SDK 基础异常 (类似 ClaudeSDKError)"""

    pass


class BridgeNotFoundError(SiiSDKError):
    """未找到 Node Bridge 可执行文件 (类似 CLINotFoundError)"""

    def __init__(
        self, message: str = "SII Bridge not found", bridge_path: Optional[str] = None
    ):
        if bridge_path:
            message = f"{message}: {bridge_path}"
        super().__init__(message)
        self.bridge_path = bridge_path


class BridgeConnectionError(SiiSDKError):
    """Bridge 连接失败 (类似 CLIConnectionError)"""

    pass


class ProcessError(SiiSDKError):
    """Bridge 进程异常 (类似 Claude SDK ProcessError)"""

    def __init__(
        self, message: str, exit_code: Optional[int] = None, stderr: Optional[str] = None
    ):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class JSONDecodeError(SiiSDKError):
    """JSON 解析失败 (类似 CLIJSONDecodeError)"""

    def __init__(self, line: str, original_error: Exception):
        self.line = line
        self.original_error = original_error
        super().__init__(f"Failed to decode JSON: {line[:100]}...")


class AuthenticationError(SiiSDKError):
    """认证失败 (SII 特色)"""

    def __init__(self, message: str, auth_type: Optional[str] = None):
        super().__init__(message)
        self.auth_type = auth_type


class ToolNotAllowedError(SiiSDKError):
    """工具不可用 (SII 特色)"""

    def __init__(self, tool_name: str, auth_type: str, required_auth: Optional[str] = None):
        message = f"Tool '{tool_name}' not available with auth type '{auth_type}'"
        if required_auth:
            message += f", requires '{required_auth}'"
        super().__init__(message)
        self.tool_name = tool_name
        self.auth_type = auth_type
        self.required_auth = required_auth


class TimeoutError(SiiSDKError):
    """执行超时"""

    def __init__(self, message: str, timeout_ms: int):
        super().__init__(message)
        self.timeout_ms = timeout_ms


class MessageParseError(SiiSDKError):
    """消息解析错误 (类似 Claude SDK)"""

    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.data = data 