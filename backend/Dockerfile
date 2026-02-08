FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
WORKDIR /backend
COPY requirements/ ./requirements/
RUN pip install -r requirements/prod.txt

COPY src /backend/src
COPY scripts /backend/scripts
RUN chmod +x /backend/scripts/*.sh