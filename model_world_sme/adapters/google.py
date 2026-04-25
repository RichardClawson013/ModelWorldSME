"""
adapters/google.py — Google Gemini driver.

Requires: pip install google-genai
"""

from __future__ import annotations
from .base import BaseDriver

try:
    from google import genai as _genai
except ImportError:
    _genai = None  # type: ignore[assignment]


class GoogleDriver(BaseDriver):
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
    ) -> None:
        if _genai is None:
            raise ImportError("pip install google-genai")
        self._client = _genai.Client(api_key=api_key)
        self._model = model

    async def ask(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
        )
        return response.text or ""
