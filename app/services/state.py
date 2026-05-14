from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

INGESTIONS: dict[str, dict[str, Any]] = {}
QUIZZES: dict[str, dict[str, Any]] = {}
ATTEMPTS: dict[str, dict[str, Any]] = {}
RESULTS: dict[str, dict[str, Any]] = {}
JOBS: dict[str, dict[str, Any]] = {}
COUNTERS = defaultdict(int)


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    COUNTERS[prefix] += 1
    return f"{prefix}_{uuid4().hex[:10]}_{COUNTERS[prefix]}"
