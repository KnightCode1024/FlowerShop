FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
WORKDIR /backend_flower_shop
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .