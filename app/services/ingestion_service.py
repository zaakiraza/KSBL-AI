from __future__ import annotations

import html
import os
import re
import tempfile
from pathlib import Path
from typing import Any

import httpx
from pdfminer.high_level import extract_text

from app.services.state import new_id


WORD_RE = re.compile(r"\s+")
TAG_RE = re.compile(r"<[^>]+>")
HEADER_RE = re.compile(r"^(?:header|footer)\s*[:\-]", re.IGNORECASE)


def normalize_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\r", "\n")
    text = TAG_RE.sub(" ", text)
    text = WORD_RE.sub(" ", text)
    return text.strip()


def fetch_html(url: str) -> str:
    try:
        response = httpx.get(url, timeout=20.0)
        response.raise_for_status()
        return response.text
    except Exception:
        return f"Placeholder content fetched from {url}."


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(pdf_bytes)
        temp_path = temp_file.name
    try:
        return extract_text(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def clean_text_blocks(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    filtered = [line for line in lines if not HEADER_RE.match(line)]
    deduped: list[str] = []
    previous = None
    for line in filtered:
        if line != previous:
            deduped.append(line)
        previous = line
    return "\n".join(deduped)


def chunk_text(text: str, chunk_size_words: int = 120, overlap_words: int = 20) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(len(words), start + chunk_size_words)
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = max(0, end - overlap_words)
    return chunks


def build_ingestion_record(*, teacher_id: str, class_id: str, title: str, raw_text: str, source_kind: str) -> dict[str, Any]:
    cleaned = clean_text_blocks(normalize_text(raw_text))
    chunks = chunk_text(cleaned)
    chunk_records = []
    for index, chunk in enumerate(chunks):
        chunk_records.append(
            {
                "chunkId": new_id("chunk"),
                "chunkIndex": index,
                "text": chunk,
                "sectionPath": f"{title} / section {index + 1}",
                "pageStart": index + 1,
                "pageEnd": index + 1,
            }
        )
    return {
        "ingestionId": new_id("ingestion"),
        "teacherId": teacher_id,
        "classId": class_id,
        "title": title,
        "sourceKind": source_kind,
        "rawText": cleaned,
        "chunks": chunk_records,
        "stats": {
            "characters": len(cleaned),
            "words": len(cleaned.split()),
            "chunks": len(chunk_records),
        },
    }
