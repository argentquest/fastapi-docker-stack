# Port Configuration Guide

## Service Ports Overview

| Service | Docker Mode | Local Debug Mode | No Conflict? |
|---------|------------|------------------|--------------|
| **FastAPI App** | localhost:8000 | localhost:8001 | ✅ Yes |
| **PostgreSQL** | localhost:5432 | localhost:5432 (use Docker) | ✅ Yes |
| **Redis** | localhost:6379 | localhost:6379 (use Docker) | ✅ Yes |
| **MinIO API** | localhost:9000 | localhost:9000 (use Docker) | ✅ Yes |
| **MinIO Console** | localhost:9001 | localhost:9001 (use Docker) | ✅ Yes |
| **pgAdmin** | localhost:5050 | localhost:5050 (use Docker) | ✅ Yes |
| **Redis Commander** | localhost:8081 | localhost:8081 (use Docker) | ✅ Yes |
| **Dashboard** | localhost:8082 | localhost:8082 (use Docker) | ✅ Yes |
| **Nginx Proxy** | localhost:80, 81, 443 | localhost:80, 81, 443 (use Docker) | ✅ Yes |

## Running Both Simultaneously

Now you can run **BOTH** Docker and Local debug at the same time:

### Docker FastAPI (Production-like)
- **URL:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Running in:** Docker container
- **Logs:** `docker-compose logs -f app`

### Local FastAPI (Debug Mode)
- **URL:** http://localhost:8001  ⬅️ Different port!
- **Docs:** http://localhost:8001/docs
- **Running in:** Your local machine with VSCode debugger
- **Logs:** VSCode terminal

## Benefits of This Setup

1. **Compare behavior:** Run production Docker version and debug version side-by-side
2. **No port conflicts:** Each uses different port
3. **Shared services:** Both use the same PostgreSQL, Redis, MinIO instances
4. **Fast debugging:** Local debug with breakpoints
5. **Integration testing:** Test against real services

## Quick Commands

### Start everything (Docker + Debug):
```bash
# Terminal 1: Start all Docker services
docker-compose up -d

# VSCode: Select "FastAPI - Local Debug (Port 8001)" and press F5
```

### Access both versions:
```bash
# Docker version
curl http://localhost:8000/health

# Debug version
curl http://localhost:8001/health
```

### Test specific version:
```python
# Test Docker version
import requests
response = requests.get("http://localhost:8000/health")

# Test Debug version
response = requests.get("http://localhost:8001/health")
```

## Port Forwarding for Remote Development

If using WSL2, Remote SSH, or Codespaces:

```json
// .vscode/settings.json
{
    "remote.autoForwardPorts": true,
    "remote.forwardPorts": [
        8000,  // Docker FastAPI
        8001,  // Local Debug FastAPI
        5432,  // PostgreSQL
        6379,  // Redis
        9000,  // MinIO API
        9001,  // MinIO Console
        5050,  // pgAdmin
        8081,  // Redis Commander
        8082,  // Dashboard
        5678   // Remote debugger (if using)
    ]
}
```

## Switching Between Modes

### Use Docker Version (8000):
- For testing production-like behavior
- For performance testing
- For container-specific issues

### Use Debug Version (8001):
- For development
- For debugging with breakpoints
- For rapid iteration with hot reload
- For inspecting variables

## Environment-Specific Testing

```bash
# Test with Docker environment
curl -X POST http://localhost:8000/test-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "docker"}'

# Test with Debug environment
curl -X POST http://localhost:8001/test-endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "debug"}'
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