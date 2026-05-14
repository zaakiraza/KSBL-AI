from __future__ import annotations

from collections import Counter


def _tokenize(text: str) -> set[str]:
    return {token.strip(".,:;!?()[]{}\"").lower() for token in text.split() if len(token) > 2}


def rank_chunks(query: str, chunks: list[dict], top_k: int = 5) -> list[dict]:
    query_tokens = _tokenize(query)
    scored = []
    for chunk in chunks:
        chunk_tokens = _tokenize(chunk.get("text", ""))
        score = len(query_tokens.intersection(chunk_tokens))
        scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]
