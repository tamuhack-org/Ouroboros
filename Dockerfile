FROM python:3.6-slim
WORKDIR /app
COPY ouroboros /app/ouroboros
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
