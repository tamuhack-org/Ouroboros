FROM python:3.6-slim

WORKDIR /app

COPY hiss /app

RUN python3 -m pip install -r requirements.txt

RUN python3 manage.py collectstatic --no-input

CMD gunicorn -b :$PORT hiss.wsgi:application --capture-output
