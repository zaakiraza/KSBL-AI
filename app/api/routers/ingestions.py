from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Response

from app.models.schemas import GenerationPreferences, IngestionResponse
from app.services.ingestion_service import build_ingestion_record, extract_text_from_pdf_bytes, fetch_html
from app.services.state import INGESTIONS
from app.services.quiz_service import generate_quiz_bundle

router = APIRouter(prefix="/v1", tags=["ingestions"])


@router.post("/ingestions", response_model=IngestionResponse)
async def create_ingestion(
    response: Response,
    teacherId: str = Form(...),
    classId: str = Form(...),
    title: str = Form(...),
    url: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
) -> IngestionResponse:
    if not file and not url:
        raise HTTPException(status_code=400, detail="Provide either a file upload or a URL.")

    if file:
        raw_bytes = await file.read()
        raw_text = extract_text_from_pdf_bytes(raw_bytes)
        doc_type = file.content_type or "application/pdf"
        source_kind = "upload"
    else:
        raw_text = fetch_html(url or "")
        doc_type = "text/html"
        source_kind = "url"

    record = build_ingestion_record(
        teacher_id=teacherId,
        class_id=classId,
        title=title,
        raw_text=raw_text,
        source_kind=source_kind,
    )
    record["docType"] = doc_type
    INGESTIONS[record["ingestionId"]] = record

    # Auto-generate a quiz immediately after a file upload ingestion completes.
    # This leaves the existing response shape unchanged while making a draft quiz
    # available via the quizzes APIs.
    if source_kind == "upload":
        # Use default generation preferences; clients can still regenerate later if desired.
        try:
            draft, _ = generate_quiz_bundle(record, GenerationPreferences())
            # Expose the new quiz id as a response header without changing the body schema
            response.headers["X-Quiz-Id"] = draft.quizId
        except Exception:
            # Fail silently to avoid breaking file ingestion if quiz generation encounters an error.
            # Clients may call the explicit /v1/quizzes/generate endpoint as a fallback.
            pass
    return IngestionResponse(
        ingestionId=record["ingestionId"],
        status="processed",
        title=title,
        docType=doc_type,
        stats=record["stats"],
    )
