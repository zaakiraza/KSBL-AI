from __future__ import annotations

from app.models.schemas import ReviewArtifact
from app.services.state import QUIZZES, now_utc


EDITABLE_FIELDS = [
    "stem",
    "options",
    "correctOptionId",
    "trueFalseCorrect",
    "blanks",
    "shortAnswerReferenceAnswers",
    "shortAnswerRubric",
    "rationale",
    "difficulty",
    "topic",
]


def export_review_artifact(quiz_id: str) -> ReviewArtifact:
    quiz = QUIZZES[quiz_id]
    return ReviewArtifact(
        quizId=quiz_id,
        version=quiz["version"],
        editableFields=EDITABLE_FIELDS,
        questions=[question for question in quiz["questions"]],
    )


def import_review_artifact(review_artifact: ReviewArtifact, editor_id: str) -> dict:
    quiz = QUIZZES[review_artifact.quizId]
    previous_version = quiz["version"]
    quiz["version"] = previous_version + 1
    quiz["reviewArtifact"] = review_artifact.model_dump()
    quiz["lastEditorId"] = editor_id
    quiz["updatedAt"] = now_utc()
    return {
        "quizId": review_artifact.quizId,
        "previousVersion": previous_version,
        "newVersion": quiz["version"],
        "diffs": ["review artifact replaced"],
    }
