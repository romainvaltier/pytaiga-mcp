# Multi-stage build for pytaiga-mcp
# Stage 1: Build environment
FROM python:3.10-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_CACHE=1

# Install system dependencies for building
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
        ca-certificates \
        build-essential \
        && \
    rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Copy project files
WORKDIR /build
COPY pyproject.toml pyproject.toml
COPY README.md README.md
COPY src/ src/

# Install dependencies using uv
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt

# Stage 2: Runtime image
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        && \
    rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN useradd -m -u 1000 appuser

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy application source
COPY --chown=appuser:appuser src/ src/

# Switch to non-root user
USER appuser

# Default environment variables
ENV TAIGA_TRANSPORT=stdio \
    LOG_LEVEL=INFO \
    SESSION_EXPIRY=28800

# Expose port for SSE mode
EXPOSE 8000

# Copy entrypoint script with executable permissions
COPY --chmod=755 entrypoint.sh /app/entrypoint.sh

# Start the MCP server
ENTRYPOINT ["/app/entrypoint.sh"]
