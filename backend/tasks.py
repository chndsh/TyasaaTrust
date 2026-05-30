from celery import Celery
import os

# Rename your variable instance to matches Celery's default inspection pattern
celery = Celery(
    'tasks',
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

@celery.task
def my_background_task():
    return "Task completed"


#placeholder app