"""Conversation retrieval helper."""

from __future__ import annotations

from typing import Any, Dict

from ..client import _HTTPClient


class ConversationAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def get(self, conversation_id: str) -> dict[str, Any]:
        convo = self._http.request("GET", f"/v1/conversations/{conversation_id}")
        if not isinstance(convo, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for conversation response")
        return convo
