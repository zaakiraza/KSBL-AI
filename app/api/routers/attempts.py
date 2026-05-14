from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import AttemptBatchSubmission, AttemptSubmitResponse, AttemptSubmission, ResultResponse
from app.services.grading_service import grade_attempt
from app.services.state import ATTEMPTS, QUIZZES, RESULTS, new_id

router = APIRouter(prefix="/v1", tags=["attempts"])


@router.post("/attempts:submit", response_model=AttemptSubmitResponse)
def submit_attempt(request: AttemptSubmission) -> AttemptSubmitResponse:
    quiz = QUIZZES.get(request.quizId)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    attempt_payload = request.model_dump()
    ATTEMPTS[request.attemptId] = attempt_payload
    result = grade_attempt(quiz, attempt_payload)
    RESULTS[request.attemptId] = result.model_dump()
    return AttemptSubmitResponse(jobId=new_id("job"), attemptId=request.attemptId, status="graded")


@router.post("/attempts:batch")
def submit_attempt_batch(request: AttemptBatchSubmission) -> dict:
    jobs = [submit_attempt(attempt).model_dump() for attempt in request.attempts]
    return {"jobs": jobs}
