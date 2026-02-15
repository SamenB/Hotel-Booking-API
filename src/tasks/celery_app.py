from celery import Celery
from src.config import settings


celery_instance = Celery(
    "hotel_booking_app",
    broker=settings.REDIS_URL,
    include=["src.tasks.tasks"],
)
# celery -A src.tasks.celery_app:celery_instance worker --loglevel=info --pool=solo


celery_instance.conf.beat_schedule = {
    "send-emails-to-users-with-today-checkin": {
        "task": "booking_tooday_checkin",
        "schedule": 5,  # every 5 s
    },
}
# celery -A src.tasks.celery_app:celery_instance beat --loglevel=info
