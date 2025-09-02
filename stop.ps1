# V2 POC Docker Shutdown Script for Windows
# This script gracefully stops all containers and optionally cleans up

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    V2 POC DOCKER ENVIRONMENT SHUTDOWN         " -ForegroundColor Cyan
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

# Function to stop containers
function Stop-Containers {
    param(
        [bool]$RemoveVolumes = $false,
        [bool]$RemoveOrphans = $true
    )
    
    if (-not (Test-DockerRunning)) {
        Write-Host "Docker is not running. Nothing to stop." -ForegroundColor Yellow
        return
    }
    
    Write-Host "Checking for running containers..." -ForegroundColor Yellow
    $runningContainers = docker ps --format "{{.Names}}" | Where-Object { $_ -match "aq-devsuite" }
    
    if ($runningContainers.Count -eq 0) {
        Write-Host "No V2 POC containers are currently running." -ForegroundColor Green
        return
    }
    
    Write-Host "Found $($runningContainers.Count) running container(s)" -ForegroundColor Cyan
    Write-Host ""
    
    # Stop containers
    Write-Host "Stopping containers..." -ForegroundColor Yellow
    
    if ($RemoveVolumes) {
        Write-Host "Removing volumes as well (--volumes flag set)..." -ForegroundColor Yellow
        docker-compose down --volumes --remove-orphans 2>&1 | Out-String
    }
    elseif ($RemoveOrphans) {
        docker-compose down --remove-orphans 2>&1 | Out-String
    }
    else {
        docker-compose down 2>&1 | Out-String
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ All containers stopped successfully" -ForegroundColor Green
    }
    else {
        Write-Host "WARNING: Some containers may not have stopped cleanly" -ForegroundColor Yellow
    }
}

# Function to clean Docker system
function Clean-DockerSystem {
    Write-Host ""
    Write-Host "Docker Cleanup Options:" -ForegroundColor Cyan
    Write-Host "1. Remove unused containers, networks, and images" -ForegroundColor Gray
    Write-Host "2. Remove all stopped containers" -ForegroundColor Gray
    Write-Host "3. Remove all unused images" -ForegroundColor Gray
    Write-Host "4. Full system prune (removes everything unused)" -ForegroundColor Gray
    Write-Host "5. Skip cleanup" -ForegroundColor Gray
    Write-Host ""
    
    $choice = Read-Host "Select cleanup option (1-5)"
    
    switch ($choice) {
        "1" {
            Write-Host "Removing unused containers, networks, and images..." -ForegroundColor Yellow
            docker system prune -f 2>&1 | Out-String
            Write-Host "✓ Cleanup completed" -ForegroundColor Green
        }
        "2" {
            Write-Host "Removing all stopped containers..." -ForegroundColor Yellow
            docker container prune -f 2>&1 | Out-String
            Write-Host "✓ Stopped containers removed" -ForegroundColor Green
        }
        "3" {
            Write-Host "Removing unused images..." -ForegroundColor Yellow
            docker image prune -a -f 2>&1 | Out-String
            Write-Host "✓ Unused images removed" -ForegroundColor Green
        }
        "4" {
            Write-Host "WARNING: This will remove all unused Docker resources!" -ForegroundColor Red
            $confirm = Read-Host "Are you sure? (Y/N)"
            if ($confirm -eq 'Y' -or $confirm -eq 'y') {
                Write-Host "Performing full system prune..." -ForegroundColor Yellow
                docker system prune -a --volumes -f 2>&1 | Out-String
                Write-Host "✓ Full cleanup completed" -ForegroundColor Green
            }
            else {
                Write-Host "Cleanup cancelled" -ForegroundColor Yellow
            }
        }
        "5" {
            Write-Host "Skipping cleanup" -ForegroundColor Gray
        }
        default {
            Write-Host "Invalid option. Skipping cleanup" -ForegroundColor Yellow
        }
    }
}

# Main execution
try {
    # Check if docker-compose.yml exists
    if (-not (Test-Path ".\docker-compose.yml")) {
        Write-Host "ERROR: docker-compose.yml not found in current directory." -ForegroundColor Red
        Write-Host "Please run this script from the V2 project root." -ForegroundColor Yellow
        exit 1
    }
    
    # Ask about volume removal
    Write-Host "Stop Options:" -ForegroundColor Cyan
    Write-Host "1. Stop containers only (preserve data)" -ForegroundColor Gray
    Write-Host "2. Stop containers and remove volumes (delete all data)" -ForegroundColor Gray
    Write-Host ""
    
    $stopChoice = Read-Host "Select option (1 or 2)"
    
    if ($stopChoice -eq "2") {
        Write-Host ""
        Write-Host "WARNING: This will delete all data in volumes!" -ForegroundColor Red
        $confirm = Read-Host "Are you sure? (Y/N)"
        if ($confirm -eq 'Y' -or $confirm -eq 'y') {
            Stop-Containers -RemoveVolumes $true
        }
        else {
            Write-Host "Operation cancelled" -ForegroundColor Yellow
            Stop-Containers -RemoveVolumes $false
        }
    }
    else {
        Stop-Containers -RemoveVolumes $false
    }
    
    # Ask about cleanup
    Write-Host ""
    $cleanup = Read-Host "Would you like to clean up Docker resources? (Y/N)"
    if ($cleanup -eq 'Y' -or $cleanup -eq 'y') {
        Clean-DockerSystem
    }
    
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "    SHUTDOWN COMPLETE                          " -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "To restart the environment, run: .\start.ps1" -ForegroundColor Cyan
}
catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")