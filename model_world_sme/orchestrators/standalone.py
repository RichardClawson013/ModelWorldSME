"""
orchestrators/standalone.py — Terminal orchestrator for local use.

No framework needed. Runs in your terminal.
"""

from __future__ import annotations
from .base import BaseOrchestrator
from typing import Any


class TerminalOrchestrator(BaseOrchestrator):
    """Delivers questions to stdout and reads answers from stdin."""

    def __init__(self, prompt_prefix: str = "You: ") -> None:
        self._prefix = prompt_prefix

    async def send(self, message: str) -> str:
        print(f"\n{message}\n")
        return input(self._prefix).strip()

    async def on_complete(self, result: Any) -> None:
        print("\n--- Interview complete ---")
        print(f"Active tasks: {result.summary['total_active']}")
        print(f"Agent name:   {result.summary.get('agent_name', '-')}")
        print("\nFiles ready to export:")
        print("  result.worldmodel_json")
        print("  result.agent_config_yaml")
        print("  result.soul_md")
