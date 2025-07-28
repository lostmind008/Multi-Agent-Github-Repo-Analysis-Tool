# Multi-Agent GitHub Repository Analysis Tool
# Built by LostMind AI (www.LostMindAI.com)
# Multi-stage build for optimal container size

# Build stage
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILDPLATFORM
ARG TARGETPLATFORM

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-updated.txt .
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-updated.txt

# Production stage
FROM python:3.11-slim as production

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r analyzer && useradd -r -g analyzer analyzer

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=analyzer:analyzer . .

# Create necessary directories
RUN mkdir -p /app/reports && \
    chown -R analyzer:analyzer /app

# Switch to non-root user
USER analyzer

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0 if __import__('src.config') else 1)"

# Default command
CMD ["python", "main.py", "--help"]

# Labels for metadata
LABEL maintainer="LostMind AI <info@lostmindai.com>" \
      description="Multi-Agent GitHub Repository Analysis Tool" \
      version="2.0.0" \
      url="https://github.com/lostmind008/Multi-Agent-Github-Repo-Analysis-Tool" \
      vendor="LostMind AI" \
      license="MIT"