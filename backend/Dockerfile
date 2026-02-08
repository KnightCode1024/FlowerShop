FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /backend
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Copy application source and scripts relative to build context (./backend)
COPY src /backend/src
COPY scripts /backend/scripts
RUN chmod +x /backend/scripts/*.sh