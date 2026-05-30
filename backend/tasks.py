import os
import sys

# Compute the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if not os.path.exists(os.path.join(project_root, "backend")):
    if project_root in sys.path:
        sys.path.remove(project_root)
    project_root = os.path.dirname(project_root)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from celery import Celery

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