# Docker Best Practices Guide - Multi-Platform

## Overview

This comprehensive guide provides platform-specific best practices for running Docker Desktop with optimal performance and resource management across Windows 11, macOS, and Ubuntu 24.04 LTS.

## Table of Contents

- [Windows 11 Best Practices](#windows-11-best-practices)
- [macOS Best Practices](#macos-best-practices) 
- [Ubuntu 24.04 Best Practices](#ubuntu-24-best-practices)
- [Universal Best Practices](#universal-best-practices)

---

# Windows 11 Best Practices

## System Requirements & Recommendations

### Minimum Requirements
- **RAM**: 8GB (16GB+ recommended)
- **CPU**: 4 cores minimum
- **Storage**: 20GB free space for Docker
- **Windows**: Windows 11 with WSL2 support
- **Hyper-V**: Enabled

### Optimal Hardware Configuration

#### By RAM Size
- **32GB RAM**: Use 8GB for WSL2/Docker, 24GB for Windows
- **16GB RAM**: Use 6GB for WSL2/Docker, 10GB for Windows  
- **8GB RAM**: Use 4GB for WSL2/Docker, 4GB for Windows

#### By CPU Configuration
- **4 cores / 8 threads**: Use 2-4 cores for Docker, 4 threads for Windows
- **6 cores / 12 threads**: Use 4 cores for Docker, 8 threads for Windows
- **8 cores / 16 threads**: Use 4-6 cores for Docker, 10+ threads for Windows
- **12+ cores / 24+ threads**: Use 6-8 cores for Docker, 16+ threads for Windows

## Docker Desktop Installation & Setup

### 1. Enable WSL2 Backend
```
Docker Desktop Settings → General:
☑ Use WSL 2 based engine
```

### 2. Configure WSL2 Resource Limits

Create `C:\Users\[YourUsername]\.wslconfig`:

#### For High-End Systems (32GB RAM / 8+ cores):
```ini
[wsl2]
# Set memory to 8GB (25% of total RAM)
memory=8GB

# Use 4-6 CPU cores (half of available cores)
processors=4

# Set swap to 2GB (25% of allocated memory)
swap=2GB

# Enable localhost forwarding for Docker port access
localhostForwarding=true

# Kernel optimizations for better performance
kernelCommandLine=cgroup_no_v1=all systemd.unified_cgroup_hierarchy=1

# Disable page reporting for better performance
pageReporting=false

# Set VM idle timeout to 60 seconds
vmIdleTimeout=60000
```

#### For Mid-Range Systems (16GB RAM / 6 cores):
```ini
[wsl2]
# Set memory to 6GB (37% of total RAM)
memory=6GB

# Use 4 CPU cores (66% of available cores)
processors=4

# Set swap to 1GB
swap=1GB

localhostForwarding=true
kernelCommandLine=cgroup_no_v1=all systemd.unified_cgroup_hierarchy=1
pageReporting=false
vmIdleTimeout=60000
```

#### For Budget Systems (8GB RAM / 4 cores):
```ini
[wsl2]
# Set memory to 4GB (50% of total RAM)
memory=4GB

# Use 2 CPU cores (50% of available cores)
processors=2

# Set swap to 1GB
swap=1GB

localhostForwarding=true
kernelCommandLine=cgroup_no_v1=all systemd.unified_cgroup_hierarchy=1
pageReporting=false
vmIdleTimeout=60000
```

#### For Ultra High-End Systems (64GB+ RAM / 12+ cores):
```ini
[wsl2]
# Set memory to 16GB (25% of total RAM)
memory=16GB

# Use 6-8 CPU cores (50% of available cores)
processors=6

# Set swap to 4GB (25% of allocated memory)
swap=4GB

localhostForwarding=true
kernelCommandLine=cgroup_no_v1=all systemd.unified_cgroup_hierarchy=1
pageReporting=false
vmIdleTimeout=60000
```

### 3. Apply WSL2 Configuration

```powershell
# In PowerShell (as Administrator)
wsl --shutdown

# Wait 10 seconds
Start-Sleep 10

# Restart Docker Desktop
```

## Windows 11 Specific Optimizations

### File Sharing Optimization
```
Settings → Resources → File Sharing:
☑ Use gRPC FUSE for file sharing
☑ Enable VirtioFS (if available)
```

### Windows Defender Exclusions
Add these paths to Windows Defender exclusions:
```
C:\Users\[Username]\.docker\
C:\ProgramData\Docker\
\\wsl$\docker-desktop-data\
\\wsl$\docker-desktop\
```

### Performance Monitoring
- **Task Manager**: Look for "Vmmem" process (WSL2 usage)
- **Resource Monitor**: Monitor Docker Desktop CPU/Memory
- **Windows Performance Toolkit**: For advanced diagnostics

---

# macOS Best Practices

## System Requirements & Recommendations

### Minimum Requirements
- **RAM**: 8GB (16GB+ recommended)
- **CPU**: Intel or Apple Silicon
- **Storage**: 20GB free space for Docker
- **macOS**: 12.0 or later

### Optimal Hardware Configuration

#### By RAM & CPU Configuration
- **32GB RAM / 8+ cores**: Use 8GB for Docker (4-6 cores), 24GB for macOS
- **16GB RAM / 6+ cores**: Use 6GB for Docker (4 cores), 10GB for macOS
- **8GB RAM / 4 cores**: Use 4GB for Docker (2 cores), 4GB for macOS
- **64GB+ RAM / 12+ cores**: Use 16GB for Docker (6-8 cores), 48GB+ for macOS

## Docker Desktop Configuration

### 1. Resource Settings

#### For High-End Systems (32GB RAM / 8+ cores):
```
Docker Desktop → Settings → Resources:

Memory: 8GB
CPUs: 4-6 cores
Swap: 2GB
Disk image size: 64GB
```

#### For Mid-Range Systems (16GB RAM / 6 cores):
```
Docker Desktop → Settings → Resources:

Memory: 6GB
CPUs: 4 cores
Swap: 1GB
Disk image size: 32GB
```

#### For Budget Systems (8GB RAM / 4 cores):
```
Docker Desktop → Settings → Resources:

Memory: 4GB
CPUs: 2 cores
Swap: 1GB
Disk image size: 20GB
```

#### For Ultra High-End Systems (64GB+ RAM / 12+ cores):
```
Docker Desktop → Settings → Resources:

Memory: 16GB
CPUs: 6-8 cores
Swap: 4GB
Disk image size: 128GB
```

### 2. File Sharing Optimization
```
Settings → Resources → File Sharing:
☑ Use gRPC FUSE for file sharing
☑ Enable VirtioFS
☑ Use Rosetta for x86_64/amd64 emulation (Apple Silicon only)
```

## Apple Silicon (M1/M2/M3) Specific Settings

### Platform Architecture
```yaml
# In docker-compose.yml, specify platform for compatibility
services:
  app:
    platform: linux/amd64  # For x86_64 images
    # or
    platform: linux/arm64  # For native ARM images
```

### Performance Optimization
```
Docker Desktop Settings:
☑ Use Rosetta for x86_64/amd64 emulation on Apple Silicon
☑ Enable VirtioFS accelerated directory sharing
```

## macOS Specific Monitoring

### Activity Monitor
- Monitor "Docker Desktop" process
- Check memory pressure
- Watch CPU usage patterns

### Command Line Monitoring
```bash
# Check Docker resource usage
docker stats --no-stream

# Monitor system resources
top -pid $(pgrep Docker)

# Check disk usage
docker system df
```

---

# Ubuntu 24.04 Best Practices

## System Requirements & Recommendations

### Minimum Requirements
- **RAM**: 8GB (16GB+ recommended)
- **CPU**: 4 cores minimum
- **Storage**: 20GB free space for Docker
- **Ubuntu**: 24.04 LTS
- **Kernel**: 5.15 or later

## Docker Engine Installation (Recommended)

### 1. Install Docker Engine (Not Docker Desktop)
```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Docker Daemon Configuration

Create `/etc/docker/daemon.json`:
```json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-address-pools": [
    {
      "base": "172.17.0.0/16",
      "size": 24
    }
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "features": {
    "buildkit": true
  }
}
```

### 3. System Resource Limits

#### For High-End Systems (32GB RAM / 8+ cores):
Edit `/etc/systemd/system/docker.service.d/override.conf`:
```ini
[Service]
# Memory limit for Docker daemon
MemoryLimit=8G

# CPU limit (400% = 4 cores)
CPUQuota=400%

# Restart policy
Restart=always
RestartSec=10
```

#### For Mid-Range Systems (16GB RAM / 6 cores):
```ini
[Service]
MemoryLimit=6G
CPUQuota=400%  # 4 cores
Restart=always
RestartSec=10
```

#### For Budget Systems (8GB RAM / 4 cores):
```ini
[Service]
MemoryLimit=4G
CPUQuota=200%  # 2 cores
Restart=always
RestartSec=10
```

#### For Ultra High-End Systems (64GB+ RAM / 12+ cores):
```ini
[Service]
MemoryLimit=16G
CPUQuota=600%  # 6 cores
Restart=always
RestartSec=10
```

## Ubuntu Specific Optimizations

### 1. Systemd Service Management
```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Restart Docker with new settings
sudo systemctl restart docker

# Enable Docker auto-start
sudo systemctl enable docker

# Check Docker status
sudo systemctl status docker
```

### 2. Firewall Configuration (UFW)
```bash
# Allow Docker subnet
sudo ufw allow from 172.17.0.0/16

# Allow specific Docker ports if needed
sudo ufw allow 2376/tcp  # Docker daemon
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

### 3. Performance Tuning
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
echo "fs.file-max=2097152" | sudo tee -a /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

## Ubuntu Monitoring & Diagnostics

### System Monitoring
```bash
# Monitor Docker daemon
sudo journalctl -fu docker

# Check system resources
htop

# Monitor container resources
docker stats --no-stream

# Check disk usage
df -h
docker system df
```

---

# Universal Best Practices

## Container Resource Management

### Setting Container Limits in docker-compose.yml

```yaml
services:
  app:
    build: .
    deploy:
      resources:
        limits:
          cpus: '1.0'      # Max 1 CPU core
          memory: 1GB      # Max 1GB RAM
        reservations:
          cpus: '0.5'      # Reserve 0.5 CPU
          memory: 512MB    # Reserve 512MB RAM
```

### Production vs Development Configuration

#### Development (with hot-reload):
```yaml
command: ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0"]
# Expected memory: ~900MB-1GB per container
```

#### Production (optimized):
```yaml
command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--workers", "1"]
# Expected memory: ~600-800MB per container
```

## Maintenance & Cleanup

### Daily Maintenance
```bash
# Check container status
docker ps

# Monitor resource usage
docker stats --no-stream
```

### Weekly Maintenance
```bash
# Clean up unused resources
docker system prune -f

# Clean up unused volumes (be careful!)
docker volume prune -f

# Clean up build cache
docker builder prune -f

# Remove unused images
docker image prune -a -f
```

### Monthly Deep Clean
```bash
# Stop all containers
docker stop $(docker ps -q)

# Remove all stopped containers
docker container prune -f

# Remove all unused images
docker image prune -a -f

# Remove all unused volumes
docker volume prune -f

# Remove all unused networks
docker network prune -f

# Check recovered space
docker system df
```

## Resource Allocation Guidelines

### Memory Allocation by System Configuration

| System Configuration | Docker Memory | Docker CPUs | OS Reserve | Use Case |
|---------------------|---------------|-------------|------------|----------|
| **Budget**: 8GB RAM / 4 cores | 4GB | 2 cores | 4GB / 2 cores | Light development |
| **Mid-Range**: 16GB RAM / 6 cores | 6GB | 4 cores | 10GB / 2 cores | Standard development |
| **High-End**: 32GB RAM / 8 cores | 8GB | 4-6 cores | 24GB / 2-4 cores | Full-stack development |
| **Ultra**: 64GB+ RAM / 12+ cores | 16GB | 6-8 cores | 48GB+ / 4+ cores | Enterprise/Heavy workloads |

### CPU Allocation Guidelines by Architecture

| CPU Architecture | Total Cores/Threads | Docker Allocation | Performance Profile |
|------------------|-------------------|------------------|-------------------|
| **4C/4T** (Budget) | 4 cores | 2 cores (50%) | Basic containers only |
| **4C/8T** (Mainstream) | 4 cores / 8 threads | 2-3 cores (50-75%) | Light to medium workloads |
| **6C/6T** (Mid-range) | 6 cores | 4 cores (66%) | Multi-container development |
| **6C/12T** (High-performance) | 6 cores / 12 threads | 4 cores (66%) | Full development stack |
| **8C/8T** (High-end) | 8 cores | 4-6 cores (50-75%) | Heavy development workloads |
| **8C/16T** (Enthusiast) | 8 cores / 16 threads | 4-6 cores (50-75%) | Professional development |
| **12C/24T+** (Workstation) | 12+ cores / 24+ threads | 6-8 cores (50-66%) | Enterprise/CI/CD pipelines |

### Container Scaling Guidelines

| System Tier | Max Containers | Container Memory | Worker Processes |
|-------------|---------------|------------------|------------------|
| **Budget** | 3-5 containers | 512MB-1GB each | 1 worker per app |
| **Mid-Range** | 5-10 containers | 1GB-2GB each | 1-2 workers per app |
| **High-End** | 10-20 containers | 2GB-4GB each | 2-4 workers per app |
| **Ultra** | 20+ containers | 4GB+ each | 4+ workers per app |

## Common Troubleshooting

### Performance Issues
1. **High Memory Usage**: Check container limits and cleanup unused resources
2. **Slow Build Times**: Enable BuildKit and optimize Dockerfile layers  
3. **Network Connectivity**: Check firewall settings and port conflicts
4. **Disk Space**: Regular cleanup and monitoring of Docker disk usage

### Platform-Specific Issues

#### Windows 11
- WSL2 not starting: Check Windows features and restart
- Port conflicts: Ensure `localhostForwarding=true` in `.wslconfig`
- Performance: Monitor "Vmmem" process in Task Manager

#### macOS
- Rosetta compatibility: Use correct platform architecture
- File sharing slow: Enable VirtioFS
- Memory pressure: Adjust Docker Desktop resource limits

#### Ubuntu 24.04
- Permission denied: Add user to docker group
- Service not starting: Check systemctl status and logs
- Network issues: Configure UFW firewall rules

## Security Best Practices

### Container Security
```yaml
# Use non-root user in containers
USER 1001:1001

# Limit capabilities
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
```

### Network Security
```yaml
# Use custom networks
networks:
  app_network:
    driver: bridge
    internal: true
```

### Secret Management
```bash
# Use Docker secrets (not environment variables)
docker secret create db_password password.txt
```

---

## Platform Comparison Summary

| Feature | Windows 11 | macOS | Ubuntu 24.04 |
|---------|------------|-------|---------------|
| **Backend** | WSL2 | HyperKit/VirtioFS | Native |
| **Performance** | Very Good | Excellent | Excellent |
| **Resource Control** | `.wslconfig` | Docker Desktop | systemd limits |
| **File Sharing** | gRPC FUSE | VirtioFS | Native bind mounts |
| **Monitoring** | Task Manager | Activity Monitor | htop/systemctl |
| **Best For** | Development | Development | Production |

---

*This guide covers Docker optimization for Windows 11, macOS, and Ubuntu 24.04 LTS. Update configurations based on your specific hardware and requirements.*