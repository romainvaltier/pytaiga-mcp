# Multi-stage build for pytaiga-mcp
# Stage 1: Build environment
FROM python:3.10-slim as builder

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
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project files
WORKDIR /build
COPY pyproject.toml pyproject.toml
COPY README.md README.md
COPY src/ src/

# Install dependencies using uv
ENV PATH="/root/.cargo/bin:$PATH"
RUN /root/.cargo/bin/uv pip compile pyproject.toml -o requirements.txt && \
    /root/.cargo/bin/uv pip install --python /usr/bin/python3.10 -r requirements.txt

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

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default environment variables
ENV TAIGA_TRANSPORT=stdio \
    LOG_LEVEL=INFO \
    SESSION_EXPIRY=28800

# Expose port for SSE mode
EXPOSE 8000

# Start the MCP server
CMD ["python", "-m", "src.server"]
