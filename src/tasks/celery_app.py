from celery import Celery
from src.config import settings


celery_instance = Celery(
    "task_name",
    broker=settings.REDIS_URL,
    include=["src.tasks.tasks"],
)



# celery -A src.tasks.celery_app:celery_instance worker --loglevel=info --pool=solo