from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.settings import get_settings
from app.models.schemas import ApproveQuizRequest, QuizDraftResponse, QuizGenerateRequest, ReviewImportRequest, ReviewArtifact
from app.services.platform_push import push_approved_quiz
from app.services.quiz_service import approve_quiz, generate_quiz_bundle
from app.services.review_service import export_review_artifact, import_review_artifact
from app.services.state import INGESTIONS, QUIZZES

router = APIRouter(prefix="/v1/quizzes", tags=["quizzes"])


@router.post("/generate", response_model=QuizDraftResponse)
def generate_quiz(request: QuizGenerateRequest) -> QuizDraftResponse:
    ingestion = INGESTIONS.get(request.ingestionId)
    if not ingestion:
        raise HTTPException(status_code=404, detail="Ingestion not found.")
    draft, _ = generate_quiz_bundle(ingestion, request.preferences)
    return draft


@router.get("/{quiz_id}/review-export", response_model=ReviewArtifact)
def get_review_export(quiz_id: str) -> ReviewArtifact:
    if quiz_id not in QUIZZES:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return export_review_artifact(quiz_id)


@router.post("/{quiz_id}/review-import")
def review_import(quiz_id: str, request: ReviewImportRequest) -> dict:
    if quiz_id not in QUIZZES:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    return import_review_artifact(request.reviewArtifact, request.editorId)


@router.post("/{quiz_id}/approve")
async def approve(quiz_id: str, request: ApproveQuizRequest) -> dict:
    if quiz_id not in QUIZZES:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    approval = approve_quiz(quiz_id, request.version, request.approverId)
    settings = get_settings()
    quiz = QUIZZES[quiz_id]
    push_payload = {
        "quizId": quiz_id,
        "version": request.version,
        "title": quiz["title"],
        "timeLimitSec": quiz["timeLimitSec"],
        "questions": quiz["questions"],
    }
    push_status = await push_approved_quiz(settings.quiz_push_url, push_payload)
    approval.pushStatus = str(push_status)
    return approval.model_dump()
