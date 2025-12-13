# Contributing to Argentquest Development Suite

Thank you for your interest in contributing to the Argentquest Development Suite! This document provides guidelines and instructions for contributing to the project.

## 🎯 Project Overview

This is a **comprehensive 22-container development environment** designed as a cost-effective alternative to cloud services, providing enterprise-grade functionality with 90% cost savings. The architecture includes:

### Core Application Services
- **Dual FastAPI environments**: Production (`app-prod`) and development (`app-dev`) containers
- **Three environment configurations**: `.env`, `.env.dev`, `.env.prod` for flexible deployment

### Database Services
- **PostgreSQL 16** with pgvector extension for vector similarity search
- **MongoDB 7.0** for NoSQL document storage
- **Redis 7.2** for caching and session storage

### Management Tools
- **pgAdmin** for PostgreSQL management (pre-configured)
- **Mongo Express** for MongoDB management
- **Redis Commander** for Redis management
- **Portainer** for Docker container management

### Development Tools
- **VS Code Server** for browser-based development
- **MCP Inspector** for Model Context Protocol testing
- **Jupyter Lab** for data science workflows
- **n8n** for workflow automation

### Infrastructure Services
- **MinIO** for S3-compatible object storage
- **Nginx Proxy Manager** for reverse proxy and SSL
- **Beszel + Agent** for comprehensive monitoring
- **System Monitor** for real-time container stats
- **Heimdall** as application dashboard

**Important Note**: This system is designed for **development and proof-of-concept use only** and is not production-ready without significant security hardening.

## 🤝 How to Contribute

### Types of Contributions We Welcome

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new functionality
- 📖 **Documentation**: Improve guides, examples, and API docs
- 🔧 **Code Contributions**: Fix bugs, add features, improve performance
- 🧪 **Testing**: Add test cases, improve test coverage
- 🏗️ **Architecture**: Suggest architectural improvements
- 🔒 **Security**: Report security vulnerabilities or improvements

### Getting Started

1. **Fork the Repository**
   ```bash
   git fork https://github.com/[username]/fastapi-docker-stack
   cd fastapi-docker-stack
   ```

2. **Set Up Development Environment**
   ```bash
   # Create Python 3.13+ virtual environment
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate    # Windows

   # Install uv and dependencies
   pip install uv
   uv pip install -e .

   # Copy environment template and configure
   cp .env.template .env
   # Edit .env with your OpenRouter API key and other settings
   
   # Environment files overview:
   # .env      - Main configuration for local development
   # .env.dev  - Development container settings (debug mode)
   # .env.prod - Production container settings (performance mode)
   ```

3. **Start Development Environment**
   ```bash
   # Start all 22 containers
   docker-compose up -d

   # Wait for initialization (2-3 minutes for first startup)
   sleep 180

   # Set up NPM proxy hosts (for domain-based access)
   python scripts/npm-simple-setup.py

   # Validate deployment
   python health-check.py
   ./validate-database-setup.sh
   ```

4. **Configure Domain Access (Important!)**
   
   Add these entries to your hosts file for proper access:
   
   **Windows (Run as Administrator):**
   ```cmd
   notepad C:\Windows\System32\drivers\etc\hosts
   ```
   
   **Linux/macOS:**
   ```bash
   sudo nano /etc/hosts
   ```
   
   **Add these lines (use 127.0.0.1 for local development):**
   ```
   127.0.0.1    pocmaster.argentquest.com
   127.0.0.1    api.pocmaster.argentquest.com
   127.0.0.1    api-dev.pocmaster.argentquest.com
   127.0.0.1    pgadmin.pocmaster.argentquest.com
   127.0.0.1    portainer.pocmaster.argentquest.com
   127.0.0.1    heimdall.pocmaster.argentquest.com
   ```

## 📝 Development Guidelines

### Code Style

- **Python**: Follow PEP 8, use Black formatter (120 char line length)
- **Type Hints**: Use comprehensive type annotations
- **Docstrings**: Document all functions, classes, and modules
- **Async/Await**: Use proper async patterns throughout

### Code Quality Standards

1. **Linting**: Code must pass Flake8 with project configuration
2. **Type Checking**: Code must pass mypy type checking
3. **Testing**: New features must include comprehensive tests
4. **Security**: Follow security best practices (input validation, etc.)
5. **Performance**: Consider performance implications of changes

### Development Workflow

#### **Hot-Reload Development**
The `app-dev` container provides hot-reload functionality:
- Edit code in the `./app/` directory on your host machine
- Changes are automatically detected and applied (via volume mount)
- Test your changes at `http://api-dev.pocmaster.argentquest.com`
- Development logs are available with debug detail

#### **Environment-Specific Testing** 
Test your changes in different environments:
```bash
# Test development environment (single worker, debug logging)
curl http://api-dev.pocmaster.argentquest.com/health

# Test production environment (multiple workers, performance)  
curl http://api.pocmaster.argentquest.com/health

# Compare database connections
docker exec aq-devsuite-app-dev env | grep DATABASE_URL
docker exec aq-devsuite-app-prod env | grep DATABASE_URL
```

#### **Database Development**
Both databases come with comprehensive test data:
- **PostgreSQL**: Users, stories, world elements, AI test logs
- **MongoDB**: User profiles, documents, world building, AI conversations

Access databases for testing:
```bash
# PostgreSQL via pgAdmin: http://localhost:5050 (admin@example.com/admin)
# MongoDB via Mongo Express: Available via NPM proxy

# Direct database access
docker exec -it aq-devsuite-postgres psql -U pocuser -d poc_db
docker exec -it aq-devsuite-mongodb mongosh -u mongoadmin -p mongopass123 --authenticationDatabase admin
```

### Testing Requirements

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service interactions with actual databases
- **End-to-End Tests**: Test complete workflows across environments
- **Container Health Tests**: Validate all 22 containers
- **Database Tests**: Test PostgreSQL (with pgvector) and MongoDB functionality
- **Security Tests**: Validate input handling and security measures (**Note: System has known vulnerabilities by design**)

Run tests before submitting:
```bash
# Run comprehensive health check (22 containers)
python health-check.py

# Validate database setup and test data
./validate-database-setup.sh

# Run all automated tests
python run_all_tests.py

# Run specific test categories
python tests/test_01_containers_health.py
python tests/test_02_database_pgvector.py
python tests/test_03_openrouter_integration.py
python tests/test_04_minio_storage.py
python tests/test_05_redis_cache.py
python tests/test_06_end_to_end.py
```

### Docker Guidelines

- **Multi-stage builds**: Use efficient Docker builds
- **Security**: Follow Docker security best practices
- **Resource limits**: Define appropriate resource constraints
- **Health checks**: Include proper health check endpoints

## 🔄 Pull Request Process

### Before Submitting

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make Your Changes**
   - Follow coding standards
   - Add/update tests
   - Update documentation
   - Ensure all tests pass

3. **Commit Guidelines**
   ```bash
   # Use conventional commit format
   git commit -m "feat: add vector similarity search caching"
   git commit -m "fix: resolve SQL injection vulnerability"
   git commit -m "docs: update API documentation"
   git commit -m "test: add comprehensive MinIO integration tests"
   ```

### Commit Message Format

Use [Conventional Commits](https://conventionalcommits.org/) format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code formatting (no logic changes)
- `refactor`: Code restructuring (no feature changes)
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Submitting the Pull Request

1. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**
   - Use the provided PR template
   - Provide clear description of changes
   - Reference related issues
   - Include screenshots for UI changes
   - Add breaking change notes if applicable

3. **PR Review Process**
   - Automated tests must pass
   - Code review by maintainers
   - Address feedback and requested changes
   - Final approval and merge

## 📋 Issue Guidelines

### Bug Reports

Include the following information:
- **Environment**: OS, Python version, Docker version
- **Steps to reproduce**: Clear, numbered steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error logs**: Relevant log outputs
- **Configuration**: Relevant environment variables (redact secrets)

### Feature Requests

Please provide:
- **Problem description**: What issue are you trying to solve?
- **Proposed solution**: How would you like it to work?
- **Alternatives considered**: Other approaches you've thought about
- **Additional context**: Any other relevant information

### Security Vulnerabilities

**DO NOT** create public issues for security vulnerabilities. Instead:
1. Email security concerns to: [security-email]
2. Include detailed description and reproduction steps
3. Allow time for assessment and patching before disclosure

## 🏗️ Architecture Contributions

### Adding New Services

When adding new containerized services to the 22-container stack:

1. **Update docker-compose.yml**
   - Add service configuration with proper naming (`aq-devsuite-*`)
   - Define health checks and dependencies
   - Set resource limits and security settings
   - Configure networks (`v2_network`)
   - Add to appropriate environment files if needed

2. **Create Service Integration**
   - Add service client in `app/services/`
   - Implement health check endpoint
   - Add configuration to environment files (`.env`, `.env.dev`, `.env.prod`)
   - Update initialization in `app/main.py`
   - Consider dual-environment support (dev/prod containers)

3. **Add Management and Monitoring**
   - Update NPM proxy setup script (`scripts/npm-simple-setup.py`)
   - Add monitoring to Beszel configuration
   - Include in system monitor dashboard
   - Update Heimdall dashboard links

4. **Add Comprehensive Tests**
   - Service-specific test file
   - Update health check tests (`test_01_containers_health.py`)
   - Integration with existing test scenarios
   - Update container count expectations (currently 22)

5. **Update Documentation**
   - README.md service descriptions and architecture section
   - Update container count and service directory
   - Architecture diagrams and flow charts
   - Configuration examples and credentials reference
   - Docker Compose comments and service descriptions

### Environment Configuration Changes

When modifying environment configurations:

1. **Update All Environment Files**
   - `.env` - Local development configuration
   - `.env.dev` - Development container settings
   - `.env.prod` - Production container settings
   - Maintain consistency across environments

2. **Database Connection Updates**
   - Use Docker container names for internal communication
   - Document localhost access for external tools
   - Update validation scripts accordingly

3. **Security Considerations**
   - Remember this is a development system with known vulnerabilities
   - Document any new security implications
   - Update SECURITY.md if introducing new services with default credentials

### Performance Improvements

- Profile before and after changes
- Include benchmark results in PR
- Consider memory and CPU impact
- Test under realistic load conditions

## 🛠️ Development Tools

### Recommended VS Code Extensions

The project includes comprehensive VS Code configuration:
- **Python extension pack** for FastAPI development
- **Docker extension** for container management
- **GitLens** for Git integration
- **Database tools** for PostgreSQL and MongoDB

### Development Environment Access

#### **Browser-Based Development**
- **VS Code Server**: http://code.pocmaster.argentquest.com (password: `dev123`)
- **Jupyter Lab**: http://jupyter.pocmaster.argentquest.com (password: `changeme`)
- **n8n Workflows**: http://n8n.pocmaster.argentquest.com (for automation testing)

#### **Database Management**
- **pgAdmin**: http://localhost:5050 (`admin@example.com` / `admin`)  
- **Mongo Express**: Available via NPM proxy (`admin` / `admin`)
- **Redis Commander**: Available via NPM proxy

#### **System Monitoring**
- **System Monitor**: http://pocmaster.argentquest.com (real-time container stats)
- **Beszel Monitoring**: http://beszel.pocmaster.argentquest.com (`admin@example.com` / `changeme`)
- **Portainer**: http://localhost:9443 (Docker management)
- **NPM Admin**: http://localhost:81 (`admin@example.com` / `changeme`)

### Debugging

#### **Local Debugging**
Use VS Code launch configurations for:
- Debug FastAPI application with hot-reload
- Debug individual test files
- Attach to running Docker containers

#### **Container Debugging**
```bash
# View container logs
docker-compose logs -f app-dev
docker-compose logs -f app-prod

# Access container shell
docker exec -it aq-devsuite-app-dev bash
docker exec -it aq-devsuite-postgres psql -U pocuser -d poc_db

# Monitor container resources
docker stats
```

#### **Environment-Specific Debugging**
```bash
# Compare environment configurations
cat .env | grep DATABASE_URL
cat .env.dev | grep DATABASE_URL  
cat .env.prod | grep DATABASE_URL

# Test environment-specific features
curl http://api-dev.pocmaster.argentquest.com/docs   # Development API docs
curl http://api.pocmaster.argentquest.com/docs       # Production API docs
```

### Local Testing

```bash
# Format code
black app/ tests/ --line-length 120

# Lint code
flake8 app/ tests/ --max-line-length=120 --ignore=E203,W503

# Type check
mypy app/

# Run security checks (if available)
bandit -r app/
```

## 📚 Documentation

### When to Update Documentation

- New features or API changes
- Configuration changes
- Architecture modifications
- New deployment options
- Performance improvements

### Documentation Standards

- **Clear Examples**: Provide working code examples
- **Step-by-Step**: Break down complex procedures
- **Screenshots**: Include for UI-related changes
- **API Documentation**: Update OpenAPI/Swagger docs

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Change log updated
- [ ] Version bumped in appropriate files
- [ ] Security review completed
- [ ] Performance regression testing

## ❓ Getting Help

### Community Support

- **GitHub Discussions**: General questions and discussions
- **Issues**: Bug reports and feature requests
- **Documentation**: Check README and docs/ folder

### Development Questions

For development-related questions:
1. Check existing issues and discussions
2. Review documentation thoroughly
3. Search for similar problems online
4. Create a detailed issue with context

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page
- Special recognition for significant contributions

## 🚨 Important Contribution Notes

### Security Awareness
**Remember**: This is a development system with known security vulnerabilities:
- Default credentials throughout the system
- No authentication on API endpoints  
- Development configurations not suitable for production
- Always review SECURITY.md before contributing security-related changes

### Environment Consistency
When contributing:
- Test changes in both `app-dev` and `app-prod` environments
- Ensure database connections work with Docker network names
- Validate that all 22 containers remain healthy
- Update environment files consistently

### Documentation Priority
Given the complexity of the 22-container system:
- Always update documentation for architectural changes
- Include clear examples and step-by-step instructions
- Update service counts and URLs in multiple documentation files
- Test documentation steps on a fresh environment

Thank you for helping make the Argentquest Development Suite better for everyone! 🎉

---

**Last Updated**: August 31, 2025  
**Version**: 2.0  
**Project**: Argentquest Development Suite (22 containers)  
**Status**: Development/POC Environment