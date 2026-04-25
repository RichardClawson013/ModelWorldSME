"""
adapters/openai.py — OpenAI driver (also works with any OpenAI-compatible endpoint).

Requires: pip install openai
"""

from __future__ import annotations
from .base import BaseDriver

try:
    import openai as _openai
except ImportError:
    _openai = None  # type: ignore[assignment]


class OpenAIDriver(BaseDriver):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        if _openai is None:
            raise ImportError("pip install openai")
        self._client = _openai.AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._max_tokens = max_tokens

    async def ask(self, prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
