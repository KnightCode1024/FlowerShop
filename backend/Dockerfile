FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
WORKDIR /backend
COPY requirements.txt /backend/

RUN pip install --no-cache-dir -r /backend/requirements.txt