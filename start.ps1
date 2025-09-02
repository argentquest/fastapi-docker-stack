# V2 POC Docker Startup Script for Windows
# This script ensures Docker Desktop is running and starts all containers

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    V2 POC DOCKER ENVIRONMENT STARTUP          " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Docker is running
function Test-DockerRunning {
    try {
        $dockerInfo = docker info 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

# Function to start Docker Desktop
function Start-DockerDesktop {
    Write-Host "[1/4] Checking Docker Desktop status..." -ForegroundColor Yellow
    
    if (Test-DockerRunning) {
        Write-Host "✓ Docker Desktop is already running" -ForegroundColor Green
        return $true
    }
    
    Write-Host "✗ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "Starting Docker Desktop..." -ForegroundColor Yellow
    
    # Try to find Docker Desktop in common locations
    $dockerPaths = @(
        "C:\Program Files\Docker\Docker\Docker Desktop.exe",
        "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
        "$env:LOCALAPPDATA\Docker\Docker Desktop.exe",
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    )
    
    $dockerPath = $null
    foreach ($path in $dockerPaths) {
        if (Test-Path $path) {
            $dockerPath = $path
            break
        }
    }
    
    if ($null -eq $dockerPath) {
        Write-Host "ERROR: Docker Desktop not found. Please install Docker Desktop first." -ForegroundColor Red
        Write-Host "Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
    
    # Start Docker Desktop
    Start-Process -FilePath $dockerPath -WindowStyle Hidden
    
    # Wait for Docker to be ready (up to 2 minutes)
    Write-Host "Waiting for Docker Desktop to start (this may take up to 2 minutes)..." -ForegroundColor Yellow
    $maxAttempts = 24  # 24 attempts * 5 seconds = 120 seconds
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 5
        $attempt++
        Write-Host "." -NoNewline -ForegroundColor Yellow
        
        if (Test-DockerRunning) {
            Write-Host ""
            Write-Host "✓ Docker Desktop started successfully!" -ForegroundColor Green
            return $true
        }
    }
    
    Write-Host ""
    Write-Host "ERROR: Docker Desktop failed to start within 2 minutes." -ForegroundColor Red
    Write-Host "Please start Docker Desktop manually and run this script again." -ForegroundColor Yellow
    exit 1
}

# Function to check if containers are already running
function Get-ContainerStatus {
    $runningContainers = docker ps --format "table {{.Names}}\t{{.Status}}" 2>$null
    if ($LASTEXITCODE -eq 0 -and $runningContainers) {
        return $runningContainers
    }
    return $null
}

# Function to start containers
function Start-Containers {
    Write-Host ""
    Write-Host "[2/4] Checking existing containers..." -ForegroundColor Yellow
    
    $containerStatus = Get-ContainerStatus
    if ($containerStatus) {
        Write-Host "Current container status:" -ForegroundColor Cyan
        Write-Host $containerStatus
        
        # Check if our specific containers are running
        $requiredContainers = @(
            "aq-devsuite-postgres",
            "aq-devsuite-redis",
            "aq-devsuite-minio",
            "aq-devsuite-mongodb"
        )
        
        $runningCount = 0
        foreach ($container in $requiredContainers) {
            if ($containerStatus -match $container) {
                $runningCount++
            }
        }
        
        if ($runningCount -eq $requiredContainers.Count) {
            Write-Host "✓ All core services are already running" -ForegroundColor Green
            
            # Check app containers
            if ($containerStatus -match "aq-devsuite-app-dev" -and $containerStatus -match "aq-devsuite-app-prod") {
                Write-Host "✓ App containers are already running" -ForegroundColor Green
                return $true
            }
        }
    }
    
    Write-Host ""
    Write-Host "[3/4] Starting Docker containers..." -ForegroundColor Yellow
    Write-Host "This may take a few minutes on first run..." -ForegroundColor Gray
    
    # Start core services first
    Write-Host ""
    Write-Host "Starting core services (PostgreSQL, Redis, MinIO, MongoDB)..." -ForegroundColor Yellow
    docker-compose up -d postgres redis minio mongodb 2>&1 | Out-String
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to start core services" -ForegroundColor Red
        Write-Host "Try running: docker-compose down" -ForegroundColor Yellow
        Write-Host "Then run this script again" -ForegroundColor Yellow
        exit 1
    }
    
    # Wait for core services to be healthy
    Write-Host "Waiting for core services to be healthy..." -ForegroundColor Yellow
    $maxWait = 60  # 60 seconds
    $waited = 0
    
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 5
        $waited += 5
        Write-Host "." -NoNewline -ForegroundColor Yellow
        
        $healthStatus = docker ps --filter "health=healthy" --format "{{.Names}}" 2>$null
        $healthyCount = ($healthStatus | Where-Object { $_ -match "postgres|redis|minio|mongodb" } | Measure-Object).Count
        
        if ($healthyCount -ge 3) {  # At least 3 of 4 core services healthy
            Write-Host ""
            Write-Host "✓ Core services are healthy" -ForegroundColor Green
            break
        }
    }
    
    # Start app containers
    Write-Host ""
    Write-Host "Starting application containers..." -ForegroundColor Yellow
    docker-compose up -d app-dev app-prod 2>&1 | Out-String
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: App containers may have issues starting" -ForegroundColor Yellow
    }
    else {
        Write-Host "✓ Application containers started" -ForegroundColor Green
    }
    
    return $true
}

# Function to display final status
function Show-FinalStatus {
    Write-Host ""
    Write-Host "[4/4] Verifying deployment..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    $finalStatus = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
    
    if ($finalStatus) {
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "    DEPLOYMENT STATUS                          " -ForegroundColor Green
        Write-Host "================================================" -ForegroundColor Green
        Write-Host $finalStatus
        
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "    ACCESS POINTS                              " -ForegroundColor Green
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "Frontend Claude:  " -NoNewline; Write-Host "http://localhost:8001/claude/" -ForegroundColor Cyan
        Write-Host "API Docs:        " -NoNewline; Write-Host "http://localhost:8001/docs" -ForegroundColor Cyan
        Write-Host "Health Check:    " -NoNewline; Write-Host "http://localhost:8001/health" -ForegroundColor Cyan
        Write-Host "PostgreSQL:      " -NoNewline; Write-Host "localhost:5432" -ForegroundColor Cyan
        Write-Host "Redis:           " -NoNewline; Write-Host "localhost:6379" -ForegroundColor Cyan
        Write-Host "MinIO Console:   " -NoNewline; Write-Host "http://localhost:9001" -ForegroundColor Cyan
        Write-Host "MongoDB:         " -NoNewline; Write-Host "localhost:27017" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Green
        Write-Host "✓ V2 POC environment is ready!" -ForegroundColor Green
        Write-Host "================================================" -ForegroundColor Green
        
        # Optional: Open browser
        $openBrowser = Read-Host "Would you like to open the dashboard in your browser? (Y/N)"
        if ($openBrowser -eq 'Y' -or $openBrowser -eq 'y') {
            Start-Process "http://localhost:8001/claude/"
        }
    }
    else {
        Write-Host "WARNING: Could not verify container status" -ForegroundColor Yellow
        Write-Host "Run 'docker ps' to check container status manually" -ForegroundColor Yellow
    }
}

# Function to handle errors
function Handle-Error {
    param($ErrorMessage)
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Red
    Write-Host "    ERROR OCCURRED                             " -ForegroundColor Red
    Write-Host "================================================" -ForegroundColor Red
    Write-Host $ErrorMessage -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Ensure Docker Desktop is installed" -ForegroundColor Gray
    Write-Host "2. Check if virtualization is enabled in BIOS" -ForegroundColor Gray
    Write-Host "3. Run 'docker-compose logs' to see detailed errors" -ForegroundColor Gray
    Write-Host "4. Try 'docker-compose down' and run this script again" -ForegroundColor Gray
    exit 1
}

# Main execution
try {
    # Check if running as administrator (recommended but not required)
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    if (-not $isAdmin) {
        Write-Host "NOTE: Running without administrator privileges" -ForegroundColor Yellow
        Write-Host "Some Docker operations may require admin rights" -ForegroundColor Yellow
        Write-Host ""
    }
    
    # Check if docker-compose.yml exists
    if (-not (Test-Path ".\docker-compose.yml")) {
        Handle-Error "docker-compose.yml not found in current directory. Please run this script from the V2 project root."
    }
    
    # Start Docker Desktop if needed
    Start-DockerDesktop
    
    # Start containers
    Start-Containers
    
    # Show final status
    Show-FinalStatus
}
catch {
    Handle-Error $_.Exception.Message
}

Write-Host ""
Write-Host "Script completed. Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")