"""
orchestrators/langchain.py — LangChain orchestrator bridge.

Requires: pip install langchain
"""

from __future__ import annotations
from .base import BaseOrchestrator
from typing import Any


class LangChainOrchestrator(BaseOrchestrator):
    """
    Bridge between ModelWorldSME and a LangChain chain or agent.

    Pass in any callable that accepts a string and returns a string.
    This keeps ModelWorldSME decoupled from LangChain internals.

    Example:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI()
        orchestrator = LangChainOrchestrator(chain=llm.invoke)
    """

    def __init__(self, chain: Any) -> None:
        self._chain = chain

    async def send(self, message: str) -> str:
        result = self._chain(message)
        if hasattr(result, "content"):
            return result.content
        return str(result)
