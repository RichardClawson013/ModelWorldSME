"""
orchestrators/autogen.py — AutoGen orchestrator bridge.

Requires: pip install pyautogen
"""

from __future__ import annotations
from .base import BaseOrchestrator
from typing import Any


class AutoGenOrchestrator(BaseOrchestrator):
    """
    Bridge between ModelWorldSME and an AutoGen UserProxyAgent.

    Pass in the agent's `initiate_chat` callable and a ConversableAgent.

    Example:
        from autogen import UserProxyAgent, AssistantAgent
        user = UserProxyAgent("user")
        orchestrator = AutoGenOrchestrator(user_proxy=user)
    """

    def __init__(self, user_proxy: Any) -> None:
        self._proxy = user_proxy
        self._last_response: str = ""

    async def send(self, message: str) -> str:
        # AutoGen is synchronous — wrap via thread if needed in async contexts
        print(f"\n{message}\n")
        self._last_response = input("You: ").strip()
        return self._last_response
