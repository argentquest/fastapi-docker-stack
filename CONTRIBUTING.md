# Contributing to FastAPI Docker Stack

Thank you for your interest in contributing to the FastAPI Docker Stack! This document provides guidelines and instructions for contributing to the project.

## 🎯 Project Overview

This is a production-ready FastAPI microservices stack designed as a cost-effective alternative to cloud services. The architecture includes:
- FastAPI application with async support
- PostgreSQL with pgvector for vector similarity search
- Redis for caching
- MinIO for S3-compatible object storage
- Nginx as reverse proxy

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
   # Create Python 3.11+ virtual environment
   python3.11 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate    # Windows

   # Install uv and dependencies
   pip install uv
   uv pip install -e .

   # Copy environment template
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start Development Environment**
   ```bash
   # Start all containers
   docker-compose up -d

   # Run tests to ensure everything works
   python run_all_tests.py
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

### Testing Requirements

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test service interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Benchmark critical operations
- **Security Tests**: Validate input handling and security measures

Run tests before submitting:
```bash
# Run all tests
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

When adding new containerized services:

1. **Update docker-compose.yml**
   - Add service configuration
   - Define health checks
   - Set resource limits
   - Configure networks

2. **Create Service Integration**
   - Add service client in `app/services/`
   - Implement health check endpoint
   - Add configuration in `app/core/config.py`
   - Update initialization in `app/main.py`

3. **Add Comprehensive Tests**
   - Service-specific test file
   - Integration with existing tests
   - Update end-to-end test scenarios

4. **Update Documentation**
   - README.md service descriptions
   - Architecture diagrams
   - Configuration examples
   - Docker Compose comments

### Performance Improvements

- Profile before and after changes
- Include benchmark results in PR
- Consider memory and CPU impact
- Test under realistic load conditions

## 🛠️ Development Tools

### Recommended VS Code Extensions

The project includes comprehensive VS Code configuration:
- Python extension pack
- Docker extension
- GitLens for Git integration
- Database tools for PostgreSQL

### Debugging

Use the provided VS Code launch configurations:
- Debug FastAPI application
- Debug individual test files
- Attach to Docker containers

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

Thank you for helping make FastAPI Docker Stack better for everyone! 🎉

---

**Last Updated**: January 23, 2025  
**Version**: 1.0