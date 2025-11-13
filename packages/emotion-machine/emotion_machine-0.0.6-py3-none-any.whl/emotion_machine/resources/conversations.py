"""Conversation retrieval helper."""

from __future__ import annotations

from typing import Any, Dict, Optional
from urllib.parse import urlencode

from ..client import _HTTPClient


class ConversationAPI:
    def __init__(self, http: _HTTPClient) -> None:
        self._http = http

    def get(self, conversation_id: str) -> dict[str, Any]:
        convo = self._http.request("GET", f"/v1/conversations/{conversation_id}")
        if not isinstance(convo, dict):  # pragma: no cover - defensive
            raise TypeError("Expected dict payload for conversation response")
        return convo

    def list(
        self,
        companion_id: str,
        *,
        limit: int = 50,
        offset: int = 0,
        external_user_id: Optional[str] = None,
        external_user_prefix: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        params = {
            "limit": limit,
            "offset": offset,
        }
        if external_user_id:
            params["external_user_id"] = external_user_id
        if external_user_prefix:
            params["external_user_prefix"] = external_user_prefix

        query = urlencode(params)
        path = f"/v1/companions/{companion_id}/conversations"
        if query:
            path = f"{path}?{query}"
        payload = self._http.request("GET", path)
        if not isinstance(payload, list):  # pragma: no cover - defensive
            raise TypeError("Expected list payload for conversation collection")
        return payload
