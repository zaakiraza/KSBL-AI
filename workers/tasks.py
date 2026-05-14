from __future__ import annotations

from workers.celery_app import celery_app


@celery_app.task(name="workers.tasks.generate_quiz_task")
def generate_quiz_task(ingestion_id: str, preferences: dict) -> dict:
    return {"ingestionId": ingestion_id, "preferences": preferences, "status": "mocked"}


@celery_app.task(name="workers.tasks.grade_attempt_task")
def grade_attempt_task(attempt_payload: dict) -> dict:
    return {"attemptId": attempt_payload.get("attemptId"), "status": "mocked"}


@celery_app.task(name="workers.tasks.deliver_results_task")
def deliver_results_task(attempt_id: str) -> dict:
    return {"attemptId": attempt_id, "delivered": False, "reason": "not_configured"}
