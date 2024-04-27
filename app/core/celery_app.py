from celery import Celery
from kombu import Exchange, Queue

from app.core.config import settings


celery_app = Celery(__name__)

celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND

celery_app.conf.task_queues = [
    Queue(
        settings.QUEUE_NAME,
        Exchange(settings.QUEUE_NAME),
        routing_key=settings.QUEUE_NAME,
        queue_arguments={"x-max-priority": 10},
    ),
]
