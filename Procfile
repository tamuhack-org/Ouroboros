web: gunicorn hiss.wsgi:application --log-file -
worker: celery -A hiss.celery worker --loglevel=info