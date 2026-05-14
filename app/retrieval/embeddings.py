from __future__ import annotations

import hashlib


def embed_text(text: str, dimensions: int = 8) -> list[float]:
    vector = [0.0] * dimensions
    normalized = text.lower().strip()
    for index, byte in enumerate(normalized.encode("utf-8")):
        vector[index % dimensions] += (byte % 31) / 31.0
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    vector[0] += int(digest[:4], 16) / 65535.0
    return vector
