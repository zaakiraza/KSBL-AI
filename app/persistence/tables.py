from __future__ import annotations

from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, SQLModel


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: str
    class_id: str
    title: str
    created_at: datetime | None = None


class Chunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    page_start: int
    page_end: int
    section_path: str
    text: str
    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(8)))


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="document.id")
    version: int = 1
    status: str = "draft"
    policy_json: str = "{}"
    created_at: datetime | None = None


class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    type: str
    topic: str
    difficulty: str
    stem: str
    options_json: str = "[]"
    answer_key_json: str = "{}"
    citations_json: str = "[]"
    rationale: str | None = None
    version: int = 1


class Attempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    student_id: str
    submitted_at: datetime | None = None
    responses_json: str = "[]"


class Result(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="attempt.id")
    total_score: float = 0.0
    max_score: float = 0.0
    breakdown_json: str = "[]"
    feedback_json: str = "{}"
    created_at: datetime | None = None
