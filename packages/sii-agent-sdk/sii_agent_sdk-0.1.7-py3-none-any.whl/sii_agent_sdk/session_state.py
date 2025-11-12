"""Session state utilities for multi-round YOLO interactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

ConversationRole = Literal["system", "user", "assistant", "tool"]


@dataclass
class ConversationTurn:
    """Represents a single conversational turn persisted across rounds."""

    role: ConversationRole
    content: str
    tool_name: Optional[str] = None
    tool_call_id: Optional[str] = None
    is_error: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_bridge_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "role": self.role,
            "content": self.content,
        }
        if self.tool_name:
            payload["tool_name"] = self.tool_name
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        if self.is_error:
            payload["is_error"] = True
        if self.metadata:
            payload["metadata"] = self.metadata
        return payload


@dataclass
class SessionState:
    """Holds reusable session-level data across YOLO executions."""

    session_id: Optional[str] = None
    environment_context: Optional[str] = None
    history: List[ConversationTurn] = field(default_factory=list)
    _tool_names: Dict[str, str] = field(default_factory=dict, init=False, repr=False)

    def to_bridge_history(self) -> List[Dict[str, Any]]:
        """Serialise history for the bridge layer."""
        return [turn.to_bridge_dict() for turn in self.history]

    def append(self, turn: ConversationTurn) -> None:
        self.history.append(turn)
        if turn.tool_call_id and turn.tool_name:
            self._tool_names[turn.tool_call_id] = turn.tool_name

    def register_tool_call(self, call_id: str, tool_name: Optional[str]) -> None:
        if call_id and tool_name:
            self._tool_names[call_id] = tool_name

    def resolve_tool_name(self, call_id: str) -> Optional[str]:
        if not call_id:
            return None
        return self._tool_names.get(call_id)

    def clear(self) -> None:
        self.history.clear()
        self._tool_names.clear()
        self.session_id = None
        self.environment_context = None
