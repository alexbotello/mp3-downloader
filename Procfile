web: gunicorn --chdir server server:app
worker: celery -A server.tasks:celery worker --loglevel=DEBUG