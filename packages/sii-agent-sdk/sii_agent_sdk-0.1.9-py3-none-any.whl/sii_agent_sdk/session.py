"""High-level session helper enabling multi-round YOLO interactions."""

from __future__ import annotations

from dataclasses import replace
from typing import AsyncIterator, Iterable, List, Optional

from .query import query
from .session_state import ConversationTurn, SessionState
from .types import Message, SiiAgentOptions


class SiiAgentSession:
    """Manage a reusable agent session across multiple YOLO executions."""

    def __init__(self, base_options: SiiAgentOptions, *, session_id: Optional[str] = None) -> None:
        self._base_options = replace(base_options)
        self._state = SessionState(session_id=session_id)

    @property
    def session_id(self) -> Optional[str]:
        return self._state.session_id

    @property
    def history(self) -> List[ConversationTurn]:
        return list(self._state.history)

    @property
    def state(self) -> SessionState:
        return self._state

    def append_user_feedback(self, feedback: str) -> None:
        if feedback:
            self._state.append(ConversationTurn(role="user", content=feedback))

    def append_turns(self, turns: Iterable[ConversationTurn]) -> None:
        for turn in turns:
            self._state.append(turn)

    async def run(
        self,
        prompt: str,
        *,
        options: Optional[SiiAgentOptions] = None,
    ) -> AsyncIterator[Message]:
        request_options = replace(options) if options is not None else replace(self._base_options)
        async for message in query(prompt, options=request_options, session_state=self._state):
            yield message

    def reset(self) -> None:
        self._state.clear()
