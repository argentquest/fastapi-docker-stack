# Environment Configuration for Argentquest Development Suite

## ⚠️ IMPORTANT SECURITY NOTICE ⚠️

**THIS IS A DEVELOPMENT/PROOF-OF-CONCEPT SYSTEM - NOT PRODUCTION READY**

This documentation describes environment configuration for the **22-container development environment**. All default credentials and configurations are designed for development purposes only and must be changed before any production use.

## Overview

The Argentquest Development Suite uses a three-tier environment configuration system to support different deployment scenarios across the 22-container architecture. Each configuration connects to shared database instances but with different application behaviors and security settings.

## Environment Files Architecture

### `.env` (Main/Local Development Configuration)
- **Purpose**: Primary configuration for local development and local debugging
- **Database Connection**: Docker network connections (`postgres:5432`, `mongodb:27017`)
- **Use Cases**: 
  - Local VS Code debugging (FastAPI - Local Debug configuration)
  - Direct application development outside containers
  - Environment variable defaults and shared configuration
  - Base configuration that other environments inherit from

### `.env.dev` (Development Container Environment)
- **Purpose**: Configuration for `app-dev` container with hot-reload debugging
- **Container**: `aq-devsuite-app-dev`
- **URL**: `http://api-dev.pocmaster.argentquest.com`
- **Database Connection**: Docker network connections (`postgres:5432`, `mongodb:27017`)
- **Features**: 
  - DEBUG level logging with detailed output
  - Hot reload enabled via volume mount (`./app:/app/app`)
  - Relaxed CORS policies for development
  - Single worker for easier debugging
  - Extended session timeouts
  - SQL query logging enabled
  - Development-specific error handling

### `.env.prod` (Production Container Environment)  
- **Purpose**: Configuration for `app-prod` container simulating production environment
- **Container**: `aq-devsuite-app-prod`
- **URL**: `http://api.pocmaster.argentquest.com`
- **Database Connection**: Docker network connections (`postgres:5432`, `mongodb:27017`)
- **Features**:
  - INFO level logging for performance
  - Multiple Uvicorn workers (4) for concurrent request handling
  - Strict CORS policies
  - Production-style security settings
  - Audit logging enabled
  - Performance monitoring and optimization
  - Production error handling patterns

## Shared Database Architecture

All three environment configurations connect to the same shared database instances within the 22-container stack. This design enables consistent data access across development, testing, and production-like environments while maintaining environment-specific application behaviors.

### PostgreSQL 16 with pgvector
- **Container**: `aq-devsuite-postgres`
- **Internal Connection**: `postgres:5432` (Docker network)
- **External Access**: `localhost:5432` (for tools like pgAdmin)
- **Connection String**: `postgresql://pocuser:pocpass@postgres:5432/poc_db`
- **Features**: 
  - pgvector extension for vector similarity search
  - Comprehensive test data (5+ users, stories, world elements)
  - Advanced PostgreSQL configuration for performance
  - Connection pooling support
- **Test Data**: Users, stories, world_elements, ai_cost_logs, job_statuses
- **Management**: pgAdmin available at `http://pgadmin.pocmaster.argentquest.com`

### MongoDB 7.0
- **Container**: `aq-devsuite-mongodb` 
- **Internal Connection**: `mongodb:27017` (Docker network)
- **External Access**: `localhost:27017` (for development tools)
- **Connection String**: `mongodb://mongoadmin:mongopass123@mongodb:27017/poc_mongo_db`
- **Features**:
  - NoSQL document storage for flexible schemas
  - Comprehensive test data (5+ users, documents, world elements)
  - Replica set configuration ready
  - GridFS support for file storage
- **Test Data**: users, documents, world_building, ai_conversations, system_logs
- **Management**: Mongo Express available via NPM proxy

### Redis 7.2 (Cache Layer)
- **Container**: `aq-devsuite-redis`
- **Internal Connection**: `redis:6379` (Docker network)
- **Features**:
  - In-memory caching for performance
  - Session storage
  - Rate limiting data
  - Background job queue support
- **Configuration**: Memory limits, persistence, LRU eviction
- **Management**: Redis Commander available via NPM proxy

### MinIO (S3-Compatible Storage)
- **Container**: `aq-devsuite-minio`
- **Internal Connection**: `minio:9000` (Docker network)
- **External Access**: Via NPM proxy setup
- **Features**:
  - S3-compatible object storage
  - File upload and management
  - Multi-bucket support
  - Development-friendly setup

## Environment Configuration Comparison

| Setting | Local (.env) | Development (.env.dev) | Production (.env.prod) |
|---------|--------------|------------------------|------------------------|
| **Purpose** | Local debugging | Container development | Production testing |
| **Container** | None (local) | `aq-devsuite-app-dev` | `aq-devsuite-app-prod` |
| **URL Access** | `localhost:8001` | `api-dev.pocmaster.argentquest.com` | `api.pocmaster.argentquest.com` |
| **Logging Level** | DEBUG | DEBUG | INFO |
| **Log Format** | Text | Text with colors | JSON structured |
| **Workers** | 1 (uvicorn) | 1 (debugging) | 4 (performance) |
| **Hot Reload** | Yes (--reload) | Yes (volume mount) | No |
| **CORS** | Development | Permissive | Restrictive |
| **Security** | Development | Relaxed | Production-like |
| **Error Detail** | Full stack traces | Development details | Sanitized messages |
| **Caching TTL** | 5 minutes | 5 minutes | 1 hour |
| **Rate Limiting** | 200/min | 120/min | 60/min |
| **Session Timeout** | 2 hours | 2 hours | 1 hour |
| **Database Pool** | 5-10 connections | 10-20 connections | 20-50 connections |

## Container Architecture Integration

### Docker Compose Implementation
The 22-container stack uses these environment files as follows:

```yaml
# Development container with hot-reload
app-dev:
  build: .
  container_name: aq-devsuite-app-dev
  env_file:
    - .env.dev
  volumes:
    - ./app:/app/app  # Hot-reload volume mount
  command: ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production container with multiple workers
app-prod:
  build: .
  container_name: aq-devsuite-app-prod
  env_file:
    - .env.prod
  command: ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Development Workflow Usage

#### **Local Development (VS Code Debugging)**
```bash
# 1. Ensure all containers are running
docker-compose up -d

# 2. Use .env file for local debugging
# 3. Access local instance at: http://localhost:8001
# 4. Database connections use Docker network names
```

#### **Container Development (Hot-Reload)**
```bash
# 1. Edit code in ./app/ directory
# 2. app-dev container automatically detects changes
# 3. Access development API at: http://api-dev.pocmaster.argentquest.com
# 4. Uses .env.dev configuration with debug logging
```

#### **Production Testing**
```bash
# 1. Test production-like behavior
# 2. Access production API at: http://api.pocmaster.argentquest.com  
# 3. Uses .env.prod configuration with performance optimization
# 4. Multiple workers handle concurrent requests
```

### Environment Validation and Testing
```bash
# Complete system health check (all 22 containers)
python health-check.py

# Validate database connections and test data
./validate-database-setup.sh

# Check environment-specific configurations
docker exec aq-devsuite-app-dev env | grep -E "(DATABASE_URL|APP_ENV|LOG_LEVEL)"
docker exec aq-devsuite-app-prod env | grep -E "(DATABASE_URL|APP_ENV|LOG_LEVEL)"

# Compare logging behavior
docker-compose logs -f app-dev   # Debug logging
docker-compose logs -f app-prod  # Info logging

# Test API endpoints in different environments
curl http://api-dev.pocmaster.argentquest.com/health   # Development
curl http://api.pocmaster.argentquest.com/health       # Production
```

### Configuration Management

#### **Creating Environment Files**
```bash
# Start with template
cp .env.template .env
cp .env.template .env.dev
cp .env.template .env.prod

# Customize for each environment
nano .env      # Local development settings
nano .env.dev  # Container development settings  
nano .env.prod # Production-like settings
```

#### **Required Environment Variables**
All environment files should include:
```bash
# API Configuration
OPENROUTER_API_KEY=your_api_key_here
APP_ENV=development  # or production
LOG_LEVEL=DEBUG      # or INFO

# Database Connections (Docker network names)
DATABASE_URL=postgresql://pocuser:pocpass@postgres:5432/poc_db
MONGODB_URL=mongodb://mongoadmin:mongopass123@mongodb:27017/poc_mongo_db
REDIS_URL=redis://redis:6379/0

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production

# External Services
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

## 🔒 Security and Default Credentials Warning

**⚠️ CRITICAL: This system uses default credentials throughout - NOT production ready! ⚠️**

### **Default Credentials Used Across All Environments**

| Service | Username | Password | Notes |
|---------|----------|----------|-------|
| **PostgreSQL** | `pocuser` | `pocpass` | Database access |
| **MongoDB** | `mongoadmin` | `mongopass123` | Database access |
| **pgAdmin** | `admin@example.com` | `admin` | Web interface |
| **Mongo Express** | `admin` | `admin` | Web interface |
| **MinIO** | `minioadmin` | `minioadmin123` | Object storage |
| **VS Code Server** | N/A | `dev123` | Browser IDE |
| **NPM Admin** | `admin@example.com` | `changeme` | Proxy management |
| **Beszel** | `admin@example.com` | `changeme` | Monitoring |
| **Jupyter** | N/A | `changeme` | Token-based |

### **Security Requirements for Production Use**
Before any production deployment, you MUST:

1. **Change ALL Default Passwords**
   - Generate strong, unique passwords for each service
   - Use password managers or secret generation tools
   - Document new credentials securely

2. **Implement Authentication**
   - Add JWT or OAuth2 to FastAPI endpoints
   - Enable proper user management
   - Implement role-based access control

3. **Network Security**
   - Enable HTTPS with valid certificates
   - Configure firewalls and security groups
   - Use VPN for administrative access

4. **Environment Variable Security**
   - Move secrets out of .env files
   - Use Docker Secrets or external secret management
   - Encrypt sensitive configuration data

### **Environment-Specific Security Considerations**

#### **.env (Local Development)**
- Safe for local development only
- Never commit to version control
- Use for testing and debugging

#### **.env.dev (Development Container)**  
- Includes debug features that expose system information
- Extended error messages with stack traces
- Relaxed CORS and security policies
- Should not be used with real user data

#### **.env.prod (Production Container)**
- More secure configuration but still has default passwords
- Production-style logging and error handling
- Requires additional hardening for actual production use
- Multiple workers for better performance

## Monitoring and Management Access

### **Service URLs (After NPM Setup)**
- **Main Dashboard**: `http://pocmaster.argentquest.com`
- **Development API**: `http://api-dev.pocmaster.argentquest.com` 
- **Production API**: `http://api.pocmaster.argentquest.com`
- **pgAdmin**: `http://pgadmin.pocmaster.argentquest.com`
- **Portainer**: `http://localhost:9443` or via proxy
- **System Monitor**: `http://pocmaster.argentquest.com`
- **Beszel Monitor**: `http://beszel.pocmaster.argentquest.com`
- **VS Code Server**: `http://code.pocmaster.argentquest.com`

### **Direct Port Access**
When domain setup isn't available:
```bash
# Database Management
pgAdmin:         http://localhost:5050
Portainer:       http://localhost:9443
MCP Inspector:   http://localhost:5173
n8n Workflows:   http://localhost:5678
Jupyter Lab:     http://localhost:8888
NPM Admin:       http://localhost:81
Beszel:          http://localhost:8090
```

## Environment Validation and Troubleshooting

### **Comprehensive System Health Check**
```bash
# Run complete health validation (22 containers)
python health-check.py

# Database-specific validation with test data verification
./validate-database-setup.sh

# Manual container status check
docker-compose ps
docker stats --no-stream
```

### **Environment-Specific Validation**
```bash
# Validate environment variable loading
docker exec aq-devsuite-app-dev env | grep -E "(APP_ENV|LOG_LEVEL|DATABASE_URL)"
docker exec aq-devsuite-app-prod env | grep -E "(APP_ENV|LOG_LEVEL|DATABASE_URL)"

# Test environment-specific API responses
curl -s http://api-dev.pocmaster.argentquest.com/health | jq '.environment'
curl -s http://api.pocmaster.argentquest.com/health | jq '.environment'

# Compare logging output
docker-compose logs --tail=20 app-dev   # Should show DEBUG messages
docker-compose logs --tail=20 app-prod  # Should show INFO messages
```

### **Network and Service Validation**
```bash
# Test Docker internal network connectivity
docker exec aq-devsuite-app-dev ping -c 3 postgres
docker exec aq-devsuite-app-dev ping -c 3 mongodb
docker exec aq-devsuite-app-dev ping -c 3 redis

# Validate database connections
docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -c "SELECT version();"
docker exec aq-devsuite-mongodb mongosh --eval "db.adminCommand('buildinfo')" -u mongoadmin -p mongopass123

# Test external access via NPM proxy
curl -I http://pocmaster.argentquest.com
curl -I http://api-dev.pocmaster.argentquest.com
curl -I http://api.pocmaster.argentquest.com
```

### **Troubleshooting Common Issues**

#### **Environment Variables Not Loading**
```bash
# Check if files exist and have correct content
ls -la .env*
head -5 .env.dev .env.prod

# Restart containers to reload environment
docker-compose restart app-dev app-prod
```

#### **Database Connection Issues**
```bash
# Check database container health
docker-compose ps postgres mongodb redis

# Test direct database connections
docker exec -it aq-devsuite-postgres psql -U pocuser -d poc_db
docker exec -it aq-devsuite-mongodb mongosh -u mongoadmin -p mongopass123
```

#### **NPM Proxy Issues**
```bash
# Verify NPM proxy configuration
python scripts/npm-simple-setup.py
curl http://localhost:81

# Check hosts file entries
cat /etc/hosts | grep pocmaster    # Linux/Mac
type C:\Windows\System32\drivers\etc\hosts | findstr pocmaster    # Windows
```

---

## 📊 Environment Configuration Summary

| Component | Container Count | Environment Files | Database Instances | Management Tools |
|-----------|----------------|-------------------|-------------------|------------------|
| **Total Containers** | 22 | 3 (.env, .env.dev, .env.prod) | 4 (PostgreSQL, MongoDB, Redis, MinIO) | 8 (pgAdmin, Mongo Express, Portainer, etc.) |
| **Application Containers** | 2 | app-dev (.env.dev), app-prod (.env.prod) | Shared instances | Hot-reload development |
| **Security Level** | 🟡 Development | 🔴 Default credentials | 🟡 Test data included | 🔴 Not production ready |

**Remember**: This is a comprehensive development environment designed for learning, testing, and proof-of-concept work. All security warnings must be addressed before any production use.

---

**Last Updated**: August 31, 2025  
**Environment**: Argentquest Development Suite (22 containers)  
**Configuration**: Three-tier environment system with shared databases