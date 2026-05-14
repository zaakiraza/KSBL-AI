# AI Quiz Agent

FastAPI service for document-to-quiz generation and attempt grading.

## What this scaffold includes

- FastAPI app with routes for ingestion, quiz generation, review, approval, attempt grading, and results lookup
- Mock generation/grading logic to keep the project runnable before Vertex AI integration
- Celery worker tasks for async generation and grading
- HMAC signing utilities for agent-to-platform communication
- In-memory state store for local development

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/health/live`
- `http://127.0.0.1:8000/docs`

## Notes

- The current implementation uses an in-memory store so you can run it without Postgres or Redis.
- The project is structured so you can replace the mock services with Vertex AI, Redis, and pgvector later.

## Auto-generation behavior

- When you upload a file via `POST /v1/ingestions` (multipart form-data with `file`), the service now auto-generates a draft quiz immediately using default generation preferences. The quiz draft is stored in-memory and can be accessed via the quizzes APIs (e.g., `GET /v1/quizzes/{quiz_id}/review-export`) or approved with `POST /v1/quizzes/{quiz_id}/approve`.
- The ingestion API response shape is unchanged; clients that need the quiz ID can list or export from the quizzes APIs after upload, or still call `POST /v1/quizzes/generate` to regenerate with custom preferences.
