# VSCode Debug Setup for FastAPI

## Overview
This guide explains how to debug the FastAPI application in VSCode, both locally and with Docker.

## Prerequisites

1. **VSCode Extensions:**
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - Docker (ms-azuretools.vscode-docker)

2. **Local Python Environment:**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate it
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies
   uv pip install -e .
   ```

## Debug Configurations

Three debug configurations have been created in `.vscode/launch.json`:

### 1. FastAPI - Local Debug
**Use this when:** You want to debug the FastAPI app running locally on your machine.

**Setup:**
1. Stop the Docker app container: `docker-compose stop app`
2. Keep other services running: PostgreSQL, Redis, MinIO, etc.
3. In VSCode, select "FastAPI - Local Debug" from the Run and Debug dropdown
4. Set breakpoints in your code
5. Press F5 to start debugging

**Note:** This connects to Docker services on localhost ports (5432, 6379, 9000)

### 2. FastAPI - Docker Remote Debug
**Use this when:** You want to debug the FastAPI app running inside Docker.

**Setup:**
1. Build the debug Docker image:
   ```bash
   docker build -f Dockerfile.debug -t v2-app-debug .
   ```

2. Update docker-compose.yml temporarily:
   ```yaml
   app:
     image: v2-app-debug  # Use debug image
     ports:
       - "8000:8000"
       - "5678:5678"  # Add debug port
   ```

3. Restart the app container:
   ```bash
   docker-compose up -d app
   ```

4. In VSCode, select "FastAPI - Docker Remote Debug"
5. Set breakpoints
6. Press F5 to attach to the container

### 3. Python: Current File
**Use this when:** You want to debug a standalone Python script.

## Setting Breakpoints

1. Click in the gutter (left of line numbers) to set a breakpoint
2. Red dot appears indicating breakpoint is set
3. When code execution reaches the breakpoint, it will pause

## Debug Panel Features

When debugging:
- **Variables:** View all local and global variables
- **Watch:** Monitor specific expressions
- **Call Stack:** See the execution path
- **Breakpoints:** Manage all breakpoints
- **Debug Console:** Execute Python expressions in current context

## Common Debug Scenarios

### Debug API Endpoint
```python
# app/main.py
@app.get("/health")
async def health_check():
    # Set breakpoint here
    result = await check_all_services()  # <- Click left of this line
    return result
```

### Debug Service Method
```python
# app/services/database_service.py
async def initialize(self):
    # Set breakpoint to inspect connection params
    self.pool = await asyncpg.create_pool(
        dsn=self.connection_string,
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
    )
```

### Debug Background Task
```python
# app/services/embedding_service.py
async def generate_embedding(self, text: str):
    # Set breakpoint to inspect embedding generation
    embedding = self.model.encode(text)
    return embedding.tolist()
```

## Troubleshooting

### Issue: Can't connect to services when debugging locally
**Solution:** Ensure Docker services are running and ports are exposed:
```bash
docker-compose ps
# Should show postgres:5432, redis:6379, minio:9000 exposed
```

### Issue: Breakpoints not hitting in Docker debug
**Solution:** Ensure you're using the debug Dockerfile and debugpy is waiting:
```bash
docker logs v2-poc-app
# Should show: "Waiting for debugger attach..."
```

### Issue: Module not found errors
**Solution:** Install dependencies in your local virtual environment:
```bash
.venv\Scripts\activate  # or source .venv/bin/activate
uv pip install -e .
```

## Hot Reload During Debug

The debug configurations include `--reload` flag, so:
1. Make code changes
2. Save the file
3. Uvicorn automatically reloads
4. Breakpoints remain active

## Environment Variables

The debug configuration loads from `.env` file. To override:
1. Edit `.vscode/launch.json`
2. Modify the `env` section
3. Or update `.env` file directly

## Performance Tips

1. **Use conditional breakpoints:** Right-click breakpoint → "Edit Breakpoint" → Add condition
2. **Log points:** Instead of stopping, log values (right-click → "Add Logpoint")
3. **Debug specific tests:** Use pytest with debugger:
   ```python
   import pdb; pdb.set_trace()  # Add in test
   ```

## VSCode Shortcuts

- **F5:** Start/Continue debugging
- **F10:** Step over
- **F11:** Step into
- **Shift+F11:** Step out
- **Shift+F5:** Stop debugging
- **F9:** Toggle breakpoint
- **Ctrl+Shift+F5:** Restart debugging

## Debug Output

Check these panels in VSCode:
- **Terminal:** Shows FastAPI startup logs
- **Debug Console:** Interactive Python during debugging
- **Output → Python:** Shows debugger connection status
- **Problems:** Shows any code issues

## Production vs Debug

**Never use debug mode in production!**

Production should use the standard Dockerfile:
```bash
docker build -t v2-app .
```

Debug mode adds overhead and security risks:
- Debugger port exposed (5678)
- Waits for debugger connection
- Additional dependencies (debugpy)

---

## Quick Start

1. **Local debugging (recommended for development):**
   ```bash
   # Terminal 1: Start services
   docker-compose up -d postgres redis minio
   
   # VSCode: Press F5 with "FastAPI - Local Debug" selected
   ```

2. **Docker debugging (for container-specific issues):**
   ```bash
   # Build debug image
   docker build -f Dockerfile.debug -t v2-app-debug .
   
   # Run with debug image
   docker-compose up -d
   
   # VSCode: Press F5 with "FastAPI - Docker Remote Debug" selected
   ```

Happy debugging! 🐛🔍