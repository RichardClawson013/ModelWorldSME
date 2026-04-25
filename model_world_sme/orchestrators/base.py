"""
orchestrators/base.py — Base orchestrator interface.

Implement this to plug ModelWorldSME into any agent framework.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class BaseOrchestrator(ABC):
    """
    Minimal interface between ModelWorldSME and your agent framework.

    Your orchestrator receives interview turns and delivers them to
    whatever conversation loop your system uses.
    """

    @abstractmethod
    async def send(self, message: str) -> str:
        """
        Deliver *message* to the end user and return their response.

        This is the only method the interview engine calls externally.
        Implement it to fit your channel: terminal, WhatsApp, Telegram,
        web socket, Hermes skill, LangChain chain, etc.
        """
        ...

    async def on_complete(self, result: Any) -> None:
        """
        Called once when the interview finishes.

        *result* is the InterviewResult object. Override to persist,
        trigger downstream agents, or send a confirmation message.
        """
