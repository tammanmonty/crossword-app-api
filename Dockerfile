# Metadata: specifies the author of this Docker image
LABEL authors="Tamman Montanaro"
#ENTRYPOINT ["top", "-b"]

# Multi-stage build for FastAPI Crossword Clues API
# Use Python 3.8 slim image as base (smaller size, fewer packages)
# Stage 1: Builder stage
FROM python:3.8-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r crosswrd_api_svc && useradd -r -g crosswrd_api_svc crosswrd_api_svc

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=crosswrd_api_svc:crosswrd_api_svc ./src ./src
COPY --chown=crosswrd_api_svc:crosswrd_api_svc requirements.txt ./

# Create logs directory with proper permissions
RUN mkdir -p logs && chown -R crosswrd_api_svc:crosswrd_api_svc logs

# Switch to non-root user
USER appuser

# Expose the API port (default 8000)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthcheck').read()" || exit 1

# Run the application using uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
