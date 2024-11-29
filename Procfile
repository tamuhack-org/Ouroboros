web: gunicorn hiss.wsgi --log-file -
worker: celery -A hiss worker.celery --loglevel=info