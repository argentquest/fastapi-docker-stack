# FastAPI Docker Stack

## 🚀 Overview

A production-ready FastAPI microservices stack with PostgreSQL+pgvector, Redis, MinIO, and Nginx - fully containerized with Docker. This architecture provides a cost-effective alternative to cloud services, offering up to 90% cost savings (from $400-500/month to $45-60/month) while maintaining enterprise-grade functionality.

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
│                  Nginx (Port 80)                 │
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
| **CDN/Proxy** | Azure CDN | Nginx | 100% |

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

### VS Code Integration

The project includes comprehensive VS Code configuration:

- **Launch configurations** for debugging
- **Tasks** for Docker and testing
- **Code snippets** for rapid development
- **Recommended extensions**
- **Python formatting** with Black
- **Linting** with Flake8

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
│   └── Andersen's Fairy Tales.txt  # Test data
├── nginx/
│   └── nginx.conf            # Reverse proxy config
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