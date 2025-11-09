# =====================================================================
# Base stage - installs dependencies and builds Python environment
# =====================================================================
FROM python:3.11-slim AS base

WORKDIR /app

# Environment setup
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# System dependencies for psycopg2, PDFs, images, etc.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements early for better caching
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy full project
COPY . .

# Copy entrypoint and make executable
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh

# Default command (overridden by docker-compose)
CMD ["/app/docker/entrypoint.sh", "web"]

# =====================================================================
# Worker stage (Celery)
# =====================================================================
FROM base AS worker
RUN pip install --no-cache-dir celery==5.4.0
CMD ["/app/docker/entrypoint.sh", "worker"]

# =====================================================================
# Flower stage (Celery monitoring dashboard)
# =====================================================================
FROM base AS flower
RUN pip install --no-cache-dir celery==5.4.0 flower==2.0.1
CMD ["/app/docker/entrypoint.sh", "flower"]