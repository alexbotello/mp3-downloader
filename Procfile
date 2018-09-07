web: gunicorn server:app
worker: celery -A tasks:celery worker --loglevel=DEBUG