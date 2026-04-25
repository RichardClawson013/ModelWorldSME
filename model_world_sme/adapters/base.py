"""
adapters/base.py — Base interface for model drivers.

Implement this to plug in any LLM provider.
The interview core never calls a model directly — it calls your driver.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


class BaseDriver(ABC):
    """Minimal interface: receive a prompt, return a string response."""

    @abstractmethod
    async def ask(self, prompt: str) -> str:
        """Send *prompt* to the model and return its response as a string."""
        ...

    async def close(self) -> None:
        """Optional cleanup. Called when the interview ends."""
