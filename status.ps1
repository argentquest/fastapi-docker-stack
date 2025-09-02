# V2 POC Docker Status Check Script for Windows
# This script shows the current status of all containers and services

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    V2 POC ENVIRONMENT STATUS CHECK            " -ForegroundColor Cyan
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

# Function to format container status
function Get-ContainerHealth {
    param($ContainerName)
    
    $health = docker inspect --format='{{.State.Health.Status}}' $ContainerName 2>$null
    if ($LASTEXITCODE -eq 0) {
        switch ($health) {
            "healthy" { return "✓ Healthy", "Green" }
            "unhealthy" { return "✗ Unhealthy", "Red" }
            "starting" { return "◐ Starting", "Yellow" }
            default { return "◯ No Health Check", "Gray" }
        }
    }
    return "✗ Not Found", "Red"
}

# Check Docker status
Write-Host "Docker Desktop Status:" -ForegroundColor Yellow
if (Test-DockerRunning) {
    Write-Host "✓ Docker is running" -ForegroundColor Green
}
else {
    Write-Host "✗ Docker is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start Docker Desktop first." -ForegroundColor Yellow
    Write-Host "Run: .\start.ps1" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host ""
Write-Host "Container Status:" -ForegroundColor Yellow
Write-Host "-----------------" -ForegroundColor Gray

# Define containers to check
$containers = @(
    @{Name="aq-devsuite-postgres"; Display="PostgreSQL"; Type="Database"},
    @{Name="aq-devsuite-redis"; Display="Redis"; Type="Cache"},
    @{Name="aq-devsuite-minio"; Display="MinIO"; Type="Storage"},
    @{Name="aq-devsuite-mongodb"; Display="MongoDB"; Type="Database"},
    @{Name="aq-devsuite-app-dev"; Display="App Dev"; Type="Application"},
    @{Name="aq-devsuite-app-prod"; Display="App Prod"; Type="Application"}
)

$runningCount = 0
$healthyCount = 0

foreach ($container in $containers) {
    $status = docker inspect --format='{{.State.Status}}' $container.Name 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        if ($status -eq "running") {
            $runningCount++
            $healthInfo = Get-ContainerHealth $container.Name
            $healthStatus = $healthInfo[0]
            $healthColor = $healthInfo[1]
            
            if ($healthStatus -like "*Healthy*") {
                $healthyCount++
            }
            
            Write-Host "$($container.Display.PadRight(12)) " -NoNewline
            Write-Host "[$($container.Type.PadRight(12))]" -ForegroundColor DarkGray -NoNewline
            Write-Host " Running " -ForegroundColor Green -NoNewline
            Write-Host "- $healthStatus" -ForegroundColor $healthColor
        }
        else {
            Write-Host "$($container.Display.PadRight(12)) " -NoNewline
            Write-Host "[$($container.Type.PadRight(12))]" -ForegroundColor DarkGray -NoNewline
            Write-Host " Stopped" -ForegroundColor Red
        }
    }
    else {
        Write-Host "$($container.Display.PadRight(12)) " -NoNewline
        Write-Host "[$($container.Type.PadRight(12))]" -ForegroundColor DarkGray -NoNewline
        Write-Host " Not Found" -ForegroundColor DarkGray
    }
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "--------" -ForegroundColor Gray
Write-Host "Containers Running: $runningCount / $($containers.Count)" -ForegroundColor $(if ($runningCount -eq $containers.Count) { "Green" } elseif ($runningCount -gt 0) { "Yellow" } else { "Red" })
Write-Host "Containers Healthy: $healthyCount / $runningCount" -ForegroundColor $(if ($healthyCount -eq $runningCount) { "Green" } elseif ($healthyCount -gt 0) { "Yellow" } else { "Red" })

# Check port availability
Write-Host ""
Write-Host "Port Status:" -ForegroundColor Yellow
Write-Host "------------" -ForegroundColor Gray

$ports = @(
    @{Port=8001; Service="Frontend Claude"},
    @{Port=5432; Service="PostgreSQL"},
    @{Port=6379; Service="Redis"},
    @{Port=9000; Service="MinIO API"},
    @{Port=9001; Service="MinIO Console"},
    @{Port=27017; Service="MongoDB"}
)

foreach ($portInfo in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $portInfo.Port -WarningAction SilentlyContinue -InformationLevel Quiet
    
    Write-Host "$($portInfo.Service.PadRight(20))" -NoNewline
    Write-Host "Port $($portInfo.Port.ToString().PadRight(6))" -ForegroundColor DarkGray -NoNewline
    
    if ($connection) {
        Write-Host "✓ Open" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Closed" -ForegroundColor Red
    }
}

# Check disk usage
Write-Host ""
Write-Host "Docker Disk Usage:" -ForegroundColor Yellow
Write-Host "------------------" -ForegroundColor Gray

$diskUsage = docker system df 2>$null
if ($LASTEXITCODE -eq 0) {
    $lines = $diskUsage -split "`n"
    foreach ($line in $lines) {
        if ($line -match "Images|Containers|Local Volumes|Build Cache") {
            Write-Host $line -ForegroundColor Gray
        }
    }
}

# Service URLs
if ($runningCount -gt 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "    SERVICE ACCESS POINTS                      " -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    
    if ($runningCount -ge 4) {
        Write-Host "Frontend Claude:  " -NoNewline; Write-Host "http://localhost:8001/claude/" -ForegroundColor Cyan
        Write-Host "API Docs:        " -NoNewline; Write-Host "http://localhost:8001/docs" -ForegroundColor Cyan
        Write-Host "Health Check:    " -NoNewline; Write-Host "http://localhost:8001/health" -ForegroundColor Cyan
        Write-Host "MinIO Console:   " -NoNewline; Write-Host "http://localhost:9001" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "Database Connections:" -ForegroundColor Yellow
        Write-Host "PostgreSQL:      " -NoNewline; Write-Host "postgresql://pocuser:pocpass@localhost:5432/poc_dev" -ForegroundColor DarkGray
        Write-Host "MongoDB:         " -NoNewline; Write-Host "mongodb://mongoadmin:mongopass123@localhost:27017" -ForegroundColor DarkGray
        Write-Host "Redis:           " -NoNewline; Write-Host "redis://localhost:6379" -ForegroundColor DarkGray
    }
    else {
        Write-Host "Some services are not running. Start all services with:" -ForegroundColor Yellow
        Write-Host ".\start.ps1" -ForegroundColor Cyan
    }
}
else {
    Write-Host ""
    Write-Host "No containers are running." -ForegroundColor Red
    Write-Host "Start the environment with:" -ForegroundColor Yellow
    Write-Host ".\start.ps1" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")