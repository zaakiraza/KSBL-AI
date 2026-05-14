from __future__ import annotations

from typing import Any

from app.services.state import QUIZZES


class InMemoryVectorStore:
    def upsert(self, collection: str, item_id: str, payload: dict[str, Any]) -> None:
        QUIZZES.setdefault(collection, {})[item_id] = payload

    def search(self, collection: str, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        items = list(QUIZZES.get(collection, {}).values())
        return items[:top_k]
