FROM python:3.6-slim
WORKDIR /app
COPY hacker /app/hacker
COPY ouroboros /app/ouroboros
COPY core /app/core
COPY static /app/static
COPY templates /app/templates
COPY manage.py /app/manage.py
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt