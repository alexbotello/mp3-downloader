web: gunicorn server:app
worker: celery -A server:celery worker --loglevel=DEBUG