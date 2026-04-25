"""
orchestrators/hermes.py — Hermes (Nous Foundation) orchestrator bridge.

Plug ModelWorldSME into a Hermes skill.
"""

from __future__ import annotations
from .base import BaseOrchestrator
from typing import Any, Callable, Awaitable


class HermesOrchestrator(BaseOrchestrator):
    """
    Bridge between ModelWorldSME and a Hermes skill.

    Pass in the Hermes `send_message` and `receive_message` callables
    from your skill context.

    Example in a Hermes skill:
        from model_world_sme.orchestrators import HermesOrchestrator
        orchestrator = HermesOrchestrator(
            send=ctx.send_message,
            receive=ctx.receive_message,
            on_done=ctx.save_result,
        )
    """

    def __init__(
        self,
        send: Callable[[str], Awaitable[None]],
        receive: Callable[[], Awaitable[str]],
        on_done: Callable[[Any], Awaitable[None]] | None = None,
    ) -> None:
        self._send = send
        self._receive = receive
        self._on_done = on_done

    async def send(self, message: str) -> str:
        await self._send(message)
        return await self._receive()

    async def on_complete(self, result: Any) -> None:
        if self._on_done:
            await self._on_done(result)
