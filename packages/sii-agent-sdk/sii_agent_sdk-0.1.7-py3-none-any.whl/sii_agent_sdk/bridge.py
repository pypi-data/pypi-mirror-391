"""
Copyright 2025 Google LLC
Licensed under the Apache License, Version 2.0

Bridge 进程管理 - 管理 Node.js Bridge 子进程
"""

import asyncio
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

from .errors import (
    BridgeConnectionError,
    BridgeNotFoundError,
    JSONDecodeError as SDKJSONDecodeError,
    ProcessError,
)
from .types import SiiAgentOptions


class BridgeProcess:
    """
    管理 Node.js Bridge 子进程 (参考 Claude SDK SubprocessCLITransport)
    
    职责:
    - 查找和启动 SII Bridge 可执行文件
    - 管理 stdin/stdout 通信
    - 处理进程生命周期
    """

    def __init__(self, options: SiiAgentOptions):
        """
        初始化 Bridge 进程管理器
        
        Args:
            options: Agent 配置选项
        """
        self.options = options
        self.process: Optional[asyncio.subprocess.Process] = None
        self.stdin_writer: Optional[asyncio.StreamWriter] = None
        self.stdout_reader: Optional[asyncio.StreamReader] = None
        self.stderr_reader: Optional[asyncio.StreamReader] = None
        self._bridge_path: Optional[Path] = None
        self._ready = False

    def _find_bridge_executable(self) -> Path:
        """
        查找 Node Bridge 可执行文件
        
        查找顺序 (参考 Claude SDK):
        1. 环境变量 SII_BRIDGE_PATH
        2. 开发环境: <package_dir>/../bridge/dist/index.js
        3. 全局安装: sii-bridge (通过 which)
        
        Returns:
            Bridge 可执行文件路径
        
        Raises:
            BridgeNotFoundError: 如果找不到 Bridge
        """
        # 1. 检查环境变量
        env_path = os.environ.get("SII_BRIDGE_PATH")
        if env_path:
            bridge_path = Path(env_path)
            if bridge_path.exists():
                return bridge_path

        # 2. 检查开发环境路径
        package_dir = Path(__file__).parent
        dev_bridge_path = package_dir.parent / "bridge" / "dist" / "index.js"
        if dev_bridge_path.exists():
            return dev_bridge_path

        # 3. 检查全局安装
        which_result = shutil.which("sii-bridge")
        if which_result:
            return Path(which_result)

        # 未找到
        raise BridgeNotFoundError(
            "SII Bridge not found. Please ensure:\n"
            "1. Node.js >= 20.0.0 is installed\n"
            "2. Bridge is built: cd packages/python-sdk/bridge && npm run build\n"
            "3. Or set SII_BRIDGE_PATH environment variable"
        )

    async def start(self) -> None:
        """
        启动 Bridge 进程 (参考 Claude SDK connect)
        
        Raises:
            BridgeNotFoundError: 如果找不到 Node.js 或 Bridge
            BridgeConnectionError: 如果无法建立连接
        """
        if self._ready:
            return

        # 查找 Bridge 可执行文件
        self._bridge_path = self._find_bridge_executable()

        # 检查 Node.js
        node_path = shutil.which("node")
        if not node_path:
            raise BridgeNotFoundError(
                "Node.js not found. Please install Node.js >= 20.0.0"
            )

        try:
            # 启动进程
            self.process = await asyncio.create_subprocess_exec(
                node_path,
                str(self._bridge_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, **self.options.env},
            )

            if not self.process.stdin or not self.process.stdout or not self.process.stderr:
                raise BridgeConnectionError("Failed to create process streams")

            self.stdin_writer = self.process.stdin
            self.stdout_reader = self.process.stdout
            self.stderr_reader = self.process.stderr

            self._ready = True

        except Exception as e:
            raise BridgeConnectionError(f"Failed to start Bridge: {e}") from e

    async def send_request(
        self, method: str, params: Dict[str, Any]
    ) -> str:
        """
        发送请求到 Bridge
        
        Args:
            method: 请求方法 (query, list_tools, interrupt 等)
            params: 请求参数
        
        Returns:
            请求ID
            
        Raises:
            BridgeConnectionError: 如果 Bridge 未启动
        """
        if not self._ready or not self.stdin_writer:
            raise BridgeConnectionError("Bridge not started. Call start() first.")

        request_id = f"req-{uuid.uuid4().hex[:16]}"
        request = {
            "protocol_version": "1.0.0",
            "request_id": request_id,
            "method": method,
            "params": params,
        }

        try:
            request_json = json.dumps(request)
            self.stdin_writer.write(request_json.encode("utf-8"))
            self.stdin_writer.write(b"\n")
            await self.stdin_writer.drain()
            return request_id

        except Exception as e:
            raise BridgeConnectionError(f"Failed to send request: {e}") from e

    async def receive_events(self) -> AsyncIterator[Dict[str, Any]]:
        """
        接收事件流 (参考 Claude SDK read_messages)
        
        Yields:
            事件字典
        
        Raises:
            BridgeConnectionError: 如果 Bridge 未启动
            JSONDecodeError: 如果 JSON 解析失败
            ProcessError: 如果进程异常退出
            TimeoutError: 如果长时间没有响应
        """
        if not self._ready or not self.stdout_reader:
            raise BridgeConnectionError("Bridge not started")

        import logging
        logger = logging.getLogger(__name__)
        
        # 超时配置
        READ_TIMEOUT = 600.0  # 10 分钟超时（模型可能需要较长时间处理复杂任务）
        no_output_count = 0

        try:
            while True:
                # 逐行读取，添加超时保护
                try:
                    line_bytes = await asyncio.wait_for(
                        self.stdout_reader.readline(),
                        timeout=READ_TIMEOUT
                    )
                    
                    # 收到数据后重置计数器
                    no_output_count = 0
                    
                except asyncio.TimeoutError:
                    no_output_count += 1
                    logger.warning(
                        f"No output from Bridge for {READ_TIMEOUT}s "
                        f"(attempt {no_output_count}). Bridge might be waiting for slow model response..."
                    )
                    
                    # 检查进程是否还活着
                    if self.process and self.process.returncode is not None:
                        stderr_data = await self._read_stderr()
                        raise ProcessError(
                            "Bridge process died while waiting for output",
                            exit_code=self.process.returncode,
                            stderr=stderr_data,
                        )
                    
                    # 如果超过 3 次超时（30 分钟），仍然继续等待但发出警告
                    if no_output_count >= 3:
                        logger.error(
                            f"Bridge has been silent for {READ_TIMEOUT * no_output_count:.0f}s ({READ_TIMEOUT * no_output_count / 60:.1f} minutes). "
                            "This might indicate a problem with the model or network."
                        )
                    
                    # 继续等待下一次读取
                    continue
                
                if not line_bytes:
                    # EOF - 检查进程状态
                    if self.process and self.process.returncode is not None:
                        stderr_data = await self._read_stderr()
                        raise ProcessError(
                            "Bridge process exited unexpectedly",
                            exit_code=self.process.returncode,
                            stderr=stderr_data,
                        )
                    break

                line = line_bytes.decode("utf-8").strip()
                if not line:
                    continue

                # 记录接收到的消息（调试用）
                logger.debug(f"Received event: {line[:100]}{'...' if len(line) > 100 else ''}")

                # 解析 JSON
                try:
                    event = json.loads(line)
                    yield event

                    # 检查是否是终止事件
                    if event.get("type") in ("completed", "error"):
                        break

                except json.JSONDecodeError as e:
                    raise SDKJSONDecodeError(line, e) from e

        except asyncio.CancelledError:
            # 任务被取消，正常退出
            logger.info("Bridge event stream cancelled")
            pass
        except ProcessError:
            raise
        except Exception as e:
            if not isinstance(e, SDKJSONDecodeError):
                raise BridgeConnectionError(f"Failed to receive events: {e}") from e
            raise

    async def close(self) -> None:
        """
        关闭 Bridge 进程 (参考 Claude SDK close)
        
        Raises:
            ProcessError: 如果进程异常退出
        """
        if not self.process:
            return

        try:
            # 关闭 stdin
            if self.stdin_writer:
                self.stdin_writer.close()
                await self.stdin_writer.wait_closed()

            # 等待进程退出
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                # 超时则强制终止
                self.process.kill()
                await self.process.wait()

            # 检查退出码
            if self.process.returncode != 0:
                stderr_data = await self._read_stderr()
                raise ProcessError(
                    f"Bridge exited with code {self.process.returncode}",
                    exit_code=self.process.returncode,
                    stderr=stderr_data,
                )

        finally:
            self.process = None
            self.stdin_writer = None
            self.stdout_reader = None
            self.stderr_reader = None
            self._ready = False

    async def _read_stderr(self) -> str:
        """读取 stderr 内容"""
        if not self.stderr_reader:
            return ""

        try:
            stderr_bytes = await asyncio.wait_for(
                self.stderr_reader.read(), timeout=1.0
            )
            return stderr_bytes.decode("utf-8", errors="replace")
        except asyncio.TimeoutError:
            return ""

    def is_ready(self) -> bool:
        """检查 Bridge 是否就绪 (参考 Claude SDK)"""
        return self._ready and self.process is not None 