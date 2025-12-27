# VirtualBox Installation and Kubuntu VM Setup Guide

## Introduction

This guide provides detailed instructions for installing Oracle VirtualBox on Windows 11 and Linux hosts, creating a **Kubuntu 24.04** VM (manual or automated), and setting up the **Argentquest Development Suite**.

## 1. Install VirtualBox

### Linux Host (Ubuntu/Debian)
1.  **Update and Install Dependencies**:
    ```bash
    sudo apt update
    sudo apt install -y software-properties-common wget
    ```
2.  **Add Oracle Repository and Key**:
    ```bash
    wget -O- https://www.virtualbox.org/download/oracle_vbox_2016.asc | sudo gpg --dearmor --yes --output /usr/share/keyrings/oracle-virtualbox-2016.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/oracle-virtualbox-2016.gpg] https://download.virtualbox.org/virtualbox/debian $(lsb_release -cs) contrib" | sudo tee /etc/apt/sources.list.d/virtualbox.list
    ```
3.  **Install VirtualBox**:
    ```bash
    sudo apt update
    sudo apt install -y virtualbox-7.0
    ```

### Windows 11 Host
1.  Download the **Windows hosts** installer from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads).
2.  Run the installer (`VirtualBox-x.x.x-Win.exe`).
3.  Follow the setup wizard.
4.  **Extension Pack**: Download "All supported platforms" from the same page and install via **File > Tools > Extension Pack Manager**.

## 2. Prerequisites
-   **Kubuntu 24.04 LTS ISO**: Download from [kubuntu.org/getkubuntu/](https://kubuntu.org/getkubuntu/).

## 3. Create the Virtual Machine

### Option A: Manual Creation (GUI)
1.  Open VirtualBox and click **New**.
2.  **Name**: `Kubuntu 24.04` (Type: Linux, Version: Ubuntu 64-bit).
3.  **Hardware**:
    *   **RAM**: At least **8192 MB** (8 GB).
    *   **CPU**: At least **2 CPUs** (4 recommended).
4.  **Hard Disk**: **200 GB** (VDI, Dynamically Allocated).
5.  **Network** (Crucial Step):
    *   Go to **Settings > Network**.
    *   Change "Attached to" to **Bridged Adapter**.
    *   Select your active host interface (Ethernet/Wi-Fi).
6.  Click **Finish**.

### Option B: Automated Creation (Command Line)

#### Linux Host (Bash)
```bash
ISO_PATH="/path/to/kubuntu-24.04-desktop-amd64.iso"
VM_NAME="Kubuntu 24.04"

# Create VM
VBoxManage createvm --name "$VM_NAME" --ostype "Ubuntu_64" --register --basefolder "$HOME/VirtualBox VMs"

# Configure Hardware (8GB RAM, 2 CPUs, 128MB VRAM)
VBoxManage modifyvm "$VM_NAME" --memory 8192 --cpus 2 --vram 128 --graphicscontroller vmsvga --accelerate3d on

# Create Hard Disk (200GB)
VBoxManage createhd --filename "$HOME/VirtualBox VMs/$VM_NAME/$VM_NAME.vdi" --size 204800 --format VDI

# Attach Storage
VBoxManage storagectl "$VM_NAME" --name "SATA Controller" --add sata --controller IntelAHCI
VBoxManage storageattach "$VM_NAME" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "$HOME/VirtualBox VMs/$VM_NAME/$VM_NAME.vdi"

VBoxManage storagectl "$VM_NAME" --name "IDE Controller" --add ide
VBoxManage storageattach "$VM_NAME" --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "$ISO_PATH"

echo "VM created. REMEMBER: Manually set Network to 'Bridged Adapter' in Settings > Network."
```

#### Windows 11 Host (PowerShell)
Run as Administrator:
```powershell
$VmName = "Kubuntu 24.04"
$IsoPath = "C:\Users\YourUser\Downloads\kubuntu-24.04-desktop-amd64.iso"
$VBoxManage = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

& $VBoxManage createvm --name $VmName --ostype "Ubuntu_64" --register
& $VBoxManage modifyvm $VmName --memory 8192 --cpus 2 --vram 128 --graphicscontroller vmsvga --accelerate3d on

$VmFolder = "$env:USERPROFILE\VirtualBox VMs\$VmName"
& $VBoxManage createhd --filename "$VmFolder\$VmName.vdi" --size 204800 --format VDI

& $VBoxManage storagectl $VmName --name "SATA Controller" --add sata --controller IntelAHCI
& $VBoxManage storageattach $VmName --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium "$VmFolder\$VmName.vdi"

& $VBoxManage storagectl $VmName --name "IDE Controller" --add ide
& $VBoxManage storageattach $VmName --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium $IsoPath

Write-Host "VM created. REMEMBER: Manually set Network to 'Bridged Adapter' in Settings > Network."
```

## 4. Install Kubuntu
1.  Start the VM and select **Try or Install Kubuntu**.
2.  Choose **Install Kubuntu**, select Language/Keyboard.
3.  Choose **Normal Installation** + **Third-party software**.
4.  **Erase disk and install Kubuntu**.
5.  **Create User (Project Standard)**:
    *   **Your name**: Argentquest Dev
    *   **Username**: `argentquest`  <-- IMPORTANT
    *   **Password**: `argentquest123` <-- IMPORTANT
    *   **Computer name**: `argentquest-vm`
6.  Reboot when finished.

## 5. Post-Installation: Automated Environment Setup

This step converts your fresh Kubuntu installation into a powerful development workstation.

### 📦 Applications Added to Kubuntu 24.04
The automated script below will install and configure the following tailored software stack:

1.  **Docker Engine & Compose:** The core containerization platform for running the 22-service suite.
2.  **Python 3.13:** The latest modern Python, configured with `venv` and `dev` tools for backend development.
3.  **Visual Studio Code:** The industry-standard IDE, installed with official Microsoft repositories.
4.  **Git:** Distributed version control for managing the project codebase.
5.  **System Utilities:** Essential tools like `curl`, `wget`, `htop`, and `unzip`.

### Optional Power Tools (Included in script as comments)
*   **Postman:** Essential for testing expected payloads against the FastAPI endpoints.
*   **DBeaver:** A powerful universal database client to manage PostgreSQL and MongoDB visually.
*   **LazyDocker:** An amazing terminal UI for managing containers without leaving the command line.

### Automated Setup Script
Instead of running dozens of manual commands, use this script to install everything at once:

1.  Open Terminal (`Ctrl+Alt+T`) in the VM.
2.  Create `setup_env.sh`:
    ```bash
    nano setup_env.sh
    ```
3.  Paste this content:
    ```bash
    #!/bin/bash
    set -e
    
    # --- Standard Sudo Configuration ---
    echo ">>> Configuring standard sudo rights..."
    # Ensure current user has passwordless sudo (Standard for Dev VMs)
    echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/90-argentquest-nopasswd > /dev/null
    sudo chmod 440 /etc/sudoers.d/90-argentquest-nopasswd
    
    echo ">>> Updating system..."
    sudo apt update && sudo apt upgrade -y
    echo ">>> Installing Dependencies (curl, git, wget)..."
    sudo apt install -y software-properties-common curl git wget apt-transport-https ca-certificates gnupg htop unzip
    echo ">>> Installing Python 3.13..."
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt update
    sudo apt install -y python3.13 python3.13-venv python3.13-dev
    echo ">>> Installing Docker..."
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
    echo ">>> Installing VS Code..."
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
    sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
    rm -f packages.microsoft.gpg
    sudo apt update
    sudo apt install -y code
    
    echo ">>> Installing Power Tools (Postman, DBeaver, LazyDocker)..."
    
    # 1. Postman (API Testing)
    echo ">>> Installing Postman..."
    sudo snap install postman

    # 2. DBeaver (Universal Database Client)
    echo ">>> Installing DBeaver..."
    sudo snap install dbeaver-ce

    # 3. LazyDocker (Terminal UI for Docker)
    echo ">>> Installing LazyDocker..."
    curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash

    echo ">>> Done! Software stack installed. Please REBOOT now."
    ```
4.  Run it:
    ```bash
    chmod +x setup_env.sh
    ./setup_env.sh
    ```

### 2. Clone and Deploy the Development Suite

```bash
# Clone the repository
git clone <your-repo-url> argentquest-suite
cd argentquest-suite

# Set up environment configuration
cp .env.template .env
nano .env  # Edit with your API keys and settings

# 🚀 DEPLOYMENT (The Standard Way)
# We use a 2-step process to ensure a clean, reliable state every time.

# 1. Nuclear Reset (Cleans Docker, Cache, & Old Data)
chmod +x reset_all.sh setup.sh
./reset_all.sh

# 2. Automated Setup (Builds, Launches & Configures)
./setup.sh
```

**Note:** The `setup.sh` script automatically handles:
*   Building images with BuildKit
*   Launching all 21 containers
*   Waiting for healthy services
*   Configuring the Nginx Proxy Manager
*   Populating the Heimdall Dashboard

### 🔎 Understanding the Orchestration Scripts

Since we rely on these two scripts, here is exactly what they do under the hood:

#### `reset_all.sh` (The "Nuclear" Option)
Think of this as a "Factory Reset" for your Docker environment. It fixes 99% of issues by clearing out corrupted state.
1.  **Stops & Removes** all project containers.
2.  **Prunes** all Docker system data (images, volumes, networks) to free disk space.
3.  **Cleans** project artifacts (`.venv`, `__pycache__`, old logs).
4.  **Reclaims** disk space (often freeing 5-10GB).
5.  **Ensures** a completely clean slate for the next build.

#### `setup.sh` (The "One-Click" Deploy)
This is the intelligent installer that replaces manual configuration.
1.  **Environment Check**: Verifies Sudo rights, Docker status, and Port availability.
2.  **Config Generation**: Creates default `.env` files if they are missing.
3.  **Sequential Build**: Builds the core `app-dev` image *first* to prevent Docker engine hangs.
4.  **Launch**: Starts all 21 containers with `docker compose up`.
5.  **Smart Wait**: Polls the Nginx Proxy Manager API until it is healthy (instead of a fixed sleep timer).
6.  **Auto-Configuration**:
    *   Configures NPM proxy hosts via API.
    *   Sets up Heimdall dashboard links.
    *   Runs final system health checks.

#### 🧹 Ephemeral Setup Containers
You might notice containers like `aq-devsuite-npm-setup` and `aq-devsuite-beszel-setup` in your list.
*   **Purpose**: These are temporary "worker" containers.
*   **Lifecycle**: They run *once* to perform API configurations (like setting up proxy hosts) and then **automatically exit**.
*   **Cleanup**: One the stack is healthy, these containers are stopped and no longer consume resources. They are kept only for logs/debugging.

### 2. Clone and Deploy the Development Suite

For optimal performance with the **20-container stack**:

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 8GB | 16GB | 20 containers require significant memory |
| **CPU Cores** | 1 | 4 | Multiple services benefit from parallel processing |
| **Storage** | 100GB | 200GB | Docker images, volumes, and logs |
| **Network** | Bridged | Bridged | Required for external access to services |

### 4. Accessing Services from Host Machine

Once deployed, you can access services from your host machine:

**Update your host machine's hosts file:**

**Windows (Run as Administrator):**
```cmd
notepad C:\Windows\System32\drivers\etc\hosts
```

**Linux/macOS:**
```bash
sudo nano /etc/hosts
```

**Add these lines (replace VM_IP with your VM's IP address):**
```
# Argentquest Development Suite in VM
VM_IP    pocmaster.argentquest.com
VM_IP    api.pocmaster.argentquest.com
VM_IP    api-dev.pocmaster.argentquest.com
VM_IP    pgadmin.pocmaster.argentquest.com
VM_IP    portainer.pocmaster.argentquest.com
VM_IP    heimdall.pocmaster.argentquest.com
VM_IP    code.pocmaster.argentquest.com
```

### 5. Environment Configuration in VM

The VM deployment uses the same environment file structure:

- **`.env`**: Main configuration for local VM development
- **`.env.dev`**: Development container settings (debug mode)
- **`.env.prod`**: Production container settings (performance mode)

**Database connections in VM:**
- **PostgreSQL**: `postgres:5432` (internal) / `VM_IP:5432` (external)
- **MongoDB**: `mongodb:27017` (internal) / `VM_IP:27017` (external)
- **pgAdmin**: `http://VM_IP:5050` or `http://pgadmin.pocmaster.argentquest.com`

### 6. VM-Specific Considerations

**Firewall Configuration:**
```bash
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 81/tcp    # NPM Admin
sudo ufw allow 5050/tcp  # pgAdmin direct access
sudo ufw --force enable
```

**Performance Monitoring:**
- **System Monitor**: `http://pocmaster.argentquest.com` (after NPM setup)
- **Beszel Monitoring**: `http://beszel.pocmaster.argentquest.com`
- **Container Stats**: `docker-compose ps` and `docker stats`

**VM Management Tips:**
- Use VM snapshots before major changes
- Monitor VM resource usage with `htop` and `docker stats`
- Regular backups of VM disk and configuration files
- Consider VM pausing/resuming for resource management

## Development Workflow in VM

### Hot-Reload Development

Even when running in a VM, the hot-reload functionality is preserved:

1. **Code Editing**: Edit code on your host machine using VS Code
2. **File Sync**: Use shared folders or Git to sync changes to VM
3. **Auto-Reload**: The `app-dev` container automatically detects changes
4. **Testing**: Access development API at `http://api-dev.pocmaster.argentquest.com`

### Shared Folder Setup (Optional)

For seamless development, set up VirtualBox shared folders:

1. **VM Settings** → **Shared Folders** → **Add Folder**
2. **Folder Path**: Your local project directory
3. **Folder Name**: `argentquest-suite`
4. **Auto-mount**: ✅ Enable
5. **Make Permanent**: ✅ Enable

**Inside the VM:**
```bash
# Install Guest Additions (if not already installed)
sudo apt install virtualbox-guest-additions-iso

# Mount shared folder
sudo mkdir -p /mnt/shared
sudo mount -t vboxsf argentquest-suite /mnt/shared

# Create symlink for easier access
ln -s /mnt/shared ~/argentquest-suite
```

### Alternative: Git-Based Workflow

For better version control and isolation:

1. **Host Machine**: Develop and commit changes
2. **VM**: Pull latest changes with `git pull`
3. **Docker**: Hot-reload automatically picks up changes
4. **Testing**: Validate in VM environment before pushing

### VM Backup and Snapshots

**Create Snapshots:**
- Before major changes
- After successful deployments  
- Before system updates

**Snapshot Strategy:**
1. **Clean State**: After initial setup
2. **Working State**: After successful deployment
3. **Pre-Update**: Before system or Docker updates

## Quick Reference: VM Commands

### Essential VM Management

```bash
# Check VM resource usage
htop
docker stats

# Monitor disk space
df -h
docker system df

# Check container health
docker-compose ps
python3 health-check.py

# View service logs
docker-compose logs -f app-dev
docker-compose logs -f postgres

# Database validation
./validate-database-setup.sh

# Restart services
docker-compose restart app-dev app-prod
docker-compose down && docker-compose up -d
```

### VM Network Troubleshooting

```bash
# Check VM IP address
ip addr show

# Test Docker network connectivity
docker exec aq-devsuite-app-dev ping postgres
docker exec aq-devsuite-app-dev ping mongodb

# Check port accessibility from host
telnet VM_IP 80   # NPM
telnet VM_IP 5050 # pgAdmin
```

### Environment File Management in VM

```bash
# View environment configurations
cat .env     # Main configuration
cat .env.dev # Development settings  
cat .env.prod # Production settings

# Update environment variables
nano .env.dev
docker-compose restart app-dev

# Check environment variables in containers
docker exec aq-devsuite-app-dev env | grep DATABASE_URL
docker exec aq-devsuite-app-prod env | grep DATABASE_URL
```

## References

### General

*   **Oracle VirtualBox Official Website:** [https://www.virtualbox.org/](https://www.virtualbox.org/)
*   **Ubuntu Official Website:** [https://ubuntu.com/](https://ubuntu.com/)

### Video Guides

*   **Install VirtualBox on Windows 11:** [https://www.youtube.com/watch?v=S-p23428_yM](https://www.youtube.com/watch?v=S-p23428_yM)
*   **Install VirtualBox on macOS:** [https://www.youtube.com/watch?v=3-h3_4a2-js](https://www.youtube.com/watch?v=3-h3_4a2-js)
*   **Install Ubuntu Server 24.04 LTS:** [https://www.youtube.com/watch?v=...](https://www.youtube.com/watch?v=...)
*   **Connect to a VM with Putty:** [https://www.youtube.com/watch?v=...](https://www.youtube.com/watch?v=...)
*   **Connect to a VM with SSH on macOS:** [https://www.youtube.com/watch?v=...](https://www.youtube.com/watch?v=...)
