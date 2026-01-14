# Docker Deployment Guide - pytaiga-mcp v0.2.0

This guide covers deploying pytaiga-mcp using Docker for development, testing, and production environments.

## Quick Start - 5 Minutes

### Option 1: Docker Compose (Recommended)

The easiest way to get everything running:

```bash
# Clone the repository
git clone https://github.com/romainvaltier/pytaiga-mcp.git
cd pytaiga-mcp

# Start all services (Taiga + pytaiga-mcp)
docker-compose up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose ps

# Access services
# Taiga Frontend: http://localhost:9000
# pytaiga-mcp: http://localhost:8000 (SSE mode)
```

### Option 2: Docker Build Only

If you have Taiga running separately:

```bash
# Build the Docker image
docker build -t pytaiga-mcp:latest .

# Run the container
docker run -d \
  --name pytaiga-mcp \
  -e TAIGA_API_URL=https://your-taiga-instance.com \
  -e TAIGA_TRANSPORT=sse \
  -p 8000:8000 \
  pytaiga-mcp:latest

# Check logs
docker logs -f pytaiga-mcp
```

---

## Detailed Setup Guide

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 4GB RAM minimum
- 2GB free disk space

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Docker Network                    │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Taiga      │  │   pytaiga    │  │  PostgreSQL│ │
│  │  Frontend    │  │     MCP      │  │            │ │
│  │  (Port 9000) │  │  (Port 8000) │  │ (Internal) │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘ │
│         │                 │                 │        │
│         └─────────────────┼─────────────────┘        │
│                           │                          │
│  ┌──────────────┐  ┌──────┴──────┐  ┌────────────┐  │
│  │   Taiga      │  │    Redis    │  │  Volumes   │  │
│  │   Backend    │  │   (Cache)   │  │  (Persist) │  │
│  │ (Port 8001)  │  │ (Internal)  │  │            │  │
│  └──────────────┘  └─────────────┘  └────────────┘  │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### Step 1: Start Docker Compose Stack

```bash
# Pull latest images
docker-compose pull

# Start all services in background
docker-compose up -d

# Watch initialization logs
docker-compose logs -f
```

Wait for all services to become healthy (check with `docker-compose ps`).

### Step 2: Initialize Taiga

```bash
# Create Taiga database and seed data
docker-compose exec taiga-backend \
  python manage.py migrate

# Create superuser (optional)
docker-compose exec taiga-backend \
  python manage.py createsuperuser
```

### Step 3: Verify pytaiga-mcp is Running

```bash
# Check container status
docker-compose ps pytaiga-mcp

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs pytaiga-mcp
```

---

## Configuration

### Environment Variables

All configuration is done via environment variables in `docker-compose.yml`:

#### Taiga Configuration
```yaml
TAIGA_API_URL=http://taiga-backend:8000  # Internal network address
ALLOW_HTTP_TAIGA=true                    # OK for Docker (local network)
```

#### MCP Server Configuration
```yaml
TAIGA_TRANSPORT=sse                      # Use SSE for Docker (HTTP-based)
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR
```

#### Session Configuration
```yaml
SESSION_EXPIRY=28800                     # 8 hours in seconds
MAX_CONCURRENT_SESSIONS=5                # Max sessions per user
```

#### Rate Limiting
```yaml
RATE_LIMIT_REQUESTS=5                    # Attempts per window
RATE_LIMIT_WINDOW=900                    # Window size in seconds (15 min)
RATE_LIMIT_LOCKOUT_SECONDS=1800          # Lockout duration (30 min)
```

#### API Configuration
```yaml
REQUEST_TIMEOUT=30                       # API request timeout
MAX_CONNECTIONS=10                       # Connection pool size
MAX_KEEPALIVE_CONNECTIONS=5              # Keepalive connections
```

### Using Environment File

Create `.env.docker` for custom settings:

```bash
# Create .env.docker
cat > .env.docker << 'EOF'
TAIGA_API_URL=http://taiga-backend:8000
TAIGA_TRANSPORT=sse
LOG_LEVEL=DEBUG
SESSION_EXPIRY=86400
MAX_CONCURRENT_SESSIONS=10
EOF

# Use with docker-compose
docker-compose --env-file .env.docker up -d
```

---

## Usage

### Accessing the Services

```bash
# Taiga Frontend
# Username: admin (default)
# Password: 123123 (default)
http://localhost:9000

# pytaiga-mcp Server (SSE mode)
http://localhost:8000

# Taiga Backend API (for direct testing)
http://localhost:8001/api/v1/
```

### Connecting MCP Client

#### Claude Desktop

Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "taiga": {
      "command": "docker",
      "args": ["exec", "-i", "pytaiga-mcp-server", "python", "-m", "src.server"],
      "env": {
        "TAIGA_API_URL": "http://localhost:9000",
        "ALLOW_HTTP_TAIGA": "true"
      }
    }
  }
}
```

#### Direct HTTP (SSE Mode)

```bash
# Login via HTTP (SSE mode)
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "host": "http://localhost:9000",
    "username": "admin",
    "password": "123123"
  }'
```

#### Using Docker exec

```bash
# Test via docker exec (stdio mode)
docker-compose exec pytaiga-mcp \
  python -m src.server
```

---

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f pytaiga-mcp

# Last 100 lines
docker-compose logs --tail=100 pytaiga-mcp

# Taiga backend errors
docker-compose logs taiga-backend | grep ERROR
```

### Stop/Start Services

```bash
# Stop all services
docker-compose stop

# Start all services
docker-compose start

# Restart specific service
docker-compose restart pytaiga-mcp

# Restart all services
docker-compose restart
```

### Remove Everything

```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes (warning: deletes data)
docker-compose down -v
```

### Execute Commands in Container

```bash
# Run shell command
docker-compose exec pytaiga-mcp bash

# Run Python commands
docker-compose exec pytaiga-mcp python -c "import src.server; print('OK')"

# Run tests
docker-compose exec pytaiga-mcp pytest tests/ -v
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs pytaiga-mcp

# Check health status
docker-compose ps

# Rebuild and restart
docker-compose up -d --build
```

### Can't Connect to Taiga

```bash
# Verify Taiga is running and healthy
docker-compose ps taiga-backend

# Check logs for errors
docker-compose logs taiga-backend

# Test network connectivity
docker-compose exec pytaiga-mcp \
  curl http://taiga-backend:8000/api/v1/auth
```

### Permission Denied Errors

```bash
# Fix container permissions
docker-compose exec pytaiga-mcp \
  chown -R appuser:appuser /app

# Or rebuild
docker-compose build --no-cache pytaiga-mcp
```

### High Memory Usage

```bash
# Check container stats
docker stats pytaiga-mcp

# Reduce resource limits in docker-compose.yml
services:
  pytaiga-mcp:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Session Issues

```bash
# Clear sessions (remove and restart)
docker-compose restart pytaiga-mcp

# Check session logs
docker-compose logs pytaiga-mcp | grep -i session
```

---

## Production Deployment

### Security Considerations

1. **Use HTTPS**: Configure reverse proxy (nginx/traefik)
2. **Change Secrets**: Update `SECRET_KEY` in taiga-backend
3. **Use Strong Passwords**: Change default database password
4. **Network Isolation**: Restrict external access to internal services
5. **Health Checks**: Monitor container health
6. **Logging**: Centralize logs to ELK or similar

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  pytaiga-mcp:
    build: .
    restart: always
    environment:
      - TAIGA_API_URL=https://your-taiga-domain.com
      - TAIGA_TRANSPORT=sse
      - LOG_LEVEL=WARNING
      - SESSION_EXPIRY=3600  # 1 hour for production
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
    networks:
      - taiga-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 60s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pytaiga-mcp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pytaiga-mcp
  template:
    metadata:
      labels:
        app: pytaiga-mcp
    spec:
      containers:
      - name: pytaiga-mcp
        image: your-registry/pytaiga-mcp:v0.2.0
        ports:
        - containerPort: 8000
        env:
        - name: TAIGA_API_URL
          value: https://taiga.your-domain.com
        - name: TAIGA_TRANSPORT
          value: sse
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Using Docker Registry

```bash
# Build and push to registry
docker build -t your-registry/pytaiga-mcp:v0.2.0 .
docker push your-registry/pytaiga-mcp:v0.2.0

# Use in docker-compose
services:
  pytaiga-mcp:
    image: your-registry/pytaiga-mcp:v0.2.0
```

---

## Performance Tuning

### Connection Pooling

```yaml
environment:
  - MAX_CONNECTIONS=20
  - MAX_KEEPALIVE_CONNECTIONS=10
  - REQUEST_TIMEOUT=60
```

### Rate Limiting

```yaml
environment:
  - RATE_LIMIT_REQUESTS=100
  - RATE_LIMIT_WINDOW=60
```

### Session Management

```yaml
environment:
  - SESSION_EXPIRY=86400
  - MAX_CONCURRENT_SESSIONS=10
```

### Resource Limits

```yaml
services:
  pytaiga-mcp:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

---

## Monitoring

### Health Check

```bash
# Check if healthy
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "0.2.0"}
```

### Container Stats

```bash
# Real-time stats
docker stats pytaiga-mcp

# Format: CPU%, Memory Usage, Memory Limit, Net I/O, Block I/O
```

### Log Aggregation

```bash
# View last 100 lines
docker-compose logs --tail=100 pytaiga-mcp

# Follow logs in real-time
docker-compose logs -f pytaiga-mcp

# Filter by level
docker-compose logs pytaiga-mcp | grep ERROR
```

---

## Update/Upgrade

### Update Docker Images

```bash
# Pull latest images
docker-compose pull

# Rebuild pytaiga-mcp (if changed)
docker-compose build --no-cache pytaiga-mcp

# Restart with new images
docker-compose up -d
```

### Version-Specific Deployment

```bash
# Specify version
docker-compose build --build-arg VERSION=v0.2.0 .
docker run pytaiga-mcp:v0.2.0
```

---

## Backup & Restore

### Backup Database

```bash
# Backup PostgreSQL
docker-compose exec taiga-db \
  pg_dump -U taiga taiga > taiga_backup.sql

# Backup Taiga media
docker cp pytaiga-taiga-db:/var/lib/postgresql/data ./db_backup
```

### Restore Database

```bash
# Restore PostgreSQL
docker-compose exec -T taiga-db \
  psql -U taiga taiga < taiga_backup.sql
```

---

## Next Steps

1. **Access Taiga Frontend**: http://localhost:9000
2. **Create Test Project**: Add sample data in Taiga
3. **Test pytaiga-mcp**: Use curl or MCP client to test
4. **Configure for Production**: Update environment variables and secrets
5. **Set Up Monitoring**: Implement health checks and logging

---

## Related Documentation

- **[README.md](../../README.md)** - Main project documentation
- **[docs/testing/](../testing/)** - Testing guide (works with Docker)
- **[docs/testing/E2E_TESTING_GUIDE.md](../testing/E2E_TESTING_GUIDE.md)** - E2E testing procedures
- **[CLAUDE.md](../../CLAUDE.md)** - Development patterns

---

**Last Updated**: 2026-01-13
**Version**: v0.2.0
**Status**: ✅ Production Ready
