# V2 POC Docker Restart Script for Windows
# This script stops all containers and restarts them

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    V2 POC DOCKER ENVIRONMENT RESTART          " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if docker-compose.yml exists
if (-not (Test-Path ".\docker-compose.yml")) {
    Write-Host "ERROR: docker-compose.yml not found in current directory." -ForegroundColor Red
    Write-Host "Please run this script from the V2 project root." -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/3] Stopping all containers..." -ForegroundColor Yellow
docker-compose down --remove-orphans

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some containers may not have stopped cleanly" -ForegroundColor Yellow
}
else {
    Write-Host "✓ All containers stopped" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/3] Starting containers..." -ForegroundColor Yellow

# Start core services first
Write-Host "Starting core services..." -ForegroundColor Gray
docker-compose up -d postgres redis minio mongodb

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start core services" -ForegroundColor Red
    pause
    exit 1
}

# Wait for services to be healthy
Write-Host "Waiting for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 10

# Start app containers
Write-Host "Starting application containers..." -ForegroundColor Gray
docker-compose up -d app-dev app-prod

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: App containers may have issues" -ForegroundColor Yellow
}
else {
    Write-Host "✓ All containers started" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] Verifying restart..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Current container status:" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}"

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "    RESTART COMPLETE                           " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "• Frontend: http://localhost:8001/claude/" -ForegroundColor Gray
Write-Host "• API Docs: http://localhost:8001/docs" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")