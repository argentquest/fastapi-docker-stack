# VirtualBox Installation and VM Setup Guide

## Introduction

This guide provides detailed instructions for installing Oracle VirtualBox on Windows 11 and macOS. It also covers how to download the Ubuntu 24.04 LTS Server ISO and create a new virtual machine (VM) with a specific configuration.

## Installation on Windows 11

### 1. Download VirtualBox and Extension Pack

*   Go to the official VirtualBox download page: [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)
*   Click on the "Windows hosts" link to download the VirtualBox installer.
*   On the same page, download the "VirtualBox Extension Pack".

### 2. Install VirtualBox

*   Run the downloaded VirtualBox installer.
*   Follow the on-screen instructions, accepting the default settings.
*   If prompted about network interfaces being reset, click "Yes" to continue.
*   Once the installation is complete, click "Finish".

### 3. Install the VirtualBox Extension Pack

*   Open VirtualBox.
*   Go to `File > Tools > Extension Pack Manager`.
*   Click "Install" and select the downloaded Extension Pack file (`.vbox-extpack`).
*   Follow the on-screen prompts to complete the installation.

## Installation on macOS

### 1. Download VirtualBox and Extension Pack

*   Go to the official VirtualBox download page: [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)
*   Click on the "macOS / Intel hosts" or "Developer preview for macOS / Arm64 hosts" link, depending on your Mac's processor.
*   On the same page, download the "VirtualBox Extension Pack".

### 2. Install VirtualBox

*   Open the downloaded `.dmg` file and double-click the `VirtualBox.pkg` installer.
*   Follow the on-screen instructions to complete the installation.

### 3. Handle Security Prompts

*   During the installation, you may be prompted to allow the installation of a kernel extension from "Oracle America, Inc.".
*   Go to `System Preferences > Security & Privacy > General`.
*   Click the "Allow" button.
*   If the "Allow" button is not available, you may need to restart your Mac in Recovery Mode and use the `spctl kext-consent add VB5E2TV963` command in the terminal to grant permission.

### 4. Install the VirtualBox Extension Pack

*   Open VirtualBox.
*   Go to `File > Tools > Extension Pack Manager`.
*   Click "Install" and select the downloaded Extension Pack file (`.vbox-extpack`).
*   Follow the on-screen prompts to complete the installation.

## Downloading the Ubuntu 24.04 LTS Server ISO

*   Go to the official Ubuntu Server download page: [https://ubuntu.com/download/server](https://ubuntu.com/download/server)
*   Click on the "Download Ubuntu Server 24.04 LTS" button.
*   The ISO file will start downloading.

## Creating a New Virtual Machine

### 1. Create a New VM

*   Open VirtualBox and click the "New" button.
*   In the "Name and Operating System" section, give your VM a name (e.g., "Ubuntu Server") and select "Linux" as the type and "Ubuntu (64-bit)" as the version.

### 2. Configure Memory and CPU

*   In the "Memory size" section, set the memory to `8192` MB (8 GB).
*   In the "Processor(s)" section, set the number of CPUs to `1`.

### 3. Create a Virtual Hard Disk

*   In the "Hard disk" section, select "Create a virtual hard disk now" and click "Create".
*   Choose "VDI (VirtualBox Disk Image)" as the hard disk file type.
*   Select "Dynamically allocated".
*   Set the size of the virtual hard disk to `100` GB.
*   Click "Create" to create the virtual hard disk.

### 4. Configure Network Settings

*   Select the newly created VM in the VirtualBox Manager and click "Settings".
*   Go to the "Network" section.
*   In the "Adapter 1" tab, select "Enable Network Adapter".
*   In the "Attached to" dropdown menu, select "Bridged Adapter".
*   From the "Name" dropdown, select your host's active network interface (e.g., your Wi-Fi or Ethernet adapter).
*   Click "OK" to save the settings.

### 5. Install Ubuntu Server

*   Select the VM and click "Start".
*   In the "Select start-up disk" window, click the folder icon and select the downloaded Ubuntu 24.04 LTS Server ISO file.
*   Click "Start" to begin the installation process.
*   Follow the on-screen instructions to install Ubuntu Server on your new VM.
*   **Set Up Your User Account:** During the installation, you will be prompted to create a user account. We suggest using a simple username like `devadmin` or `ubuntu`. This user will be granted `sudo` privileges, which is the recommended way to perform administrative tasks. You will not be prompted to set a password for the `root` user directly.

> **Note on Root Access:** For security reasons, Ubuntu disables the root account by default. To run commands with administrative privileges, you should use the `sudo` command before the command you want to run (e.g., `sudo apt update`). If you still wish to enable the root account with a password, you can do so *after* the installation is complete by running the following command in the VM's terminal: `sudo passwd root`

## Connecting to the VM with SSH

### 1. Get the VM's IP Address

*   Once the Ubuntu Server installation is complete, log in to the VM.
*   Open a terminal and type the following command to get the VM's IP address:
    ```bash
    ip addr show
    ```
*   Look for the IP address associated with the `eth0` or `enp0s3` interface.

### 2. Connect with SSH

#### Windows (using Putty)

*   Open Putty on your Windows machine.
*   In the "Host Name (or IP address)" field, enter the IP address of your VM.
*   Ensure the "Port" is set to `22` and the "Connection type" is set to "SSH".
*   Click "Open" to start the SSH session.

#### macOS (using the Terminal)

*   Open the Terminal application on your macOS machine.
*   Use the following command to connect to your VM, replacing `username` with the username you created during the Ubuntu installation and `your_vm_ip_address` with the IP address of your VM:
    ```bash
    ssh username@your_vm_ip_address
    ```

### 3. Log In

*   You will be prompted for your password.
*   Enter the password you created during the Ubuntu Server installation.
*   You should now be logged in to your VM via SSH.

## Post-Installation: Setting Up the Development Environment

Once your Ubuntu Server VM is running, you can proceed to set up the Argentquest Development Suite.

### 1. Prepare the VM for Docker

After SSH connection is established, update the system and install prerequisites:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git nano htop unzip python3 python3-pip python3-venv

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for Docker permissions to take effect
exit
```

### 2. Clone and Deploy the Development Suite

```bash
# Clone the repository
git clone <your-repo-url> argentquest-suite
cd argentquest-suite

# Set up environment configuration
cp .env.template .env
nano .env  # Edit with your API keys and settings

# Start all 22 containers
docker-compose up -d

# Wait for initialization
sleep 180

# Set up NPM proxy hosts
python3 scripts/npm-simple-setup.py

# Validate deployment
python3 health-check.py
```

### 3. VM Resource Recommendations

For optimal performance with the 22-container stack:

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **RAM** | 8GB | 16GB | 22 containers require significant memory |
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
