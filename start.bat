@echo off
REM V2 POC Docker Startup Script for Windows (Batch Version)
REM This script ensures Docker Desktop is running and starts all containers

echo ================================================
echo     V2 POC DOCKER ENVIRONMENT STARTUP
echo ================================================
echo.

REM Check if PowerShell script exists and use it if available
if exist "%~dp0start.ps1" (
    echo Using PowerShell script for better functionality...
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0start.ps1"
    exit /b %ERRORLEVEL%
)

REM Fallback to basic batch commands
echo [1/3] Checking if Docker is running...

docker info >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker is not running. Starting Docker Desktop...
    
    REM Try to start Docker Desktop
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    ) else if exist "%LOCALAPPDATA%\Docker\Docker Desktop.exe" (
        start "" "%LOCALAPPDATA%\Docker\Docker Desktop.exe"
    ) else (
        echo ERROR: Docker Desktop not found. Please install Docker Desktop first.
        echo Download from: https://www.docker.com/products/docker-desktop
        pause
        exit /b 1
    )
    
    echo Waiting for Docker to start (this may take up to 2 minutes)...
    echo Please wait...
    
    :WAIT_DOCKER
    timeout /t 10 /nobreak >nul
    docker info >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Still waiting for Docker...
        goto WAIT_DOCKER
    )
    
    echo Docker Desktop started successfully!
) else (
    echo Docker is already running.
)

echo.
echo [2/3] Starting Docker containers...
echo.

REM Check if docker-compose.yml exists
if not exist "%~dp0docker-compose.yml" (
    echo ERROR: docker-compose.yml not found in current directory.
    echo Please run this script from the V2 project root.
    pause
    exit /b 1
)

REM Start core services first
echo Starting core services (PostgreSQL, Redis, MinIO, MongoDB)...
docker-compose up -d postgres redis minio mongodb

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to start core services
    echo Try running: docker-compose down
    echo Then run this script again
    pause
    exit /b 1
)

REM Wait a bit for services to initialize
echo Waiting for core services to initialize...
timeout /t 10 /nobreak >nul

REM Start app containers
echo.
echo Starting application containers...
docker-compose up -d app-dev app-prod

if %ERRORLEVEL% neq 0 (
    echo WARNING: App containers may have issues starting
) else (
    echo Application containers started
)

echo.
echo [3/3] Verifying deployment...
timeout /t 5 /nobreak >nul

echo.
echo ================================================
echo     CONTAINER STATUS
echo ================================================
docker ps --format "table {{.Names}}\t{{.Status}}"

echo.
echo ================================================
echo     ACCESS POINTS
echo ================================================
echo Frontend Claude:  http://localhost:8001/claude/
echo API Docs:         http://localhost:8001/docs
echo Health Check:     http://localhost:8001/health
echo PostgreSQL:       localhost:5432
echo Redis:            localhost:6379
echo MinIO Console:    http://localhost:9001
echo MongoDB:          localhost:27017

echo.
echo ================================================
echo V2 POC environment is ready!
echo ================================================
echo.

set /p OPEN_BROWSER=Would you like to open the dashboard in your browser? (Y/N): 
if /i "%OPEN_BROWSER%"=="Y" (
    start http://localhost:8001/claude/
)

echo.
pause