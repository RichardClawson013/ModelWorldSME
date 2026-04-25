"""
adapters/ollama.py — Ollama local model driver.

Requires: pip install httpx  (no ollama SDK needed)
Ollama must be running: https://ollama.com
"""

from __future__ import annotations
from .base import BaseDriver

try:
    import httpx as _httpx
except ImportError:
    _httpx = None  # type: ignore[assignment]


class OllamaDriver(BaseDriver):
    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ) -> None:
        if _httpx is None:
            raise ImportError("pip install httpx")
        self._model = model
        self._base_url = base_url.rstrip("/")

    async def ask(self, prompt: str) -> str:
        async with _httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self._base_url}/api/generate",
                json={"model": self._model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            return response.json()["response"]
