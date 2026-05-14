from celery import Celery

from app.core.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "quiz_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.task_routes = {
    "workers.tasks.generate_quiz_task": {"queue": "generate"},
    "workers.tasks.grade_attempt_task": {"queue": "grade"},
    "workers.tasks.deliver_results_task": {"queue": "notify"},
}
