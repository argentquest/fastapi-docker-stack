@echo off
REM Argentquest Development Suite - Windows Setup Script
REM This script provides one-command setup for Windows contributors

setlocal enabledelayedexpansion

echo 🚀 Setting up Argentquest Development Suite...
echo    22-Container Development Environment (Windows)
echo.

echo 📋 Setup Steps:
echo    1. Creating environment files
echo    2. Starting Docker containers
echo    3. Waiting for initialization
echo    4. Setting up proxy hosts
echo    5. Validating deployment
echo.

REM Step 1: Create environment files
echo 📝 Step 1: Creating environment files...
if not exist .env (
    copy .env.template .env >nul
    echo    ✅ Created .env from template
) else (
    echo    ⚠️  .env already exists, skipping
)

if not exist .env.dev (
    copy .env.template .env.dev >nul
    echo    ✅ Created .env.dev from template
) else (
    echo    ⚠️  .env.dev already exists, skipping
)

if not exist .env.prod (
    copy .env.template .env.prod >nul
    echo    ✅ Created .env.prod from template
) else (
    echo    ⚠️  .env.prod already exists, skipping
)

REM Check if Docker is running
echo.
echo 🐳 Step 2: Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo    ❌ Docker is not installed or not in PATH
    echo    Please install Docker Desktop and try again
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo    ❌ Docker is not running
    echo    Please start Docker Desktop and try again
    pause
    exit /b 1
)

echo    ✅ Docker is running

REM Step 2: Start containers
echo.
echo 🚀 Step 3: Starting all 22 containers...
echo    This may take several minutes on first run...
docker-compose up -d

REM Step 3: Wait for initialization
echo.
echo ⏳ Step 4: Waiting for container initialization...
echo    Waiting 60 seconds for services to start up...
timeout /t 60 /nobreak >nul

REM Step 4: Set up NPM proxy (if script exists)
echo.
echo 🌐 Step 5: Setting up proxy hosts...
if exist "scripts\npm-simple-setup.py" (
    python scripts\npm-simple-setup.py 2>nul || echo    ⚠️  Proxy setup failed, you may need to run this manually
) else (
    echo    ⚠️  NPM setup script not found, skipping proxy configuration
)

REM Step 5: Validate deployment
echo.
echo ✅ Step 6: Validating deployment...
if exist "health-check.py" (
    echo    Running health check...
    python health-check.py 2>nul || echo    ⚠️  Some services may still be starting
) else (
    echo    ⚠️  Health check script not found
)

if exist "validate-database-setup.sh" (
    echo    Validating database setup...
    bash validate-database-setup.sh 2>nul || echo    ⚠️  Database validation failed, may need more time
) else (
    echo    ⚠️  Database validation script not found
)

REM Final status
echo.
echo 🎉 Setup Complete!
echo.
echo 📍 Access Points:
echo    🏠 Main Dashboard:    http://pocmaster.argentquest.com
echo    🔧 Development API:   http://api-dev.pocmaster.argentquest.com
echo    🏭 Production API:    http://api.pocmaster.argentquest.com
echo    🗄️  Database Admin:   http://pgadmin.pocmaster.argentquest.com
echo    🐳 Container Mgmt:    http://localhost:9443
echo.
echo 📚 Next Steps:
echo    1. Check http://pocmaster.argentquest.com for service dashboard
echo    2. Review CONTRIBUTING.md for development workflow
echo    3. Look at 'good first issue' labels in GitHub Issues
echo    4. Join our community discussions on GitHub
echo.
echo ❓ Need Help?
echo    - Check DEBUG_SETUP.md for troubleshooting
echo    - Run: docker-compose ps (to check container status)
echo    - Run: python health-check.py (to validate services)
echo    - Create an issue on GitHub if problems persist
echo.
echo ⚠️  Note: This is a development environment with default credentials.
echo    See SECURITY.md before any production use.
echo.
pause