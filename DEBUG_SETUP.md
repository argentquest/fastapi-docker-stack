# Debug Setup for Argentquest Development Suite

## Overview
This guide explains how to debug the FastAPI application in VS Code within the comprehensive 22-container development environment. The system provides multiple debugging approaches including local debugging, Docker container debugging, and browser-based debugging through VS Code Server.

## Prerequisites

1. **VSCode Extensions:**
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - Docker (ms-azuretools.vscode-docker)

2. **System Setup:**
   ```bash
   # Ensure all 22 containers are running
   docker compose up -d
   
   # Validate system health
   python health-check.py
   ./validate-database-setup.sh
   ```

3. **Environment Configuration:**
   Ensure your environment files are properly configured:
   - **`.env`** - Main configuration for local development
   - **`.env.dev`** - Development container settings (app-dev)
   - **`.env.prod`** - Production container settings (app-prod)

4. **Local Python Environment:**
   ```bash
   # Create virtual environment
   python3.13 -m venv .venv
   
   # Activate it
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   
   # Install dependencies
   pip install uv
   uv pip install -e .
   ```

5. **Domain Access Setup:**
   Ensure your hosts file includes required entries:
   ```
   127.0.0.1    pocmaster.argentquest.com
   127.0.0.1    api.pocmaster.argentquest.com
   127.0.0.1    api-dev.pocmaster.argentquest.com
   127.0.0.1    code.pocmaster.argentquest.com
   ```

## Debug Configurations

Multiple debugging approaches are available for the 22-container development environment:

## 🔧 1. Local VS Code Debugging

### 1.1 FastAPI - Local Debug (Recommended)
**Use this when:** You want to debug the FastAPI app running locally with full debugging capabilities.

**Setup:**
1. Keep all Docker services running (databases, monitoring, etc.)
2. In VS Code, select "FastAPI - Local Debug" from the Run and Debug dropdown
3. Set breakpoints in your code
4. Press F5 to start debugging

**Configuration:**
- **Environment**: Uses `.env` file for database connections
- **Database connections**: `postgres:5432`, `mongodb:27017`, `redis:6379` (Docker network)
- **Debug URL**: `http://localhost:8001` (different from container ports)
- **Hot reload**: Enabled for rapid development

### 1.2 FastAPI - Container Debug 
**Use this when:** You need to debug within the actual app-dev container environment.

**Setup:**
1. Ensure app-dev container is running with hot-reload:
   ```bash
   docker compose logs -f app-dev  # Should show uvicorn --reload
   ```
2. Use remote debugging techniques or container attach
3. Debug through the volume-mounted code in `./app/`

**Container Details:**
- **Container**: `aq-devsuite-app-dev`
- **Environment**: Uses `.env.dev` file
- **URL**: `http://api-dev.pocmaster.argentquest.com`
- **Features**: Debug logging, single worker, hot-reload

## 🌐 2. Browser-Based Debugging (VS Code Server)

### VS Code Server Debug
**Use this when:** You want to debug in a browser or on a different machine.

**Access:**
- **URL**: http://code.pocmaster.argentquest.com
- **Password**: `dev123` (configurable in `.env`)
- **Features**: Full VS Code experience in browser with debugging capabilities

**Setup:**
1. Navigate to VS Code Server URL
2. Open the project directory
3. Set up debugging configurations within the browser VS Code
4. Access all containers and logs directly

## 🐳 3. Container-Specific Debugging

### Debugging in app-dev vs app-prod
**Development Container (app-dev):**
- **Purpose**: Hot-reload development with debug features
- **URL**: http://api-dev.pocmaster.argentquest.com
- **Logging**: Debug level with detailed output
- **Workers**: Single worker for easier debugging
- **Environment**: `.env.dev`

**Production Container (app-prod):**
- **Purpose**: Production-like testing environment  
- **URL**: http://api.pocmaster.argentquest.com
- **Logging**: Info level with performance focus
- **Workers**: Multiple workers (4)
- **Environment**: `.env.prod`

### Container Access Commands
```bash
# Access development container
docker exec -it aq-devsuite-app-dev bash

# Access production container  
docker exec -it aq-devsuite-app-prod bash

# View logs in real-time
docker compose logs -f app-dev
docker compose logs -f app-prod

# Compare environment configurations
docker exec aq-devsuite-app-dev env | grep DATABASE_URL
docker exec aq-devsuite-app-prod env | grep DATABASE_URL
```

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

### Debug API Endpoints
```python
# app/main.py
@app.get("/health")
async def health_check():
    # Set breakpoint here to inspect system health
    result = await check_all_services()  # <- Click left of this line
    return result

@app.get("/api/v1/stories")
async def get_stories():
    # Debug database interactions with test data
    stories = await story_service.get_all_stories()  # <- Breakpoint
    return stories
```

### Debug Database Connections
```python
# app/services/database_service.py
async def initialize(self):
    # Set breakpoint to inspect connection params
    # Note: Uses Docker container names (postgres:5432)
    self.pool = await asyncpg.create_pool(
        dsn=self.connection_string,  # <- Inspect this value
        min_size=settings.DB_POOL_MIN_SIZE,
        max_size=settings.DB_POOL_MAX_SIZE,
    )
    
# app/services/mongodb_service.py  
async def get_user_profiles(self):
    # Debug MongoDB queries with test data
    cursor = self.db.users.find({})  # <- Breakpoint here
    return await cursor.to_list(length=100)
```

### Debug Environment-Specific Behavior
```python
# app/core/config.py
class Settings(BaseSettings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set breakpoint to inspect loaded environment
        print(f"Environment: {self.APP_ENV}")  # <- Debug environment loading
        print(f"Database URL: {self.DATABASE_URL}")
        
# Debug different behaviors in dev vs prod
if settings.APP_ENV == "development":
    # Development-specific code path
    logger.setLevel(logging.DEBUG)  # <- Breakpoint
else:
    # Production-specific code path  
    logger.setLevel(logging.INFO)   # <- Breakpoint
```

### Debug with Test Data
```python
# Debugging with comprehensive test data
async def debug_test_data():
    # PostgreSQL test data (5 users, 5 stories, 6 world elements)
    users = await db.fetch("SELECT * FROM users")  # <- Breakpoint
    stories = await db.fetch("SELECT * FROM stories WHERE genre = 'fantasy'")
    
    # MongoDB test data (5 users, 3 documents, 3 world elements)  
    mongo_users = await mongo_db.users.find({"writing_style": "Descriptive"}).to_list(None)
    
    return {"pg_users": len(users), "mongo_users": len(mongo_users)}
```

## Troubleshooting

### Issue: Can't connect to databases when debugging locally
**Problem:** Local debug can't reach PostgreSQL/MongoDB
**Solution:** Ensure all Docker services are running:
```bash
# Check all 22 containers are healthy
python health-check.py

# Verify database containers specifically
docker ps | grep -E "(postgres|mongodb|redis)"
# Should show: aq-devsuite-postgres, aq-devsuite-mongodb, aq-devsuite-redis

# Test database connections
./validate-database-setup.sh
```

### Issue: Environment variables not loading correctly
**Problem:** Wrong database connection strings or missing configurations
**Solution:** Check environment file loading:
```bash
# Verify environment files exist and contain correct values
cat .env | grep DATABASE_URL
cat .env.dev | grep DATABASE_URL
cat .env.prod | grep DATABASE_URL

# Compare with running containers
docker exec aq-devsuite-app-dev env | grep DATABASE_URL
docker exec aq-devsuite-app-prod env | grep DATABASE_URL
```

### Issue: Hot-reload not working in app-dev container
**Problem:** File changes not reflected automatically
**Solution:** Check volume mount and container status:
```bash
# Verify volume mount
docker inspect aq-devsuite-app-dev --format '{{range .Mounts}}{{.Source}} → {{.Destination}}{{"\n"}}{{end}}'

# Check if uvicorn is running with --reload
docker compose logs app-dev | grep reload

# Restart the development container
docker compose restart app-dev
```

### Issue: Cannot access domain-based URLs
**Problem:** http://api-dev.pocmaster.argentquest.com not accessible
**Solution:** Verify hosts file and NPM proxy setup:
```bash
# Check hosts file entries (Windows: C:\Windows\System32\drivers\etc\hosts)
# Should contain: 127.0.0.1    api-dev.pocmaster.argentquest.com

# Verify NPM proxy is running and configured
curl http://localhost:81
python scripts/npm-simple-setup.py

# Test direct port access as fallback
curl http://localhost:8003/health  # app-dev direct port
```

### Issue: Containers not starting or unhealthy
**Problem:** Some of the 22 containers failing to start
**Solution:** Diagnose container health:
```bash
# Check all container statuses
docker compose ps

# View logs for failing containers
docker compose logs [container-name]

# Common fixes:
docker compose down
docker compose up -d

# For persistent issues, clean and rebuild
docker compose down --volumes
docker compose up -d --build
```

### Issue: Module not found or import errors
**Problem:** Python dependencies missing in local environment
**Solution:** Ensure virtual environment is properly set up:
```bash
# Recreate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install all dependencies
pip install uv
uv pip install -e .
```

### Issue: VS Code Server not accessible
**Problem:** Cannot access http://code.pocmaster.argentquest.com
**Solution:** Check VS Code Server container and configuration:
```bash
# Check VS Code Server container
docker ps | grep vscode

# View VS Code Server logs
docker compose logs vscode

# Verify password in .env file
grep VSCODE_PASSWORD .env
```

## Hot Reload During Debug

### Local Debug Hot Reload
When debugging locally:
1. Make code changes in `./app/` directory
2. Save the file  
3. Uvicorn automatically reloads (if `--reload` flag is enabled)
4. Breakpoints remain active after reload

### Container Hot Reload (app-dev)
The app-dev container provides automatic hot-reload:
1. Edit files in `./app/` on your host machine
2. Volume mount (`./app:/app/app`) syncs changes to container
3. Uvicorn detects changes and reloads automatically
4. Test changes at http://api-dev.pocmaster.argentquest.com

## Environment Variables

### Environment File Priority
Debug configurations load environment variables in this order:
1. **Local Debug**: Uses `.env` file (main configuration)
2. **app-dev container**: Uses `.env.dev` file 
3. **app-prod container**: Uses `.env.prod` file

### Customizing Environment for Debug
```bash
# Option 1: Edit the appropriate environment file
nano .env        # For local debugging
nano .env.dev    # For app-dev container debugging
nano .env.prod   # For app-prod container debugging

# Option 2: Temporarily override in VS Code launch.json
# Edit .vscode/launch.json → "env" section

# Option 3: Use environment-specific debugging
# Debug with different configurations to test environment differences
```

### Environment Variable Debugging
```python
# Add to your code to debug environment loading
import os
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"APP_ENV: {os.getenv('APP_ENV')}")
print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL')}")

# Compare environments
def debug_env_comparison():
    """Debug function to compare environment settings"""
    local_db_url = os.getenv('DATABASE_URL')
    app_env = os.getenv('APP_ENV', 'unknown')
    
    print(f"Running in: {app_env}")
    print(f"Database: {local_db_url}")
    return {"env": app_env, "db_url": local_db_url}
```

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

## 🚀 Quick Start Guide

### Option 1: Local Debugging (Recommended)
**Best for:** Active development with full debugging capabilities

```bash
# 1. Start all 22 containers
docker compose up -d

# 2. Wait for initialization and validate
sleep 60
python health-check.py

# 3. In VS Code: Select "FastAPI - Local Debug" and press F5
# 4. Access at: http://localhost:8001 (local debug port)
# 5. Compare with container: http://api-dev.pocmaster.argentquest.com
```

### Option 2: Browser-Based Debugging
**Best for:** Remote development or when VS Code isn't available locally

```bash
# 1. Ensure all containers are running
docker compose up -d

# 2. Access VS Code Server in browser
# URL: http://code.pocmaster.argentquest.com
# Password: dev123

# 3. Set up debugging configurations in browser VS Code
# 4. Debug with full container access
```

### Option 3: Container Debugging
**Best for:** Environment-specific issues or production testing

```bash
# 1. Start containers and verify app-dev hot-reload
docker compose up -d
docker compose logs -f app-dev | grep reload

# 2. Make code changes in ./app/ directory  
# 3. Changes automatically sync to container
# 4. Test at: http://api-dev.pocmaster.argentquest.com
```

## 📊 Debug Environment Summary

| Debug Method | Environment File | Database Host | URL | Best For |
|--------------|------------------|---------------|-----|----------|
| **Local Debug** | `.env` | `postgres:5432` | `localhost:8001` | Active development |
| **VS Code Server** | `.env` | `postgres:5432` | `code.pocmaster.argentquest.com` | Remote development |
| **app-dev Container** | `.env.dev` | `postgres:5432` | `api-dev.pocmaster.argentquest.com` | Container-specific issues |
| **app-prod Container** | `.env.prod` | `postgres:5432` | `api.pocmaster.argentquest.com` | Production testing |

## 🔧 System Information

- **Total Containers**: 22 services
- **Database Test Data**: Comprehensive test datasets in both PostgreSQL and MongoDB
- **Hot-Reload**: Enabled in app-dev container via volume mount
- **Environment Files**: Three configurations for different use cases
- **Monitoring**: System Monitor, Beszel, and Portainer available
- **Security Note**: Development system with known vulnerabilities (not production-ready)

Happy debugging! 🐛🔍

---

**Last Updated**: December 26, 2025  
**System**: Argentquest Development Suite (22 containers)  
**Debug Methods**: Local, Browser-based, Container debugging