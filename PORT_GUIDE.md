# Port Configuration Guide

## Service Ports Overview

| Service | Docker Host Port | Container Port | Notes |
|---------|------------------|----------------|-------|
| **NPM (Proxy)** | 80, 443 | 80, 443 | Main Entrypoint |
| **NPM Admin** | 81 | 81 | Admin UI |
| **FastAPI Dev** | 8001 | 8000 | Direct Access |
| **FastAPI Prod** | - | 8000 | Access via NPM (`api.pocmaster...`) |
| **PostgreSQL** | 5432 | 5432 | Direct Access |
| **Redis** | 6379 | 6379 | Direct Access |
| **MinIO API** | 9000 | 9000 | Direct Access |
| **MinIO Console** | 9001 | 9001 | Direct Access |
| **pgAdmin** | 5050 | 80 | Direct Access |
| **Mongo Express** | 8082 | 8081 | Direct Access |
| **Redis Commander** | 8084 | 8081 | Direct Access |
| **Heimdall** | 8086 | 80 | Main Dashboard |
| **Beszel** | 8090 | 8090 | Monitoring |

## Docker vs Local Development

You can run the Docker environment and a local instance simultaneously without conflicts:

### 1. Docker Dev Container
- **URL:** `http://localhost:8001` (or `http://api-dev.pocmaster.argentquest.com`)
- **Port:** 8001 mapped to container 8000
- **Use for:** Integration testing, hot-reload within Docker

### 2. Docker Production Container
- **URL:** `http://api.pocmaster.argentquest.com`
- **Port:** Not exposed directly (accessed via NPM on port 80/443)
- **Use for:** Production-like verification

### 3. Local Python (VS Code Debug)
- **URL:** `http://localhost:8000` (Default uvicorn port)
- **Port:** 8000 (Host machine)
- **Use for:** Fast debugging with breakpoints

## Quick Connection Check

```bash
# Check Docker Dev App
curl http://localhost:8001/health

# Check Production App (via NPM)
curl -H "Host: api.pocmaster.argentquest.com" http://localhost/health

# Check Local App (if running)
curl http://localhost:8000/health
```

## Port Forwarding for Remote Development

If using WSL2, Remote SSH, or Codespaces:

```json
// .vscode/settings.json
{
    "remote.autoForwardPorts": true,
    "remote.forwardPorts": [
        8001,  // Docker FastAPI Dev
        8000,  // Local Debug FastAPI (if running)
        5432,  // PostgreSQL
        6379,  // Redis
        9000,  // MinIO API
        9001,  // MinIO Console
        5050,  // pgAdmin
        8084,  // Redis Commander
        8086,  // Heimdall Dashboard
        5678   // n8n
    ]
}
```

## Modes Summary

### Docker Dev Version (8001):
- For testing changes in container
- For hot-reload development
- For integration testing

### Docker Prod Version (Domain):
- For final validation
- For performance verification

### Local Debug (8000):
- For rapid iteration
- For breakpoint debugging

## Environment-Specific Testing

```bash
# Test with Docker Dev environment
curl -X POST http://localhost:8001/test-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "docker-dev"}'

# Test with Production environment
curl -X POST http://pocmaster.argentquest.com/test-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "production"}'
```

## Troubleshooting Ports

### Check what's using a port:
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

### Kill process using a port:
```bash
# Windows (use PID from netstat)
taskkill /PID <PID> /F

# Linux/Mac
kill -9 $(lsof -t -i:8000)
```

### Docker port mapping issues:
```bash
# Check Docker port bindings
docker ps --format "table {{.Names}}\t{{.Ports}}"

# Restart with specific port
docker-compose up -d --force-recreate app
```

## Summary

- **Docker FastAPI:** http://localhost:8000 (production-like)
- **Debug FastAPI:** http://localhost:8001 (with breakpoints)
- **Both can run simultaneously** without conflicts
- **All other services** remain on their standard ports
- **Perfect for A/B testing** and debugging production issues