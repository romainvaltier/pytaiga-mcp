# Deployment Documentation - pytaiga-mcp v0.2.0

This directory contains comprehensive deployment guides for pytaiga-mcp across different environments.

## Quick Navigation

### 🐳 Docker Deployment (Recommended)
**Start here**: [`DOCKER_DEPLOYMENT.md`](./DOCKER_DEPLOYMENT.md)

- Quick start in 5 minutes
- Complete docker-compose stack (Taiga + MCP)
- Production deployment strategies
- Kubernetes support
- Troubleshooting guide

**Quick Command:**
```bash
git clone https://github.com/romainvaltier/pytaiga-mcp.git
cd pytaiga-mcp
docker-compose up -d
```

Access:
- **Taiga Frontend**: http://localhost:9000
- **pytaiga-mcp MCP**: http://localhost:8000
- **Taiga Backend**: http://localhost:8001/api/v1/

---

## Deployment Options

| Option | Time | Complexity | Best For |
|--------|------|-----------|----------|
| **Docker Compose** | 5 min | Low | Development, Testing, Quick Deployment |
| **Docker Only** | 10 min | Low | When Taiga already running |
| **Kubernetes** | 30 min | High | Production, Scaling, High Availability |
| **Manual Setup** | 30 min | Medium | Custom environments, Learning |

---

## Architecture Diagrams

### Docker Compose Stack

```
┌─────────────────────────────────────────────────────┐
│          Docker Compose Network                      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │   Taiga      │  │   pytaiga    │  External       │
│  │  Frontend    │  │     MCP      │  Access         │
│  │  :9000       │  │   :8000      │  ──────────→   │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                          │
│  ┌──────▼──────────────┐  │                          │
│  │  Taiga Backend      │◄─┘                          │
│  │  (Internal :8000)   │                             │
│  └──────┬──────────────┘                             │
│         │                                             │
│  ┌──────▼──────────┐  ┌──────────┐                   │
│  │  PostgreSQL     │  │  Redis   │                   │
│  │  (Internal)     │  │(Internal)│                   │
│  └─────────────────┘  └──────────┘                   │
└─────────────────────────────────────────────────────┘
```

### Multi-Instance Deployment

```
┌─────────────────────────────────────────────────────┐
│          Kubernetes Cluster                          │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────┐    │
│  │  Ingress / Load Balancer                    │    │
│  │  (Handles HTTPS, Routing)                   │    │
│  └────────────────┬────────────────────────────┘    │
│                   │                                   │
│  ┌────────────────▼─────────┬──────────────────┐    │
│  │                          │                  │    │
│  │  pytaiga-mcp Pod 1   pytaiga-mcp Pod 2     │    │
│  │  (Replica 1)         (Replica 2)           │    │
│  │                                             │    │
│  │  ┌──────────────────────────────────────┐  │    │
│  │  │  Shared PostgreSQL (StatefulSet)     │  │    │
│  │  │  Shared Redis (StatefulSet)          │  │    │
│  │  │  Shared Taiga Backend                │  │    │
│  │  └──────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## Key Features

### ✅ What's Included

- **Multi-stage Docker build** for minimal image size
- **Security hardening**: Non-root user, health checks
- **Complete docker-compose stack**: Taiga + MCP + PostgreSQL + Redis
- **Production-ready configuration**: Resource limits, logging, monitoring
- **Easy environment customization**: .env file support
- **Kubernetes manifests**: Ready for container orchestration
- **Comprehensive logging**: Structured JSON logs
- **Health checks**: Built-in liveness and readiness probes

### 🔐 Security

- Non-root user execution (appuser:1000)
- Health checks and restart policies
- Network isolation via Docker networks
- Environment variable configuration (no hardcoded secrets)
- HTTPS support via reverse proxy
- Rate limiting and session management

### 📊 Monitoring

- Health check endpoints
- Container statistics (CPU, memory, network)
- Structured JSON logging
- Error tracking and alerting ready
- Performance metrics in logs

---

## Getting Started

### Prerequisites

- Docker 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 1.29+ ([Install Docker Compose](https://docs.docker.com/compose/install/))
- 4GB RAM minimum
- 2GB free disk space

### Step 1: Clone Repository

```bash
git clone https://github.com/romainvaltier/pytaiga-mcp.git
cd pytaiga-mcp
```

### Step 2: Start Services

```bash
# Start all services (background mode)
docker-compose up -d

# Or view logs while starting
docker-compose up

# Or build from source first
docker-compose up -d --build
```

### Step 3: Wait for Health

```bash
# Check service status
docker-compose ps

# Wait until all show "Up" and healthy
# Typically takes 30-60 seconds for first-time setup
```

### Step 4: Access Services

```bash
# Taiga Frontend
# Default credentials: admin / 123123
open http://localhost:9000

# pytaiga-mcp Server
curl http://localhost:8000/health
```

### Step 5: Test Login

```bash
# Test authentication
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "host": "http://localhost:9000",
    "username": "admin",
    "password": "123123"
  }'

# Returns session_id for subsequent API calls
```

---

## Configuration

### Default Environment Variables

```bash
# Taiga Configuration
TAIGA_API_URL=http://taiga-backend:8000  # Use service name inside Docker
ALLOW_HTTP_TAIGA=true                    # OK for Docker (local network)

# MCP Server
TAIGA_TRANSPORT=sse                      # Use SSE for HTTP-based clients
LOG_LEVEL=INFO                           # DEBUG, INFO, WARNING, ERROR

# Session Management
SESSION_EXPIRY=28800                     # 8 hours
MAX_CONCURRENT_SESSIONS=5                # Limit per user

# Rate Limiting
RATE_LIMIT_REQUESTS=5                    # Attempts per window
RATE_LIMIT_WINDOW=900                    # 15 minutes
RATE_LIMIT_LOCKOUT_SECONDS=1800          # 30 minutes
```

### Custom Configuration

Create `.env.docker` file:

```bash
# Copy default environment
cp docker-compose.yml .env.docker

# Edit with your settings
# Then use:
docker-compose --env-file .env.docker up -d
```

---

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f pytaiga-mcp

# Restart service
docker-compose restart pytaiga-mcp

# Execute command in container
docker-compose exec pytaiga-mcp bash

# Stop and remove everything
docker-compose down

# Stop, remove, and delete volumes
docker-compose down -v
```

---

## Production Checklist

- [ ] Change Taiga `SECRET_KEY` environment variable
- [ ] Change default database password from `taiga_password`
- [ ] Configure HTTPS with reverse proxy (nginx/traefik)
- [ ] Set `ALLOW_HTTP_TAIGA=false`
- [ ] Update `SESSION_EXPIRY` for security (e.g., 3600 for 1 hour)
- [ ] Set `LOG_LEVEL=WARNING` to reduce noise
- [ ] Configure external backups for database
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting appropriately
- [ ] Test health checks and auto-recovery
- [ ] Load test before going live
- [ ] Document your deployment architecture

---

## Troubleshooting

### Services Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild containers
docker-compose build --no-cache

# Check for port conflicts
netstat -tulpn | grep -E '8000|9000|8001|5432'
```

### Can't Connect to Taiga
```bash
# Verify Taiga is running
docker-compose ps taiga-backend

# Check network connectivity
docker-compose exec pytaiga-mcp \
  curl http://taiga-backend:8000/api/v1/auth
```

### High Memory Usage
```bash
# Check stats
docker stats

# Add resource limits to docker-compose.yml
# See DOCKER_DEPLOYMENT.md for details
```

---

## Performance Benchmarks

Typical resource usage per container:

| Container | CPU | Memory | Notes |
|-----------|-----|--------|-------|
| pytaiga-mcp | 5-20% | 100-300MB | Depends on concurrent sessions |
| taiga-backend | 10-50% | 300-600MB | Peak during heavy load |
| PostgreSQL | 5-15% | 200-400MB | Depends on dataset size |
| Redis | <5% | 50-100MB | Typically low usage |
| taiga-frontend | <1% | 50MB | Static content server |

---

## Related Documentation

- **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)** - Complete Docker guide
- **[../../README.md](../../README.md)** - Main project documentation
- **[../testing/E2E_TESTING_GUIDE.md](../testing/E2E_TESTING_GUIDE.md)** - Testing with Docker
- **[../../CLAUDE.md](../../CLAUDE.md)** - Development patterns
- **[../roadmap/SPRINT_PLANNING.md](../roadmap/SPRINT_PLANNING.md)** - Project roadmap

---

**Last Updated**: 2026-01-13
**Version**: v0.2.0
**Status**: ✅ Production Ready
