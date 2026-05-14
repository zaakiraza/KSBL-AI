from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import ResultResponse
from app.services.state import RESULTS

router = APIRouter(prefix="/v1", tags=["results"])


@router.get("/results/{attempt_id}", response_model=ResultResponse)
def get_result(attempt_id: str) -> ResultResponse:
    result = RESULTS.get(attempt_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found.")
    return ResultResponse.model_validate(result)
