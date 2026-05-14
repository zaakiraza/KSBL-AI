from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


QuestionType = Literal["mcq", "true_false", "fitb", "short_answer"]


class IngestionCreateRequest(BaseModel):
    teacherId: str
    classId: str
    title: str
    url: str | None = None


class IngestionResponse(BaseModel):
    ingestionId: str
    status: Literal["accepted", "processed"]
    title: str
    docType: str
    stats: dict[str, int] = Field(default_factory=dict)


class GenerationPreferences(BaseModel):
    count: int = 20
    questionTypes: list[QuestionType] = Field(default_factory=lambda: ["mcq", "true_false", "fitb", "short_answer"])
    difficultyMix: dict[str, int] = Field(default_factory=lambda: {"easy": 20, "medium": 60, "hard": 20})
    coverage: Literal["even"] = "even"
    timeLimitMin: int = 30
    marksPerQuestion: int = 1


class QuizGenerateRequest(BaseModel):
    ingestionId: str
    preferences: GenerationPreferences = Field(default_factory=GenerationPreferences)


class Citation(BaseModel):
    docId: str
    page: int | None = None
    span: str | None = None


class QuizOption(BaseModel):
    optionId: str
    text: str


class FitbBlank(BaseModel):
    blankId: str
    correctAnswers: list[str]
    variants: list[str] = Field(default_factory=list)


class RubricCriterion(BaseModel):
    criterionId: str
    description: str
    points: int


class QuizQuestion(BaseModel):
    questionId: str
    type: QuestionType
    stem: str
    topic: str
    difficulty: Literal["easy", "medium", "hard"]
    options: list[QuizOption] = Field(default_factory=list)
    correctOptionId: str | None = None
    trueFalseCorrect: bool | None = None
    blanks: list[FitbBlank] = Field(default_factory=list)
    shortAnswerReferenceAnswers: list[str] = Field(default_factory=list)
    shortAnswerRubric: list[RubricCriterion] = Field(default_factory=list)
    rationale: str | None = None
    citations: list[Citation] = Field(default_factory=list)


class QuizDraftResponse(BaseModel):
    quizId: str
    title: str
    version: int
    timeLimitSec: int
    questions: list[QuizQuestion]
    confidence: dict[str, float | list[str]]


class ReviewArtifact(BaseModel):
    quizId: str
    version: int
    editableFields: list[str]
    questions: list[QuizQuestion]


class ReviewImportRequest(BaseModel):
    reviewArtifact: ReviewArtifact
    editorId: str
    comment: str | None = None


class ApproveQuizRequest(BaseModel):
    version: int
    approverId: str


class ApproveQuizResponse(BaseModel):
    quizId: str
    version: int
    signedAt: datetime
    etag: str
    pushStatus: str | None = None


class AttemptResponse(BaseModel):
    questionId: str
    choiceId: str | None = None
    trueFalse: bool | None = None
    blankAnswers: list[str] = Field(default_factory=list)
    shortAnswerText: str | None = None


class AttemptSubmission(BaseModel):
    attemptId: str
    quizId: str
    studentId: str
    classId: str
    teacherId: str
    startedAt: datetime
    submittedAt: datetime
    responses: list[AttemptResponse]


class AttemptBatchSubmission(BaseModel):
    attempts: list[AttemptSubmission]


class AttemptSubmitResponse(BaseModel):
    jobId: str
    attemptId: str
    status: Literal["queued", "graded"]


class BatchSubmitResponse(BaseModel):
    jobs: list[AttemptSubmitResponse]


class SectionBreakdown(BaseModel):
    sectionId: str
    score: float
    maxScore: float


class QuestionResult(BaseModel):
    questionId: str
    type: QuestionType
    correct: bool
    score: float
    maxScore: float
    chosenAnswer: str | None = None
    referenceAnswer: str | None = None
    rationale: str | None = None
    evidenceSources: list[Citation] = Field(default_factory=list)


class Feedback(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    studySuggestions: list[str] = Field(default_factory=list)


class ResultResponse(BaseModel):
    studentId: str
    classId: str
    teacherId: str
    quizId: str
    attemptId: str
    totalScore: float
    maxScore: float
    sectionBreakdown: list[SectionBreakdown]
    questions: list[QuestionResult]
    feedback: Feedback
    metadata: dict[str, str]
