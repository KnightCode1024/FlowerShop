FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
WORKDIR /backend
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application source and scripts relative to build context (./backend)
COPY src /backend/src
COPY scripts /backend/scripts
RUN chmod +x /backend/scripts/*.sh