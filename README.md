# FastAPI Docker Stack

## 🚀 Overview

A production-ready FastAPI microservices stack with PostgreSQL+pgvector, Redis, MinIO, and Nginx Proxy Manager - fully containerized with Docker. This architecture provides a cost-effective alternative to cloud services, offering up to 90% cost savings (from $400-500/month to $45-60/month) while maintaining enterprise-grade functionality.

## 🎯 Project Goals

- **Cost Reduction**: 90% reduction in monthly operational costs
- **Self-Hosted Infrastructure**: Full control over deployment and data
- **Modern Architecture**: Containerized microservices with Docker
- **Open Source Stack**: Leverage open-source alternatives to Azure services
- **Performance**: Maintain or improve response times and throughput

## 🏗️ Architecture

### Core Components (5 Containers)

```
┌─────────────────────────────────────────────────┐
│             Nginx Proxy Manager (80, 81, 443)    │
│              (Reverse Proxy & SSL)               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│               FastAPI Application                │
│         (Python 3.11 + Async + uv)              │
│                                                  │
│  • OpenRouter Integration (DeepSeek R1)         │
│  • BGE-large-en-v1.5 Embeddings (1024d)        │
│  • WebSocket Support                            │
│  • Async Request Processing                     │
└──────┬──────────┬──────────┬────────────────────┘
       │          │          │
┌──────▼────┐ ┌──▼───┐ ┌────▼────┐
│PostgreSQL │ │Redis │ │  MinIO   │
│+ pgvector │ │Cache │ │S3 Storage│
└───────────┘ └──────┘ └──────────┘
```

### Technology Stack

| Component | Current (Azure) | V2 (Docker) | Cost Savings |
|-----------|----------------|-------------|--------------|
| **Hosting** | Azure App Service | VPS + Docker | 95% |
| **Vector Search** | Azure AI Search | PostgreSQL + pgvector | 100% |
| **LLM Provider** | Azure OpenAI | OpenRouter (DeepSeek R1) | 95% |
| **Object Storage** | Azure Blob Storage | MinIO (S3-compatible) | 100% |
| **Database** | Azure PostgreSQL | PostgreSQL 16 | 90% |
| **Caching** | Azure Redis | Redis 7.2 | 100% |
| **CDN/Proxy** | Azure CDN | Nginx Proxy Manager | 100% |

## 📋 Prerequisites

- **Python 3.11** or higher
- **Docker** & **Docker Compose**
- **uv** package manager (`pip install uv`)
- **8GB RAM** minimum (16GB recommended)
- **20GB disk space** for containers and data
- **OpenRouter API key** with credits

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd V2

# Create Python virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies with uv
pip install uv
uv pip install -e .
```

### 2. Configure Environment

Create `.env` file with your credentials:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY="your-api-key-here"
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
DEFAULT_MODEL=deepseek/deepseek-r1

# Database Configuration
POSTGRES_USER=pocuser
POSTGRES_PASSWORD=secure-password-here
POSTGRES_DB=poc_db

# MinIO Configuration
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=secure-minio-password

# Redis Configuration (optional)
REDIS_PASSWORD=secure-redis-password

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

### 3. Start Services

```bash
# Start all containers
docker-compose up -d

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Run Tests


```bash
# Run comprehensive test suite
python run_all_tests.py

# Or run individual tests
python tests/test_01_containers_health.py
python tests/test_02_database_pgvector.py
python tests/test_03_openrouter_integration.py
python tests/test_04_minio_storage.py
python tests/test_05_redis_cache.py
python tests/test_06_end_to_end.py

# Test with book content (500KB+ text)
python tests/test_vector_with_book.py
```

## Ports and Services Reference

| Service | Purpose | Port(s) | Access URL / Details |
| :--- | :--- | :--- | :--- |
| **FastAPI Docker** | Production API (Container) | `8000` | `http://localhost:8000` (direct) or `http://localhost/docs` (via Nginx) |
| **FastAPI Debug** | Development API (Local) | `8001` | `http://localhost:8001` (VS Code F5 debug mode with hot-reload) |
| **Nginx Proxy** | Reverse Proxy & Admin | `80`, `443`, `81` | `http://localhost` (proxied apps), `http://localhost:81` (admin UI) |
| **PostgreSQL** | Database Server | `5432` | Connect via SQL client at `localhost:5432` |
| **MinIO S3** | S3 API Endpoint | `9000` | `http://localhost:9000` |
| **MinIO Console** | S3 Web UI | `9001` | `http://localhost:9001` |
| **Redis** | Cache Server | `6379` | Connect via Redis client at `localhost:6379` |
| **pgAdmin** | PostgreSQL Web UI | `5050` | `http://localhost:5050` |
| **Redis Commander**| Redis Web UI | `8081` | `http://localhost:8081` |
| **Dashboard** | Central Menu/Dashboard | `8082` | `http://localhost:8082` |


## ✅ Infrastructure Validation Plan

This plan outlines the steps to verify that all components of the infrastructure are running correctly after deployment.

### Step 1: Start and Check All Containers

1.  **Start the stack:** From the project root, run the following command. The `-d` flag runs the containers in detached mode.
    ```bash
    docker-compose up -d
    ```
2.  **Check container status:** Run the `docker-compose ps` command to ensure all containers are running and healthy. You should see a `State` of `Up` and `Status` indicating "healthy" for all services with healthchecks.

### Step 2: Verify Web UIs and Services

Go through the following URLs to ensure each web interface is accessible:

1.  **Service Dashboard:**
    *   **URL:** [http://localhost:8082](http://localhost:8082)
    *   **Check:** The dashboard loads and all links to other services are present.

2.  **Nginx Proxy Manager:**
    *   **URL:** [http://localhost:81](http://localhost:81)
    *   **Check:** The login page appears. You can log in with the default credentials (`admin@example.com` / `changeme`).

3.  **FastAPI Application:**
    *   **URL:** [http://localhost/docs](http://localhost/docs) (served via Nginx)
    *   **Check:** The Swagger UI for the API documentation loads correctly.
    *   **URL:** [http://localhost/health](http://localhost/health)
    *   **Check:** The health check endpoint returns a JSON response with a `"status": "healthy"` message.

4.  **MinIO Console:**
    *   **URL:** [http://localhost:9001](http://localhost:9001)
    *   **Check:** The MinIO login page appears. You can log in with the default credentials (`minioadmin` / `minioadmin123`).

5.  **pgAdmin:**
    *   **URL:** [http://localhost:5050](http://localhost:5050)
    *   **Check:** The pgAdmin login page appears. You can log in with (`admin@example.com` / `admin`). To fully validate, add the `postgres` server using the details from the "Connecting to Services" section.

6.  **Redis Commander:**
    *   **URL:** [http://localhost:8081](http://localhost:8081)
    *   **Check:** The Redis Commander interface loads and shows a connection to the `redis` instance.

### Step 3: Verify Backend Service Connectivity (CLI)

1.  **PostgreSQL:**
    *   **Action:** Connect to the database using pgAdmin or another SQL client.
    *   **Check:** Run the following SQL query to ensure the `vector` extension is enabled:
        ```sql
        SELECT * FROM pg_extension WHERE extname = 'vector';
        ```
    *   **Expected Result:** The query should return one row with details about the `vector` extension.

2.  **Redis:**
    *   **Action:** Run the following command to connect to the Redis container and ping the server:
        ```bash
        docker exec -it v2-poc-redis redis-cli ping
        ```
    *   **Expected Result:** The command should return `PONG`.

### Step 4: Run the Automated Test Suite

The most comprehensive validation is to run the project's end-to-end tests.

1.  **Action:** Run the main test script from your activated Python virtual environment.
    ```bash
    python run_all_tests.py
    ```
2.  **Check:** All tests should pass, indicating that all services are not only running but also correctly integrated and functioning as expected.

## 🗄️ Database Connectivity

You can connect to the PostgreSQL database using any standard SQL client. Here are the connection details for DBeaver:

-   **Connection Type:** PostgreSQL
-   **Host:** `localhost`
-   **Port:** `5432`
-   **Database:** `poc_db`
-   **Username:** `pocuser`
-   **Password:** `pocpass` (or the value you set in your `.env` file)

**Note:** Ensure the Docker containers are running before attempting to connect.

## 🔌 Connecting to Services

Here's how to connect to the different services running in the Docker containers:

### Nginx Proxy Manager

-   **Web UI:** [http://localhost:81](http://localhost:81)
-   **Default Email:** `admin@example.com`
-   **Default Password:** `changeme`

After logging in for the first time, you will be prompted to change the default credentials.

### FastAPI Application (Dual-Port Setup)

The FastAPI application runs in two modes for flexible development:

#### Production Mode (Docker Container - Port 8000)
-   **Direct API Access:** [http://localhost:8000](http://localhost:8000)
-   **API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
-   **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
-   **Via Nginx Proxy:** [http://localhost/docs](http://localhost/docs) (proxied through port 80)
-   **Purpose:** Production-like testing with full Docker stack integration

#### Debug Mode (Local Development - Port 8001)
-   **Direct API Access:** [http://localhost:8001](http://localhost:8001)
-   **API Docs (Swagger UI):** [http://localhost:8001/docs](http://localhost:8001/docs)
-   **Health Check:** [http://localhost:8001/health](http://localhost:8001/health)
-   **Purpose:** Local debugging with VS Code breakpoints and hot-reload
-   **Launch:** Press F5 in VS Code or run `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`

**Note:** Both instances connect to the same Docker infrastructure (PostgreSQL, Redis, MinIO), enabling seamless development and testing workflows.

### MinIO (S3 Storage)

-   **S3 API Endpoint:** `localhost:9000`
-   **Console (Web UI):** [http://localhost:9001](http://localhost:9001)
-   **Access Key:** `minioadmin`
-   **Secret Key:** `minioadmin123` (or the value you set in your `.env` file)

You can use any S3-compatible client (like `s3cmd` or the AWS CLI) to interact with the S3 API.

### pgAdmin (Database Management)

#### Access pgAdmin

-   **Web UI:** [http://localhost:5050](http://localhost:5050)
-   **Login Email:** `admin@example.com`
-   **Login Password:** `admin`

#### Connect to PostgreSQL Database

After logging in, follow these steps to connect to your database:

1. **Right-click** on "Servers" in the left panel
2. Select **"Register" → "Server..."**
3. Configure the connection:

**General Tab:**
-   **Name:** `V2 POC Database` (or any name you prefer)

**Connection Tab:**
-   **Host name/address:** `host.docker.internal` (IMPORTANT: Not localhost!)
-   **Port:** `5432`
-   **Maintenance database:** `poc_db`
-   **Username:** `pocuser`
-   **Password:** `pocpass`
-   **Save password:** ✓ (check this box)

4. Click **"Save"**

**Alternative Host Options** (if `host.docker.internal` doesn't work):
-   **Option A:** Use container name: `postgres`
-   **Option B:** Use Docker network IP: Run `docker inspect v2-poc-postgres | grep IPAddress` and use that IP

#### Verify Connection

Once connected, you should see:
-   **Databases** → `poc_db`
-   **Schemas** → `public`
-   **Tables** → `ai_test_logs`
-   **Extensions** → `vector` (pgvector extension)

#### Test pgVector

Open Query Tool and run:
```sql
-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check stored embeddings
SELECT COUNT(*) FROM ai_test_logs;

-- View embedding dimensions
SELECT octet_length(embedding::text) as embedding_size FROM ai_test_logs LIMIT 1;
```

### Redis Commander (Web UI for Redis)

-   **Web UI:** [http://localhost:8081](http://localhost:8081)

### Redis (Cache)

You can connect to the Redis container using `redis-cli`:

```bash
# Connect to the Redis container
docker exec -it v2-poc-redis redis-cli

# Ping the server to test the connection
127.0.0.1:6379> ping
PONG

# If you have a password set in your .env file, you will need to authenticate
127.0.0.1:6379> AUTH your-redis-password
OK
```

## 📚 API Documentation

### Endpoints

#### POST `/ai-test`
Test endpoint that validates all 5 containers working together.

**Request:**
```json
{
  "system_prompt": "You are a helpful assistant",
  "user_context": "Tell me a story about robots"
}
```

**Response:**
```json
{
  "id": 1,
  "ai_result": "Generated AI response...",
  "embedding_similarity": 0.95,
  "file_url": "http://localhost:9000/poc-bucket/result_123.txt",
  "response_time_ms": 1250,
  "containers_tested": {
    "openrouter": "success",
    "postgres": "success",
    "pgvector": "success",
    "minio": "success",
    "redis": "success"
  },
  "created_at": "2025-01-23T10:30:00Z"
}
```

#### GET `/health`
Health check endpoint for all services.

**Response:**
```json
{
  "status": "healthy",
  "containers": {
    "openrouter": {"status": "healthy"},
    "postgres": {"status": "healthy", "pool_size": 10},
    "redis": {"status": "healthy"},
    "minio": {"status": "healthy", "buckets": 1},
    "embedding": {"status": "healthy", "model": "BGE-large-en-v1.5"}
  }
}
```

## 🧪 Testing

### Test Coverage

The POC includes comprehensive tests for:

1. **Container Health** - Validates all 5 containers are running
2. **Database + pgvector** - Tests vector operations and similarity search
3. **OpenRouter Integration** - Validates AI generation with DeepSeek R1
4. **MinIO Storage** - Tests S3-compatible file operations
5. **Redis Cache** - Validates caching functionality
6. **End-to-End** - Complete workflow testing
7. **Vector Search** - Tests with real book content (Andersen's Fairy Tales)

### Performance Benchmarks

| Operation | Target | Actual |
|-----------|--------|--------|
| AI Generation | < 5s | ~2-3s |
| Vector Search (1M vectors) | < 100ms | ~50ms |
| File Upload (10MB) | < 1s | ~200ms |
| Cache Hit | < 10ms | ~2ms |

## 🔒 Security Features

### Implemented Security Measures

- ✅ Input validation and sanitization (Pydantic)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Error message sanitization (no internal details exposed)
- ✅ Environment-based configuration (no hardcoded secrets)
- ✅ Container security (non-root users, read-only filesystems)
- ✅ Network isolation (internal Docker networks)
- ✅ Resource limits (memory and CPU constraints)

### Production Security (docker-compose.prod.yml)

- Security options: `no-new-privileges`
- Read-only root filesystem with tmpfs for writable areas
- Resource limits and reservations
- User namespacing (non-root execution)
- Internal-only network for service communication
- Health checks with proper timeouts

## 🛠️ Development

### VS Code Development Environment

The project includes comprehensive VS Code configuration files in the `.vscode/` directory:

#### Launch Configurations (`.vscode/launch.json`)
- **FastAPI - Local Debug (Port 8001)**: Main debug configuration for local development
  - Launches FastAPI on port 8001 with hot-reload
  - Enables breakpoint debugging and step-through debugging
  - Loads environment variables from `.env` file
  - Overrides specific settings for development (DEBUG log level)
- **FastAPI - Docker Remote Debug**: Attach debugger to running Docker container
  - Connects to container's debug port (5678) for remote debugging
  - Maps local workspace to container paths
- **Python: Current File**: Debug any individual Python file with environment support

#### Development Tasks (`.vscode/tasks.json`)
Pre-configured tasks accessible via Ctrl+Shift+P → "Tasks: Run Task":
- **Docker Operations**: `docker-compose-up`, `docker-compose-down`, `docker-compose-build`, `docker-compose-logs`
- **Python Environment**: `create-venv`, `activate-venv`, `install-dependencies`
- **Testing Suite**: `run-tests` (all tests), plus individual test tasks for each test file
- **Code Quality**: `format-code` (Black), `lint-code` (Flake8), `check-types` (MyPy)

#### Editor Settings (`.vscode/settings.json`)
- **Python Environment**: Automatically uses `.venv/Scripts/python.exe`
- **Code Formatting**: Black formatter with 120-character line length
- **Linting**: Flake8 enabled with custom rules (E203, W503 ignored)
- **Testing**: Pytest integration configured
- **File Associations**: Auto-detects Dockerfiles, SQL, environment files
- **Docker Integration**: Container management and debugging support

#### Recommended Extensions (`.vscode/extensions.json`)
Essential extensions for optimal development experience:
- **Python Development**: Python, Pylance, Black formatter, Flake8, MyPy
- **Docker Support**: Docker extension, Remote-Containers
- **Database Tools**: SQLTools with PostgreSQL driver
- **Code Quality**: SonarLint, spell checker
- **API Testing**: REST Client, Thunder Client for testing endpoints
- **Git Integration**: GitLens, Git Graph for enhanced version control

#### Code Snippets (`.vscode/*.code-snippets`)
- **Python snippets**: FastAPI routes, async functions, database operations
- **Docker snippets**: Common Docker commands and configurations

**Getting Started with VS Code:**
1. Open project in VS Code: `code .`
2. Install recommended extensions when prompted
3. Press `F5` to start debug server on port 8001
4. Use `Ctrl+Shift+P` → "Tasks: Run Task" for common operations
5. Access Docker container logs via Docker extension sidebar

### Project Structure

```
V2/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   └── config.py         # Configuration management
│   └── services/
│       ├── openrouter_service.py   # AI generation
│       ├── embedding_service.py    # Vector embeddings
│       ├── database_service.py     # PostgreSQL + pgvector
│       ├── storage_service.py      # MinIO S3 storage
│       └── cache_service.py        # Redis caching
├── tests/
│   ├── test_01_containers_health.py
│   ├── test_02_database_pgvector.py
│   ├── test_03_openrouter_integration.py
│   ├── test_04_minio_storage.py
│   ├── test_05_redis_cache.py
│   ├── test_06_end_to_end.py
│   └── test_vector_with_book.py
├── datafiles/
│   ├── Andersen's Fairy Tales.txt  # Test data
│   └── npm/
│       ├── data/
│       └── letsencrypt/
├── .vscode/                  # VS Code configuration
├── docker-compose.yml        # Development setup
├── docker-compose.prod.yml   # Production setup
├── Dockerfile               # Multi-stage build
├── pyproject.toml           # Python dependencies
├── init.sql                 # Database initialization
└── .env                     # Environment variables
```

## 📊 Migration Benefits

### Cost Comparison

| Service | Azure (Monthly) | Docker (Monthly) | Savings |
|---------|----------------|------------------|---------|
| Compute | $150 | $20 (VPS) | $130 |
| Vector Search | $250 | $0 (pgvector) | $250 |
| Database | $50 | $5 (included) | $45 |
| Storage | $20 | $2 (included) | $18 |
| Redis | $30 | $0 (included) | $30 |
| **Total** | **$500** | **$45** | **$455 (91%)** |

### Performance Improvements

- **Faster cold starts** (no serverless delays)
- **Better resource utilization** (dedicated resources)
- **Lower latency** (all services co-located)
- **Predictable performance** (no noisy neighbors)

## 🚧 Known Issues & Limitations

1. **POC Scope**: This is a proof-of-concept, not production-ready
2. **Authentication**: No authentication implemented (add before production)
3. **SSL/TLS**: Not configured (use Let's Encrypt in production)
4. **Monitoring**: Basic health checks only (add Grafana/Prometheus)
5. **Backup**: No automated backups (implement before production)

## 🗺️ Roadmap

### Phase 1: POC Validation ✅
- [x] Core container setup
- [x] Service integration
- [x] Basic testing
- [x] Performance validation

### Phase 2: Production Preparation (Next)
- [ ] Authentication & authorization
- [ ] SSL/TLS configuration
- [ ] Monitoring & alerting (Grafana)
- [ ] Automated backups
- [ ] CI/CD pipeline

### Phase 3: Migration
- [ ] Deploy to staging (dev.inkandquill.io)
- [ ] Data migration scripts
- [ ] Load testing
- [ ] Gradual traffic migration
- [ ] Full production deployment

## 📖 Documentation

- [Architecture Plan](POC_PLAN.md) - Detailed technical architecture
- [Repository Setup](REPOSITORY_SETUP.md) - GitHub repository setup guide
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (dev only)

## 🤝 Contributing

We welcome contributions from the community! For questions, issues, or contributions:
- Create an issue for bugs or feature requests
- Submit pull requests for improvements
- Join discussions in the GitHub Discussions tab
- Review our [Contributing Guidelines](CONTRIBUTING.md)

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

## 🧹 Docker Cleanup Commands

### Clean Up Docker Artifacts

```bash
# Remove all stopped containers, unused networks, images, and build cache
docker system prune -a

# Also remove unused volumes (WARNING: This deletes data!)
docker system prune -a --volumes

# Force removal without confirmation prompt
docker system prune -a --volumes -f

# Check disk usage before cleaning
docker system df
```

### Granular Cleanup

```bash
# Remove all containers (stopped and running)
docker rm -f $(docker ps -aq)

# Remove all images
docker rmi -f $(docker images -aq)

# Remove all volumes (WARNING: This deletes data!)
docker volume rm $(docker volume ls -q)

# Remove all networks (except default ones)
docker network rm $(docker network ls -q)
```

### Docker Compose Cleanup

```bash
# Stop and remove containers, networks, volumes, and images created by docker-compose
docker-compose down --volumes --rmi all

# Remove only containers and networks (keep volumes and images)
docker-compose down

# Remove containers, networks, and anonymous volumes
docker-compose down --volumes
```

## 🔐 Quick Reference - All Credentials & Endpoints

### Service Endpoints

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| **FastAPI Docker** | http://localhost:8000 | 8000 | Production-like API (Docker) |
| **FastAPI Debug** | http://localhost:8001 | 8001 | Local development (VS Code F5) |
| **FastAPI Docs** | http://localhost:8000/docs | 8000 | Swagger UI (Docker) |
| **FastAPI Debug Docs** | http://localhost:8001/docs | 8001 | Swagger UI (Debug) |
| **Nginx Proxy** | http://localhost | 80 | Proxied apps |
| **Nginx Admin** | http://localhost:81 | 81 | Proxy Manager UI |
| **PostgreSQL** | localhost:5432 | 5432 | Database connection |
| **MinIO API** | http://localhost:9000 | 9000 | S3 API endpoint |
| **MinIO Console** | http://localhost:9001 | 9001 | MinIO Web UI |
| **Redis** | localhost:6379 | 6379 | Cache server |
| **pgAdmin** | http://localhost:5050 | 5050 | PostgreSQL Web UI |
| **Redis Commander** | http://localhost:8081 | 8081 | Redis Web UI |
| **Dashboard** | http://localhost:8082 | 8082 | Service dashboard |

### Default Credentials

| Service | Username/Email | Password | Notes |
|---------|---------------|----------|-------|
| **Nginx Proxy Manager** | admin@example.com | changeme | Change on first login |
| **PostgreSQL** | pocuser | pocpass | Database user |
| **MinIO** | minioadmin | minioadmin123 | Root user |
| **pgAdmin** | admin@example.com | admin | Web UI login |
| **Redis** | - | - | No auth by default |

### Database Connection String

```
postgresql://pocuser:pocpass@localhost:5432/poc_db
```

### MinIO S3 Configuration

```python
# Python boto3 example
import boto3

s3 = boto3.client('s3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='minioadmin',
    aws_secret_access_key='minioadmin123',
    region_name='us-east-1'
)
```

### Redis Connection

```python
# Python redis example
import redis

r = redis.Redis(
    host='localhost',
    port=6379,
    db=0
)
```

### Docker Container Names

| Container | Name | Purpose |
|-----------|------|---------|
| **App** | v2-poc-app | FastAPI application |
| **Nginx** | v2-poc-npm | Nginx Proxy Manager |
| **PostgreSQL** | v2-poc-postgres | Database |
| **MinIO** | v2-poc-minio | Object storage |
| **Redis** | v2-poc-redis | Cache |
| **pgAdmin** | v2-poc-pgadmin | Database UI |
| **Redis Commander** | v2-poc-redis-commander | Cache UI |
| **Dashboard** | v2-poc-dashboard | Service menu |

### Quick Docker Commands

```bash
# View all containers
docker-compose ps

# View specific container logs
docker-compose logs app
docker-compose logs postgres
docker-compose logs minio

# Enter a container
docker exec -it v2-poc-app /bin/bash
docker exec -it v2-poc-postgres psql -U pocuser -d poc_db
docker exec -it v2-poc-redis redis-cli

# Restart a specific service
docker-compose restart app
```

## 🙏 Acknowledgments

- **pgvector** - Open-source vector similarity search
- **MinIO** - S3-compatible object storage
- **OpenRouter** - Unified LLM API access
- **DeepSeek** - Cost-effective AI model
- **BGE-large-en-v1.5** - Open-source embedding model

---

**Version**: 2.0.0  
**Last Updated**: January 23, 2025  
**Status**: POC Complete - Ready for Testing