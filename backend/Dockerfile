FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
WORKDIR /backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
  && rm -rf /var/lib/apt/lists/*

COPY requirements/ ./requirements/
RUN pip install -r requirements/prod.txt

COPY src /backend/src
COPY scripts /backend/scripts
RUN chmod +x /backend/scripts/*.sh