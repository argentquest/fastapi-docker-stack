# Pull Request

## 📝 Description

<!-- Provide a brief description of the changes in this PR -->

## 🔗 Related Issues

<!-- Link to related issues using keywords: Fixes #123, Closes #456, Relates to #789 -->

## 🎯 Type of Change

<!-- Mark the type of change with an [x] -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] 🧪 Tests (adding or updating tests)
- [ ] 🏗️ Infrastructure (Docker, CI/CD, configuration)
- [ ] 🔒 Security improvement
- [ ] ⚡ Performance improvement

## 🧪 Testing

<!-- Describe the tests you ran to verify your changes -->

### Test Cases
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

### Test Commands
```bash
# Commands you used to test this change
python run_all_tests.py
# OR specific tests:
python tests/test_[specific_test].py
```

### Test Results
<!-- Paste relevant test output or screenshots -->

```
# Test output here
```

## 📋 Checklist

### Code Quality
- [ ] Code follows project style guidelines (Black, Flake8)
- [ ] Self-review of code completed
- [ ] Code is commented appropriately
- [ ] Type hints added where applicable

### Documentation
- [ ] Docstrings updated for new/modified functions
- [ ] README.md updated if needed
- [ ] API documentation updated if applicable
- [ ] CHANGELOG updated if needed

### Security
- [ ] No sensitive information exposed
- [ ] Input validation implemented where needed
- [ ] Security best practices followed
- [ ] No new security vulnerabilities introduced

### Performance
- [ ] Performance impact considered
- [ ] No significant performance regression
- [ ] Resource usage optimized

### Docker & Infrastructure
- [ ] Docker containers build successfully
- [ ] Docker Compose configurations updated if needed
- [ ] Health checks working properly
- [ ] Environment variables documented

## 🔄 Migration Guide

<!-- If this is a breaking change, provide migration instructions -->

### For Users Upgrading

```bash
# Steps users need to take to upgrade
```

### Configuration Changes

```yaml
# Any configuration file changes needed
```

## 📊 Performance Impact

<!-- If applicable, describe performance implications -->

### Benchmarks

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Response Time | - | - | - |
| Memory Usage | - | - | - |
| CPU Usage | - | - | - |

## 🖼️ Screenshots

<!-- Add screenshots for UI changes or visual improvements -->

## 📚 Additional Notes

<!-- Any additional information that reviewers should know -->

### Reviewer Notes
<!-- Specific areas you'd like reviewers to focus on -->

### Future Improvements
<!-- Ideas for follow-up PRs or improvements -->

---

## 🎯 Definition of Done

- [ ] Code review completed and approved
- [ ] All CI/CD checks pass
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Security review completed (if applicable)
- [ ] Performance reviewed (if applicable)
- [ ] Breaking changes communicated (if applicable)