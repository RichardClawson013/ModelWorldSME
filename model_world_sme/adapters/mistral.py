"""
adapters/mistral.py — Mistral AI driver.

Requires: pip install mistralai
"""

from __future__ import annotations
from .base import BaseDriver

try:
    from mistralai import Mistral as _Mistral
except ImportError:
    _Mistral = None  # type: ignore[assignment]


class MistralDriver(BaseDriver):
    def __init__(
        self,
        api_key: str,
        model: str = "mistral-small-latest",
        max_tokens: int = 1024,
    ) -> None:
        if _Mistral is None:
            raise ImportError("pip install mistralai")
        self._client = _Mistral(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    async def ask(self, prompt: str) -> str:
        response = await self._client.chat.complete_async(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
