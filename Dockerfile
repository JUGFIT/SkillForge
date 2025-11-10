#Dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# Copy entrypoint script
COPY docker/entrypoint.sh /app/docker/entrypoint.sh

# Make sure it's executable (even in cached layers)
RUN chmod +x /app/docker/entrypoint.sh && \
    ls -la /app/docker/entrypoint.sh

# Use bash to execute the entrypoint (more reliable in CI/CD)
ENTRYPOINT ["/bin/bash", "/app/docker/entrypoint.sh"]
