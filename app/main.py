from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.attempts import router as attempts_router
from app.api.routers.health import router as health_router
from app.api.routers.ingestions import router as ingestions_router
from app.api.routers.quizzes import router as quizzes_router
from app.api.routers.results import router as results_router


app = FastAPI(title="AI Quiz Agent", version="0.1.0")

# CORS for local development: allow LAN access from other devices and expose X-Quiz-Id header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Quiz-Id"],
)

app.include_router(health_router)
app.include_router(ingestions_router)
app.include_router(quizzes_router)
app.include_router(attempts_router)
app.include_router(results_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "ai-quiz-agent", "status": "running"}
