# Argentquest Development Suite

[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

**🚀 22-Container Self-Hosted Development Environment | 90% Cost Savings vs Cloud Services**

A comprehensive development stack with dual FastAPI environments, multiple databases (PostgreSQL+pgvector, MongoDB), management tools, development tools, and workflow automation - all containerized with simplified single-network architecture.

---

## ⭐ **For Contributors**

**New to the project?** Welcome! We'd love your help making this even better.

### 🚀 **Quick Start for Contributors**
```bash
# One-command setup - works on Windows, Mac, and Linux
git clone https://github.com/argentquest/fastapi-docker-stack.git
cd fastapi-docker-stack

# Windows users:
setup.bat

# Mac/Linux users:
chmod +x setup.sh && ./setup.sh

# Then visit: http://pocmaster.argentquest.com
```

### 🤝 **Ways to Contribute**
- 🐛 [Report bugs](../../issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D+)
- ✨ [Request features](../../issues/new?assignees=&labels=enhancement&template=feature_request.md&title=%5BFEATURE%5D+)
- 📖 [Improve docs](../../issues/new?assignees=&labels=documentation&template=documentation.md&title=%5BDOCS%5D+)
- 🔧 [Find good first issues](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

### 🎯 **Perfect for Learning**
- Docker & containerization
- Microservices architecture  
- FastAPI development
- Database management
- DevOps workflows

**Read our [Contributing Guide](CONTRIBUTING.md) | Check our [Roadmap](ROADMAP.md) | Follow our [Code of Conduct](CODE_OF_CONDUCT.md)**

---

## 📋 Table of Contents

- [For Contributors](#-for-contributors)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture) 
- [Service Directory](#-service-directory)
- [Development Guide](#-development-guide)
- [Credentials Reference](#-credentials-reference)
- [Troubleshooting](#-troubleshooting)
- [Advanced Configuration](#-advanced-configuration)
- [Community](#-community)

## 🎯 Project Goals

- **Cost Reduction**: 90% reduction in monthly operational costs
- **Self-Hosted Infrastructure**: Full control over deployment and data
- **Modern Architecture**: Containerized microservices with Docker
- **Open Source Stack**: Leverage open-source alternatives to Azure services
- **Performance**: Maintain or improve response times and throughput

## 🏗️ Architecture

### Argentquest Development Suite Architecture (22 Services)

```
                    INTERNET
                        │
                ┌───────▼───────┐
                │ Nginx Proxy   │ ← ports 80/443/81
                │ Manager (NPM) │
                └───────┬───────┘
                        │
              ┌─────────▼─────────┐
              │ aq-devsuite-network │ (Single Docker Bridge Network)
              │   172.18.0.0/16   │
              └─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
                │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │
        ┌───────┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴───────┐
        │                                                          │
    [Frontend]  [API]  [Data]  [Management]  [Development] [Monitoring]
        │        │      │         │            │              │
    Heimdall  FastAPI  PostgreSQL Portainer  VS Code         Beszel
              (x2)     MongoDB    pgAdmin    MCP Inspector    System Monitor
                       Redis      Mongo Expr n8n              Monitor API
                       MinIO      Redis Cmdr Jupyter
```

### Technology Stack Comparison

| Component | Current (Azure) | V2 (Docker) | Cost Savings |
|-----------|----------------|-------------| ------------|
| **Hosting** | Azure App Service | VPS + Docker (22 containers) | 95% |
| **Vector Search** | Azure AI Search | PostgreSQL + pgvector | 100% |
| **Document DB** | Azure Cosmos DB | MongoDB 7.0 | 100% |
| **LLM Provider** | Azure OpenAI | OpenRouter (GPT-5 Nano) | 95% |
| **Object Storage** | Azure Blob Storage | MinIO (S3-compatible) | 100% |
| **Relational DB** | Azure PostgreSQL | PostgreSQL 16 | 90% |
| **Caching** | Azure Redis | Redis 7.4 | 100% |
| **Reverse Proxy** | Azure CDN | Nginx with SSL | 100% |
| **Management** | Azure Portal | Portainer + Heimdall | 100% |
| **IDE** | VS Code Desktop | VS Code Server | 100% |

## 🚀 Quick Start

### Windows Users - Automated Startup Scripts

We provide PowerShell scripts that automatically check if Docker Desktop is running, start it if needed, and manage your containers:

```powershell
# Start environment (auto-starts Docker Desktop if needed)
.\start.ps1

# Check status of all services
.\status.ps1

# Restart all containers
.\restart.ps1

# Stop environment (with cleanup options)
.\stop.ps1

# Alternative: Use batch files if preferred
start.bat
```

### 🖥️ Local & Server Deployment Guide

These steps cover both local development and deployment on a fresh Ubuntu 24.04 LTS server.

#### 1. Initial Server Setup (Skip for Local Development)

If you are deploying to a remote server, follow these steps first.

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

#### 2. Clone and Setup Project
```bash
# Clone the repository
git clone <your-repo-url> argentquest-suite
cd argentquest-suite

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install requests python-dotenv
```

#### 3. Configure Environment
```bash
# Create environment file
cp .env.example .env
nano .env
```

**Update `.env` with your values:**
```env
# OpenRouter Configuration (REQUIRED)
OPENROUTER_API_KEY="your-openrouter-api-key-here"
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=openai/gpt-5-nano

# Database Configuration (Docker Network)
POSTGRES_USER=pocuser
POSTGRES_PASSWORD=pocpass
POSTGRES_DB=poc_db
DATABASE_URL=postgresql://pocuser:pocpass@postgres:5432/poc_db

MONGO_INITDB_ROOT_USERNAME=mongoadmin
MONGO_INITDB_ROOT_PASSWORD=mongopass123
MONGODB_URL=mongodb://mongoadmin:mongopass123@mongodb:27017/poc_mongo_db

# Storage and Caching
REDIS_URL=redis://redis:6379
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# Development Tools
VSCODE_PASSWORD=dev123
PGADMIN_DEFAULT_PASSWORD=admin
```

### 🔧 Environment File Configuration

The stack uses **three environment files** for different purposes:

#### **`.env` (Main Configuration)**
- **Purpose:** Local development and shared configuration
- **Database Targets:** Docker container names (`postgres:5432`, `mongodb:27017`)
- **Usage:** Local development apps, testing, and configuration base

#### **`.env.dev` (Development Container)**
- **Purpose:** Configuration for `app-dev` container
- **Features:** Debug logging, hot reload, relaxed security, single worker
- **Database Targets:** Same Docker containers (`postgres:5432`, `mongodb:27017`)

#### **`.env.prod` (Production Container)**
- **Purpose:** Configuration for `app-prod` container  
- **Features:** JSON logging, multiple workers, strict security, performance optimized
- **Database Targets:** Same Docker containers (`postgres:5432`, `mongodb:27017`)

#### **Key Benefits:**
- **Shared Database:** All environments connect to same PostgreSQL and MongoDB instances with test data
- **Environment Isolation:** Different logging, security, and performance settings per environment
- **Consistency:** All environments use Docker network names for reliable container communication
- **Flexibility:** Easy to customize each environment without affecting others

**Connection Summary:**
| Environment | File | Database Host | Purpose |
|-------------|------|---------------|---------|
| Local Development | `.env` | `postgres/mongodb` | Development apps |
| Dev Container | `.env.dev` | `postgres/mongodb` | Debug environment |
| Prod Container | `.env.prod` | `postgres/mongodb` | Production-like testing |
| External Tools | Host machine | `localhost:5432/27017` | pgAdmin, clients |

#### 4. Configure Domain Access

**REQUIRED: Update Your Hosts File**

baseThe stack uses `pocmaster.argentquest.com` domains. You must add these to your hosts file pointing to your server\'s IP address.

**Windows (Run as Administrator):**
```cmd
notepad C:\Windows\System32\drivers\etc\hosts
```

**Linux/macOS:**
```bash
sudo nano /etc/hosts
```

**Add these lines (replace SERVER_IP with `127.0.0.1` for local development or your server\'s IP):**
```
# Argentquest Development Suite
SERVER_IP    pocmaster.argentquest.com
SERVER_IP    api.pocmaster.argentquest.com
SERVER_IP    api-dev.pocmaster.argentquest.com
SERVER_IP    pgadmin.pocmaster.argentquest.com
SERVER_IP    mongo.pocmaster.argentquest.com
SERVER_IP    redis.pocmaster.argentquest.com
SERVER_IP    minio.pocmaster.argentquest.com
SERVER_IP    portainer.pocmaster.argentquest.com
SERVER_IP    heimdall.pocmaster.argentquest.com
SERVER_IP    code.pocmaster.argentquest.com
SERVER_IP    mcp.pocmaster.argentquest.com
SERVER_IP    n8n.pocmaster.argentquest.com
SERVER_IP    jupyter.pocmaster.argentquest.com
```

#### 5. Deploy the Full Stack
```bash
# Start all 22 containers
docker-compose up -d

# Wait for containers to initialize (2-3 minutes)
sleep 180

# Run automated NPM proxy host setup
python scripts/npm-simple-setup.py

# Verify deployment
python health-check.py
```

#### 6. Verify Complete Deployment
```bash
# Check all containers are running
docker ps --filter "name=aq-devsuite-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test health endpoint
curl -f http://localhost/health || echo "Setup NPM proxy hosts first"

# Access main dashboard
# http://pocmaster.argentquest.com (after hosts file or DNS setup)
```

#### 7. Firewall Configuration (Important!)
```bash
# Allow NPM ports through firewall
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS  
sudo ufw allow 81/tcp   # NPM Admin

# Optional: Allow direct access ports for development
sudo ufw allow 5050/tcp  # pgAdmin direct
sudo ufw allow 9443/tcp  # Portainer direct

# Enable firewall
sudo ufw --force enable
```

#### 8. First-Time Access
1. **NPM Admin:** http://localhost:81 (admin@example.com / changeme)
2. **Main Dashboard:** http://pocmaster.argentquest.com (after proxy setup)
3. **Change default passwords** in NPM Admin, pgAdmin, and other services

#### 9. Validation Checklist
- [ ] All 22 containers running (`docker ps`)
- [ ] NPM proxy hosts configured (12 hosts in NPM admin)
- [ ] Health check shows 100% healthy services
- [ ] Main dashboard accessible via domain
- [ ] API documentation loads at `/docs` endpoint
- [ ] Database connections working (test via admin UIs) 


**Estimated deployment time:** 15-20 minutes on a fresh Ubuntu 24 server

## 🏠 Using Custom Domains (Alternative to pocmaster.argentquest.com)

### If you want to use your own domain instead of `pocmaster.argentquest.com`:

> **IMPORTANT**: Using a custom domain requires changes to several files. This section outlines the necessary modifications. Failure to update these files will result in a non-functional deployment.

#### 1. Choose Your Domain
Examples:
- `mystack.local` (for local development only)
- `dev.mycompany.com` (for company internal use)
- `yourdomain.com` (for production with real DNS)

#### 2. Required Code Changes

**A. Update NPM automation script:**
```bash
nano scripts/npm-simple-setup.py
```
Find lines 100-104 and replace `pocmaster.argentquest.com` with your domain:
```python
# Example: Change from pocmaster.argentquest.com to mystack.local
("api.mystack.local", "aq-devsuite-app-prod", 8000),
("api-dev.mystack.local", "aq-devsuite-app-dev", 8000),
("n8n.mystack.local", "aq-devsuite-n8n", 5678),
("jupyter.mystack.local", "aq-devsuite-jupyter", 8888),
("mcp.mystack.local", "aq-devsuite-mcp-inspector", 5173),
```

**B. Update dashboard links:**
```bash
nano system-monitor/index.html
```
Replace ALL occurrences of `pocmaster.argentquest.com` with your domain (approximately 15-20 links)

**C. Update MCP Inspector allowed hosts:**
```bash
nano mcp-inspector/Dockerfile
```
Line 29: Add your domain to allowedHosts:
```javascript
allowedHosts: ["mcp.pocmaster.argentquest.com", "mcp.YOURDOMAIN.com", "localhost", "127.0.0.1"]
```

#### 3. Update Your Hosts File
**Windows (Administrator):** `notepad C:\Windows\System32\drivers\etc\hosts`
**Linux/macOS:** `sudo nano /etc/hosts`

Add your domain mappings:
```
# Replace SERVER_IP with your server\'s IP address
SERVER_IP    yourdomain.com
SERVER_IP    api.yourdomain.com
SERVER_IP    api-dev.yourdomain.com
SERVER_IP    pgadmin.yourdomain.com
SERVER_IP    mongo.yourdomain.com
SERVER_IP    redis.yourdomain.com
SERVER_IP    minio.yourdomain.com
SERVER_IP    portainer.yourdomain.com
SERVER_IP    heimdall.yourdomain.com
SERVER_IP    code.yourdomain.com
SERVER_IP    mcp.yourdomain.com
SERVER_IP    n8n.yourdomain.com
SERVER_IP    jupyter.yourdomain.com
```

#### 4. Rebuild and Deploy
```bash
# Rebuild MCP Inspector with new allowed hosts
docker-compose build mcp-inspector

# Restart deployment
docker-compose down && docker-compose up -d

# Run NPM setup with your new domains
python scripts/npm-simple-setup.py
```

**Estimated custom domain setup time:** 15-20 minutes (including code changes)

## 📊 Beszel Monitoring Setup

### Automatic Container Discovery Configuration:

#### 1. Access Beszel Dashboard
- **URL:** http://beszel.pocmaster.argentquest.com (or http://localhost:8090)
- **Login:** admin@example.com / changeme

#### 2. Add Your Server for Monitoring
1. Click **"Add System"** in Beszel dashboard
2. **Name:** Argentquest Development Suite
3. **Host:** aq-devsuite-beszel-agent (container name)
4. **Port:** 45876
5. **Generate SSH Key:** Click "Generate Key Pair" in Beszel UI
6. **Copy Public Key:** Save the generated public key

#### 3. Update Agent with Generated Key
```bash
# Edit docker-compose.yml
nano docker-compose.yml

# Replace the KEY environment variable with your generated public key:
environment:
  - PORT=45876
  - KEY=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIYourGeneratedKeyHere

# Restart the agent
docker-compose restart beszel-agent
```

#### 4. Enable Docker Monitoring
In Beszel dashboard:
1. Edit your system settings
2. Enable **"Docker Monitoring"**
3. Beszel will automatically discover all 22 containers
4. View real-time metrics for each container

#### 5. What You\'ll See
- **Host metrics:** CPU, RAM, disk, network usage
- **Container metrics:** Per-container resource usage for all 22 services
- **Historical data:** Resource usage over time
- **Alerts:** Configure thresholds for resource monitoring

**Benefits over basic system-monitor:**
- Historical metrics and trends
- Per-container resource breakdown
- Configurable alerts and notifications
- Professional monitoring interface
- Multi-server support (add more servers later)

### Prerequisites
- **Python 3.11** or higher
- **Docker** & **Docker Compose**
- **8GB RAM** minimum (16GB recommended)
- **20GB disk space** for containers and data
- **OpenRouter API key** with credits

## 📊 Service Directory

### Core Application Services

| Service | URL | Purpose | Status |
|---------|-----|---------|---------|
| **FastAPI Production** | http://api.pocmaster.argentquest.com | Main production API | ✅ Healthy |
| **FastAPI Development** | http://api-dev.pocmaster.argentquest.com | Development API with hot-reload | ✅ Healthy |
| **API Documentation** | http://api.pocmaster.argentquest.com/docs | Interactive Swagger UI | ✅ Healthy |

### Database Services

| Service | URL | Purpose | Status |
|---------|-----|---------|---------|
| **PostgreSQL** | localhost:5432 | Main database with pgvector | ✅ Healthy |
| **pgAdmin** | http://pgadmin.pocmaster.argentquest.com | PostgreSQL web management | ✅ Healthy |
| **MongoDB** | localhost:27017 | NoSQL document database | ✅ Healthy |
| **MongoDB Express** | http://mongo.pocmaster.argentquest.com | MongoDB web management | ✅ Healthy |
| **Redis** | localhost:6379 | In-memory cache | ✅ Healthy |
| **Redis Commander** | http://redis.pocmaster.argentquest.com | Redis web management | ✅ Healthy |

### Storage & Infrastructure

| Service | URL | Purpose | Status |
|---------|-----|---------|---------|
| **MinIO** | http://minio.pocmaster.argentquest.com | S3-compatible object storage | ✅ Healthy |
| **Portainer** | http://portainer.pocmaster.argentquest.com | Docker container management | ✅ Healthy |
| **NPM Admin** | http://pocmaster.argentquest.com:81 | Nginx Proxy Manager | ✅ Healthy |

### Development Tools

| Service | URL | Purpose | Status |
|---------|-----|---------|---------|
| **VS Code Server** | http://code.pocmaster.argentquest.com | Browser-based IDE | ✅ Healthy |
| **MCP Inspector** | http://mcp.pocmaster.argentquest.com | Model Context Protocol testing | ✅ Healthy |
| **n8n Workflows** | http://n8n.pocmaster.argentquest.com | Visual workflow automation | ✅ Healthy |
| **Jupyter Lab** | http://jupyter.pocmaster.argentquest.com | Data science notebooks | ✅ Healthy |

### Dashboards

| Service | URL | Purpose | Status |
|---------|-----|---------|---------|
| **System Monitor** | http://pocmaster.argentquest.com | Real-time container stats | ✅ Healthy |
| **Beszel Monitoring** | http://beszel.pocmaster.argentquest.com | Server & container monitoring | ✅ Healthy |
| **Heimdall** | http://heimdall.pocmaster.argentquest.com | Application dashboard | ✅ Healthy |

### Direct Port Access (Bypass NPM)

| Service | URL | Purpose |
|---------|-----|---------|
| **pgAdmin Direct** | http://localhost:5050 | Direct PostgreSQL admin access |
| **Portainer Direct** | https://localhost:9443 | Direct Docker management |
| **Beszel Direct** | http://localhost:8090 | Direct server monitoring |

## 🛠️ Development Guide

### Virtual Machine Setup

For detailed instructions on how to set up VirtualBox and create a new virtual machine, please refer to the [VirtualBox.md](VirtualBox.md) file.

### Dual FastAPI Environment

This stack provides two FastAPI instances for flexible development:

#### Production Container (app-prod)
- **URL:** http://api.pocmaster.argentquest.com
- **Purpose:** Production-like testing with Gunicorn workers
- **Environment:** Uses production settings
- **Command:** `uvicorn app.main:app --workers 4`

#### Development Container (app-dev)  
- **URL:** http://api-dev.pocmaster.argentquest.com
- **Purpose:** Hot-reload development
- **Environment:** Debug logging enabled
- **Command:** `uvicorn app.main:app --reload`

#### Local Debug (VS Code F5)
- **URL:** http://localhost:8001 (when running locally)
- **Purpose:** Breakpoint debugging
- **Setup:** Press F5 in VS Code

### Python Environment Setup

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install uv
```

## 🔐 Credentials Reference

### Web Interface Logins

| Service | Username/Email | Password | Notes |
|---------|---------------|----------|-------|
| **NPM Admin** | admin@example.com | changeme | ⚠️ Change on first login |
| **Beszel Monitoring** | admin@example.com | changeme | Server monitoring dashboard |
| **pgAdmin** | admin@example.com | admin | PostgreSQL web UI |
| **MongoDB Express** | admin | admin | Basic auth for web UI |
| **MinIO Console** | minioadmin | minioadmin123 | S3 storage admin |
| **VS Code Server** | - | changeme | Browser IDE |
| **n8n Workflows** | - | - | User management disabled |
| **Jupyter Lab** | - | changeme | Token-based auth |
| **Portainer** | - | - | ⚠️ First-time setup required |

### Database Connections

#### **For External Tools (Host Machine Access)**

**PostgreSQL:**
```
Host: localhost:5432
Database: poc_db
Username: pocuser
Password: pocpass
Connection String: postgresql://pocuser:pocpass@localhost:5432/poc_db
```

**MongoDB:**
```
Host: localhost:27017
Database: poc_mongo_db
Username: mongoadmin
Password: mongopass123
Connection String: mongodb://mongoadmin:mongopass123@localhost:27017/poc_mongo_db
```

**Redis:**
```
Host: localhost:6379
Database: 0
Password: (none)
Connection String: redis://localhost:6379
```

#### **For Docker Applications (Internal Network)**

**PostgreSQL:**
```
Host: postgres:5432
Database: poc_db
Username: pocuser
Password: pocpass
Connection String: postgresql://pocuser:pocpass@postgres:5432/poc_db
```

**MongoDB:**
```
Host: mongodb:27017
Database: poc_mongo_db
Username: mongoadmin
Password: mongopass123
Connection String: mongodb://mongoadmin:mongopass123@mongodb:27017/poc_mongo_db
```

**Redis:**
```
Host: redis:6379
Database: 0
Connection String: redis://redis:6379
```

**Note:** All three environment files (`.env`, `.env.dev`, `.env.prod`) use Docker container names for reliable internal network communication. External database clients should use localhost connections.

### Test Data & User Profiles

**PostgreSQL Test Users:**
| Username | Email | Password Hash | Role |
|----------|-------|---------------|------|
| admin | admin@example.com | $2b$12$... | System admin |
| testuser1 | test1@example.com | $2b$12$... | Test user |
| testuser2 | test2@example.com | $2b$12$... | Test user |
| writer1 | writer1@example.com | $2b$12$... | Story writer |
| writer2 | writer2@example.com | $2b$12$... | Story writer |

**PostgreSQL Test Stories:**
- "The Dragon\'s Quest" (fantasy, 245 words)
- "Cyber Shadows" (cyberpunk, 189 words) 
- "The Time Merchant" (sci-fi, 312 words)
- "Whispers in the Wind" (mystery, 167 words)
- "The Last Library" (dystopian, 298 words)

**MongoDB Test Users (Detailed Profiles):**
| Username | Full Name | Bio | Writing Style | AI Preference |
|----------|-----------|-----|---------------|---------------|
| alice_writer | Alice Johnson | Fantasy writer and world builder | Descriptive | High AI assistance |
| bob_cyberpunk | Robert Chen | Cyberpunk novelist and tech enthusiast | Technical | Medium AI assistance |
| carol_scifi | Dr. Carol Martinez | Science fiction author and physicist | Scientific | Low AI assistance |
| david_mystery | David Thompson | Mystery and thriller writer | Suspenseful | High AI assistance |
| eva_dystopian | Eva Rodriguez | Dystopian fiction specialist | Atmospheric | Medium AI assistance |

**MongoDB Collections:**
- **users**: 7 records with full profiles, preferences, and writing history
- **documents**: Story manuscripts with metadata and word counts
- **world_building**: Characters, locations, organizations, and lore items
- **ai_conversations**: Chat history with AI assistants and token usage
- **sessions**: User activity logs and interaction tracking

**Note:** All passwords use bcrypt hashing. For testing authentication, use the provided test users or create new accounts through the API endpoints.

## 🧪 Testing & Validation

### Health Check
```bash
python health-check.py
```
**Expected Result:** 22/22 services healthy (100.0%)

### Database Validation
```bash
./validate-database-setup.sh
```
**Purpose:** Validates PostgreSQL and MongoDB connections, test data integrity, and management tool access

### Comprehensive Test Suite
```bash
python run_all_tests.py
```

### Individual Service Tests
```bash
python tests/test_01_containers_health.py
python tests/test_02_database_pgvector.py
python tests/test_03_openrouter_integration.py
python tests/test_04_minio_storage.py
python tests/test_05_redis_cache.py
python tests/test_06_end_to_end.py
```

## 🛠️ Troubleshooting

### Common Issues

**"502 Bad Gateway" Errors:**
- Check container health: `docker-compose ps`
- Verify network connectivity: containers should use service names
- Restart specific service: `docker-compose restart <service-name>`

**Services Not Accessible:**
- Verify hosts file entries are correct
- Check NPM proxy configuration at port 81
- Ensure all containers are healthy

**Database Connection Issues:**
- **Docker containers:** Use service names (`postgres`, `mongodb`, `redis`) - configured in all `.env` files
- **External tools:** Use `localhost` ports (5432, 27017, 6379) from host machine
- Verify credentials match environment files (`.env`, `.env.dev`, `.env.prod`)
- Check container logs: `docker-compose logs <service-name>`

### Network Troubleshooting
```bash
# Check all containers
docker-compose ps

# Check network connectivity
docker exec aq-devsuite-app-dev ping postgres
docker exec aq-devsuite-app-dev ping mongodb

# View service logs
docker-compose logs -f <service-name>
```

## ⚙️ Advanced Configuration

### Custom Domain Setup

To use your own domain instead of `pocmaster.argentquest.com`:

1. **Update these files:**
   - `docker-compose.yml` - No changes needed (uses service names)
   - `hosts file` - Replace with your domain
   - NPM proxy configuration - Update domain names

2. **NPM Proxy Update:**
   ```bash
   # Use provided scripts with your domain
   python npm-complete-setup.py  # Update domains in script first
   ```

### SSL Configuration

For production with real domain:
```bash
python npm-ssl-setup.py  # Configure Let\'s Encrypt
```

### Monitoring Setup

**Health Monitoring:**
```bash
python health-check.py  # Run periodically
```

**Container Stats:**
- **System Monitor:** http://pocmaster.argentquest.com
- **Portainer:** http://portainer.pocmaster.com

## 🔧 Maintenance Commands

### Container Management
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart <service-name>

# View all container logs
docker-compose logs -f

# Update and rebuild
docker-compose up -d --build
```

### Database Maintenance
```bash
# PostgreSQL backup
docker exec aq-devsuite-postgres pg_dump -U pocuser poc_db > backup.sql

# MongoDB backup
docker exec aq-devsuite-mongodb mongodump --db poc_mongo_db --out /backup

# Redis backup
docker exec aq-devsuite-redis redis-cli SAVE
```

### Cleanup Commands
```bash
# Stop all containers
docker-compose down

# Full cleanup (⚠️ Deletes data!)
docker-compose down --volumes --rmi all

# System cleanup
docker system prune -a
```

## 📈 Performance & Monitoring

### Current Performance Metrics
- **All Services Response Time:** 8-200ms
- **Health Check Status:** 22/22 services healthy (100%)
- **Network Latency:** < 10ms (single network)
- **Memory Usage:** ~6GB total (all containers)

### Monitoring Tools
- **Real-time Stats:** http://pocmaster.argentquest.com
- **Container Management:** http://portainer.pocmaster.com  
- **Health Monitoring:** `python health-check.py`

## 🗺️ Migration Benefits

### Cost Comparison
| Service | Azure (Monthly) | Docker (Monthly) | Savings |
|---------|-----------------|------------------|---------|
| Compute | $150 | $20 (VPS) | $130 |
| Vector Search | $250 | $0 (pgvector) | $250 |
| Database | $50 | $5 (included) | $45 |
| Storage | $20 | $2 (included) | $18 |
| Redis | $30 | $0 (included) | $30 |
| **Total** | **$500** | **$45** | **$455 (91%)** |

## 🚧 Known Limitations

1. **POC Scope**: Proof-of-concept, not production-ready
2. **Local Development**: Requires hosts file entries
3. **SSL**: Let\'s Encrypt needs real domain for production
4. **Monitoring**: Basic health checks (add Grafana for production)
5. **Backup**: Manual backup procedures (automate for production)

## 📖 Quick Reference

### Essential URLs
- **Main Dashboard:** http://pocmaster.argentquest.com
- **NPM Admin:** http://pocmaster.argentquest.com:81
- **API Docs:** http://api.pocmaster.argentquest.com/docs
- **Beszel Monitoring:** http://beszel.pocmaster.argentquest.com
- **Heimdall:** http://heimdall.pocmaster.argentquest.com

### Essential Commands
```bash
docker-compose up -d          # Start all services (22 containers)
bash scripts/setup-npm-hosts.sh  # Auto-configure NPM proxy hosts
docker-compose ps             # Check status
python health-check.py        # Verify health
docker-compose logs -f app    # View API logs
```

### Argentquest Development Suite Container Names
```
aq-devsuite-npm          # Nginx Proxy Manager
aq-devsuite-app-prod          # FastAPI Production
aq-devsuite-app-dev           # FastAPI Development  
aq-devsuite-postgres          # PostgreSQL Database
aq-devsuite-mongodb           # MongoDB Database
aq-devsuite-redis             # Redis Cache
aq-devsuite-minio             # MinIO Object Storage
aq-devsuite-pgadmin           # pgAdmin Web UI
aq-devsuite-mongo-express     # MongoDB Web UI
aq-devsuite-redis-commander   # Redis Web UI
aq-devsuite-portainer         # Docker Management
aq-devsuite-heimdall          # Application Dashboard
aq-devsuite-vscode            # VS Code Server
aq-devsuite-mcp-inspector     # MCP Protocol Testing
aq-devsuite-beszel            # Beszel Monitoring Hub
aq-devsuite-beszel-agent      # Beszel Monitoring Agent
aq-devsuite-system-monitor    # System Stats Frontend
aq-devsuite-monitor-api       # System Stats Backend
aq-devsuite-npm-setup       # NPM Auto-Setup
aq-devsuite-beszel-setup      # Beszel Auto-Setup
```

---

## 🌟 **Community**

### 🤝 **Get Involved**
- **GitHub Issues**: [Report bugs](../../issues) and [request features](../../issues)
- **GitHub Discussions**: Coming soon for community conversations
- **Contributing**: Read our [Contributing Guide](CONTRIBUTING.md)
- **Roadmap**: Check our [project roadmap](ROADMAP.md) to see what's planned

### 💡 **Perfect for**
- **Learning**: Docker, microservices, FastAPI, database management
- **Development**: Full-stack application development environment
- **Testing**: Multi-service integration testing
- **Proof of Concepts**: Enterprise architecture exploration
- **Cost Savings**: Replace expensive cloud development environments

### 🏆 **Recognition**
Contributors to this project are recognized in our community! Check out [CONTRIBUTORS.md](CONTRIBUTORS.md) (coming soon) and help make this project even better.

### ❓ **Getting Help**
1. **Check Documentation**: Start with our comprehensive guides
2. **Search Issues**: See if your question has been answered
3. **Ask Questions**: Create an issue with the 'question' label
4. **Join Discussions**: Participate in community conversations

### 🚨 **Important Notes**
- **Development Environment**: This is designed for development and learning
- **Security Warning**: Default credentials throughout - see [SECURITY.md](SECURITY.md)
- **Production Use**: Requires significant hardening - not production-ready out of the box

---

**Status:** All 22 services healthy (100%) - Ready for development and testing  
**Version:** 2.1.1
**Last Updated:** December 7, 2025

**🚀 Ready to contribute? Start with a [good first issue](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) or check our [roadmap](ROADMAP.md) for bigger challenges!**