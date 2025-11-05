Worker app placeholder. Move background job logic here under `src/`.

Structure:
- src/podcast/ - Podcast generation tasks
- src/tasks/ - Celery task definitions
- src/processing/ - Data processing tasks

Run: `celery -A src.tasks worker --loglevel=info` (after moving code)
