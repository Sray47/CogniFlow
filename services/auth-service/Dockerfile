# Authentication Service Dockerfile
# Multi-stage build for production-ready container with security best practices

FROM python:3.11-slim as base

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/code \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /code

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8003

# Development command with auto-reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]

# Production stage (commented for future use)
# FROM base as production
# 
# # Copy requirements and install production dependencies only
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt \
#     && pip uninstall -y pip setuptools
# 
# # Copy application code
# COPY . .
# 
# # Change ownership to non-root user
# RUN chown -R appuser:appuser /code
# 
# # Switch to non-root user
# USER appuser
# 
# # Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8003/health || exit 1
# 
# # Production command
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003", "--workers", "4"]
