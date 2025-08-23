# V2 Architecture POC Plan
## Core Container Validation & Testing

**Objective:** Validate the 5 core Docker containers work together as a foundation for the full migration  
**Scope:** Minimal viable implementation to prove architecture concepts  
**Timeline:** 1-2 weeks development + testing  
**Status:** ✅ **IMPLEMENTATION COMPLETE** - Ready for testing  
**Success Criteria:** All 5 containers operational with working AI endpoint  

---

## POC Goals

### Primary Objectives
1. **Prove Container Integration** - All 5 core containers communicate properly
2. **Validate pgvector Performance** - Vector storage and similarity search working
3. **Test OpenRouter Integration** - Existing OpenRouter code works in new architecture
4. **Confirm MinIO Functionality** - S3-compatible storage replaces Azure Blob
5. **Benchmark Basic Performance** - Response times and resource usage

### Secondary Objectives
- Test uv package management in containerized environment
- Validate Docker Compose orchestration
- Confirm Nginx reverse proxy configuration
- Test basic monitoring/logging capabilities

---

## Architecture Under Test

### 5 Core Containers
```
┌─────────────────────────────────────────┐
│              V2 POC Stack               │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐    ┌─────────────────┐ │
│  │   Nginx     │    │   FastAPI App   │ │
│  │ (Proxy/SSL) │◄──►│  + BGE-large    │ │
│  │             │    │  + OpenRouter   │ │
│  └─────────────┘    └─────────────────┘ │
│         │                    │          │
│         ▼                    ▼          │
│  ┌─────────────┐    ┌─────────────────┐ │
│  │    MinIO    │    │  PostgreSQL     │ │
│  │(S3 Storage) │    │  + pgvector     │ │
│  │             │    │                 │ │
│  └─────────────┘    └─────────────────┘ │
│                             │          │
│                    ┌─────────────────┐ │
│                    │     Redis       │ │
│                    │   (Caching)     │ │
│                    │                 │ │
│                    └─────────────────┘ │
└─────────────────────────────────────────┘
```

---

## Minimal Code Requirements

### Services to Copy from Main Project
1. **OpenRouter Client** (`app/services/openrouter_service.py`)
   - Copy existing integration
   - Minimal modifications for V2 environment
   
2. **Configuration Management** (`app/core/config.py`)  
   - Environment variable handling
   - Database connection strings
   - API keys management

3. **Database Connection Patterns** (`app/db/database.py`)
   - AsyncPG connection logic
   - Connection pooling setup

### New Services to Implement
4. **BGE-large Embedding Service** (`app/services/embedding_service.py`)
   - Replace Azure OpenAI embeddings
   - Local sentence-transformers integration
   - Vector generation for pgvector

5. **MinIO Storage Client** (`app/services/storage_service.py`)
   - S3-compatible file operations
   - Replace Azure Blob patterns
   - Simple upload/download functionality

---

## Single Table Schema

```sql
-- POC database schema (init.sql)
CREATE EXTENSION IF NOT EXISTS vector;

-- Simple logging table for POC testing
CREATE TABLE ai_test_logs (
    id SERIAL PRIMARY KEY,
    system_prompt TEXT NOT NULL,
    user_context TEXT NOT NULL,
    ai_result TEXT NOT NULL,
    embedding vector(1024),  -- BGE-large embeddings (1024 dimensions)
    file_url TEXT,           -- MinIO storage URL
    response_time_ms INTEGER, -- Performance tracking
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for vector similarity search
CREATE INDEX ON ai_test_logs USING ivfflat (embedding vector_cosine_ops);
```

---

## Single Test Endpoint

### FastAPI Endpoint Specification

```python
@app.post("/ai-test")
async def ai_test_endpoint(
    system_prompt: str,
    user_context: str
) -> dict:
    """
    POC endpoint that tests all 5 core containers:
    1. Receives system prompt + user context
    2. Calls OpenRouter API (existing integration)
    3. Generates embedding with BGE-large (new)
    4. Stores result in PostgreSQL + pgvector (new)
    5. Saves response file to MinIO (new)  
    6. Caches result in Redis (new)
    7. Returns response with performance metrics
    """
```

### Expected Response Format
```json
{
  "id": 1,
  "ai_result": "Generated response text...",
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

---

## Container Configuration

### Docker Compose Services

```yaml
version: '3.8'
services:
  # 1. Custom FastAPI application
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DATABASE_URL=postgresql://pocuser:pocpass@postgres:5432/poc_db
    depends_on:
      - postgres
      - redis  
      - minio

  # 2. Nginx reverse proxy
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app

  # 3. PostgreSQL + pgvector
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_USER=pocuser
      - POSTGRES_PASSWORD=pocpass
      - POSTGRES_DB=poc_db
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # 4. MinIO S3-compatible storage
  minio:
    image: minio/minio:RELEASE.2024-12-13T22-06-12Z
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    ports:
      - "9001:9001"  # Admin console
    command: server /data --console-address ":9001"

  # 5. Redis caching
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
```

---

## Testing Strategy

### Automated Tests

#### 1. Container Health Checks
```bash
# Test all containers are running
docker-compose ps

# Verify service health endpoints
curl http://localhost/health
```

#### 2. Database Connectivity
```bash
# Test PostgreSQL + pgvector
curl -X POST http://localhost/ai-test \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "Test", "user_context": "Hello world"}'

# Verify data in database  
docker exec postgres psql -U pocuser -d poc_db \
  -c "SELECT COUNT(*) FROM ai_test_logs;"
```

#### 3. Vector Search Functionality
```bash
# Test embedding similarity search
curl http://localhost/similar-logs?query="Hello world"
```

#### 4. Storage Integration
```bash
# Verify MinIO file creation
curl http://localhost:9001  # Check admin console
```

#### 5. Performance Benchmarks
```bash
# Test response times
for i in {1..10}; do
  time curl -X POST http://localhost/ai-test \
    -H "Content-Type: application/json" \
    -d "{\"system_prompt\": \"Test $i\", \"user_context\": \"Benchmark test $i\"}"
done
```

### Manual Validation

#### MinIO Console Testing
- Access: http://localhost:9001 (minioadmin/minioadmin123)
- Verify bucket creation
- Check file uploads
- Test file downloads

#### Database Inspection
```sql
-- Connect to database
docker exec -it postgres psql -U pocuser -d poc_db

-- Check data and embeddings
SELECT id, system_prompt, LENGTH(ai_result), embedding <-> embedding as self_similarity 
FROM ai_test_logs 
LIMIT 5;

-- Test vector search
SELECT id, system_prompt, 1 - (embedding <=> (SELECT embedding FROM ai_test_logs WHERE id = 1)) as similarity
FROM ai_test_logs 
WHERE id != 1
ORDER BY embedding <=> (SELECT embedding FROM ai_test_logs WHERE id = 1)
LIMIT 3;
```

---

## Success Metrics

### Technical Validation
- [x] **All 5 containers configured** (docker-compose.yml + docker-compose.prod.yml)
- [x] **Nginx routes requests properly** (nginx.conf configured)
- [x] **PostgreSQL with pgvector** (init.sql with vector extension)
- [x] **pgvector 1024 dimensions** (BGE-large-en-v1.5 support)
- [x] **OpenRouter integration** (DeepSeek R1 configured)
- [x] **BGE-large embeddings service** (sentence-transformers ready)
- [x] **MinIO S3 storage client** (minio-py integration)
- [x] **Redis caching service** (redis-py configured)

### Security Validation ✅ NEW
- [x] **Input validation implemented** (Pydantic validators)
- [x] **SQL injection prevention** (parameterized queries)
- [x] **Error handling secured** (sanitized responses)
- [x] **Container security hardened** (non-root, read-only)
- [x] **Network isolation configured** (internal Docker networks)
- [x] **Resource limits applied** (memory and CPU constraints)
- [x] **Environment validation** (configuration validators)

### Performance Baselines
- [ ] **Response time < 5 seconds** (AI endpoint)
- [ ] **Vector search < 100ms** (Similarity queries)
- [ ] **File upload < 1 second** (MinIO operations)
- [ ] **Memory usage < 4GB total** (All containers combined)
- [ ] **CPU usage < 50%** (Under normal load)

### Integration Validation
- [ ] **End-to-end flow works** (Request → AI → Storage → Response)
- [ ] **Data persistence verified** (Restart containers, data remains)
- [ ] **Error handling functional** (Graceful failure modes)
- [ ] **Service dependencies working** (Containers communicate properly)

---

## Resource Requirements

### Development Environment
- **Docker Desktop** with WSL2 support
- **VS Code** with Docker extension
- **uv** package manager
- **16GB RAM recommended** (8GB minimum)
- **20GB free disk space** (containers + data)

### Runtime Resource Usage
```
Container Resource Allocation:
- FastAPI App:     512MB RAM, 0.5 CPU
- PostgreSQL:      1GB RAM,   0.3 CPU  
- Nginx:           128MB RAM, 0.1 CPU
- MinIO:           256MB RAM, 0.2 CPU
- Redis:           128MB RAM, 0.1 CPU
─────────────────────────────────────
Total Estimated:   2GB RAM,  1.2 CPU
```

---

## Risk Mitigation

### Potential Issues & Solutions

#### 1. Container Communication Problems
- **Risk:** Services can't connect to each other
- **Mitigation:** Use docker-compose service names as hostnames
- **Test:** Verify with `docker-compose logs` and `docker exec` debugging

#### 2. pgvector Performance Issues  
- **Risk:** Vector operations too slow compared to Azure AI Search
- **Mitigation:** Proper indexing configuration, benchmark against requirements
- **Test:** Measure similarity search times with realistic data volumes

#### 3. OpenRouter Integration Failures
- **Risk:** Existing OpenRouter code doesn't work in containerized environment
- **Mitigation:** Copy exact working code, maintain same environment variables
- **Test:** Verify API calls work with existing API keys

#### 4. MinIO S3 Compatibility Issues
- **Risk:** S3-compatible operations don't match Azure Blob patterns
- **Mitigation:** Use standard boto3/minio-py libraries, test common operations
- **Test:** Upload, download, delete, list operations

#### 5. Resource Constraints
- **Risk:** Containers consume too much memory/CPU
- **Mitigation:** Monitor resource usage, optimize container configurations
- **Test:** Run extended load testing, monitor with docker stats

---

## Implementation Status

### ✅ Completed Components

#### Core Application
- **FastAPI Application** (`app/main.py`)
  - `/ai-test` endpoint for comprehensive testing
  - Health check endpoint at `/health`
  - Full integration with all 5 containers

#### Services Implemented
- **OpenRouter Service** (`app/services/openrouter_service.py`)
  - DeepSeek R1 model integration
  - Streaming support for real-time responses
  - Error handling and retry logic

- **Embedding Service** (`app/services/embedding_service.py`)
  - BGE-large-en-v1.5 model (1024 dimensions)
  - Batch embedding generation
  - Compatible with pgvector storage

- **Database Service** (`app/services/database_service.py`)
  - AsyncPG connection pooling
  - pgvector operations for similarity search
  - Automatic table creation and indexing

- **Storage Service** (`app/services/storage_service.py`)
  - MinIO S3-compatible operations
  - File upload/download/delete
  - Bucket management

- **Cache Service** (`app/services/cache_service.py`)
  - Redis connection management
  - Key-value operations with TTL
  - JSON serialization support

#### Docker Configuration
- **Multi-stage Dockerfile** with uv package manager
- **docker-compose.yml** with all 5 containers
- **Health checks** for all services
- **Volume persistence** for data
- **Network isolation** with service discovery

#### Database Schema
- **PostgreSQL with pgvector extension**
- **ai_test_logs table** with vector embeddings
- **book_chunks table** for document storage
- **IVFFlat indexes** for fast similarity search

#### Testing Suite
- **7 comprehensive test scripts**:
  1. Container health validation
  2. PostgreSQL + pgvector operations
  3. OpenRouter API integration
  4. MinIO storage operations
  5. Redis cache functionality
  6. End-to-end integration
  7. Vector operations with book content

- **Test data**: Andersen's Fairy Tales (500KB+)
- **Automated test runner** (`run_all_tests.py`)

#### Configuration
- **Environment variables** in `.env`
- **Python 3.11** requirement
- **uv package manager** setup
- **pyproject.toml** with all dependencies

### 🔄 Ready for Testing
- All code implemented and ready
- Comprehensive test suite available
- Documentation complete
- VS Code configuration ready

---

## Security Improvements (v3.0)

### 🔒 Implemented Security Fixes

#### Input Validation & Sanitization
- ✅ Added Pydantic field validators with min/max length constraints
- ✅ Implemented input sanitization to prevent injection attacks
- ✅ Added regex-based cleaning of potentially harmful characters
- ✅ Proper error message sanitization (no internal details exposed)

#### SQL Injection Prevention
- ✅ Fixed SQL injection vulnerability in `database_service.py`
- ✅ All queries now use parameterized statements
- ✅ No string concatenation in SQL queries

#### Configuration Security
- ✅ Added validators for critical environment variables
- ✅ Database URL format validation
- ✅ API key validation (no placeholder values)
- ✅ Configurable connection pool settings

#### Error Handling
- ✅ Differentiated error responses by type (400, 500, 503)
- ✅ No internal error details exposed to clients
- ✅ Proper logging with exc_info for debugging
- ✅ HTTP exception re-raising to preserve status codes

#### Docker Security (docker-compose.prod.yml)
- ✅ Security options: `no-new-privileges:true`
- ✅ Read-only root filesystems with tmpfs for writable areas
- ✅ Resource limits and reservations for all containers
- ✅ Non-root user execution
- ✅ Internal-only network isolation
- ✅ Removed unnecessary port exposures
- ✅ Environment-based secrets management

#### Additional Security Configurations
- ✅ Rate limiting configuration added
- ✅ CORS settings for development only
- ✅ API documentation disabled in production
- ✅ Redis password support
- ✅ Configurable allowed origins

### ⚠️ Security Tasks for Production

Before deploying to production, implement:

1. **Authentication & Authorization**
   - JWT or API key authentication
   - Role-based access control
   - Session management

2. **SSL/TLS Configuration**
   - Let's Encrypt certificates
   - Nginx SSL configuration
   - HTTPS enforcement

3. **Secrets Management**
   - External secrets store (Vault, AWS Secrets Manager)
   - Docker Swarm secrets or Kubernetes secrets
   - Encrypted environment variables

4. **Monitoring & Alerting**
   - Security event logging
   - Intrusion detection
   - Rate limiting enforcement
   - Anomaly detection

5. **Backup & Recovery**
   - Automated encrypted backups
   - Disaster recovery plan
   - Data retention policies

---

## Next Steps After POC Success

### If POC Validates Successfully
1. **Update main MIGRATION_PLAN.md** with confirmed timelines and approaches
2. **Begin Phase 1 implementation** using proven V2 patterns  
3. **Set up dev.inkandquill.io** staging environment
4. **Add monitoring containers** (Grafana/Prometheus)
5. **Implement n8n automation** workflows

### If POC Reveals Issues
1. **Document specific problems** and performance gaps
2. **Adjust architecture** based on findings
3. **Consider hybrid approaches** (keep some Azure services temporarily)
4. **Revise migration timeline** based on complexity discovered

---

## Development Workflow

### Setup Commands
```bash
# Navigate to V2 directory
cd C:\Code2025\rag\V2

# Create Python 3.11 virtual environment
python3.11 -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install uv and dependencies
pip install uv
uv pip install -e .

# Environment configuration
# .env file already configured with:
# - OpenRouter API key
# - DeepSeek R1 as default model
# - All container configurations

# Build and start containers
docker-compose up --build -d

# Run comprehensive test suite
python run_all_tests.py

# Or run individual tests:
python tests/test_01_containers_health.py
python tests/test_02_database_pgvector.py
python tests/test_03_openrouter_integration.py
python tests/test_04_minio_storage.py
python tests/test_05_redis_cache.py
python tests/test_06_end_to_end.py
python tests/test_vector_with_book.py  # Test with Andersen's Fairy Tales
```

### Iterative Development
1. **Day 1-2:** Set up basic containers and connectivity
2. **Day 3-4:** Implement core AI endpoint with logging  
3. **Day 5-6:** Add pgvector integration and testing
4. **Day 7-8:** Complete MinIO and Redis integration
5. **Day 9-10:** Performance testing and optimization
6. **Day 11-12:** Documentation and validation

---

## Conclusion

This POC provides a focused, minimal-risk approach to validating the core V2 architecture. Success here proves the feasibility of the full migration plan while identifying any architectural issues early in the process.

The self-contained nature ensures no disruption to the existing Azure production system, while reusing proven OpenRouter integration reduces implementation risk.

**Expected Outcome:** A working proof-of-concept that demonstrates 90% cost savings potential with maintained functionality and acceptable performance.

---

**Document Version:** 3.0  
**Created:** 2025-01-23  
**Updated:** 2025-01-23 (Security hardening and comprehensive review completed)  
**Next Review:** After production deployment planning