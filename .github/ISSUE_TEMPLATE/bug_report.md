---
name: Bug report
about: Create a report to help us improve the Argentquest Development Suite
title: '[BUG] '
labels: 'bug'
assignees: ''
---

## 🐛 Bug Description

**What happened?**
A clear and concise description of what the bug is.

**What did you expect to happen?**
A clear description of what you expected to happen instead.

## 🖥️ Environment Information

**Operating System:** 
- [ ] Windows 11
- [ ] Windows 10  
- [ ] macOS (version: )
- [ ] Ubuntu/Linux (version: )
- [ ] Other: 

**Docker Information:**
- Docker version: (run `docker --version`)
- Docker Compose version: (run `docker-compose --version`)
- Available RAM: 
- Available disk space:

**Browser (if applicable):**
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Other:

## 📝 Steps to Reproduce

Please provide detailed steps to reproduce the issue:

1. Go to '...'
2. Click on '...'
3. Run command '...'
4. See error

## 🔍 Additional Information

**Container Status:**
```bash
# Please paste the output of:
docker-compose ps
```

**Container Logs (if relevant):**
```bash
# Please paste relevant logs from:
docker-compose logs [service-name]
```

**Error Messages:**
```
Paste any error messages here
```

**Screenshots:**
If applicable, add screenshots to help explain your problem.

## 🔧 What I've Tried

- [ ] Restarted containers (`docker-compose restart`)
- [ ] Rebuilt containers (`docker-compose up -d --build`)
- [ ] Ran health check (`python health-check.py`)
- [ ] Checked documentation
- [ ] Searched existing issues

## 📱 Impact

**How critical is this issue?**
- [ ] Blocking - Cannot use the system
- [ ] High - Major feature not working
- [ ] Medium - Minor feature issue
- [ ] Low - Cosmetic or documentation issue

**Which services are affected?**
- [ ] FastAPI applications (app-dev/app-prod)
- [ ] PostgreSQL database
- [ ] MongoDB database
- [ ] Redis cache
- [ ] MinIO storage
- [ ] Monitoring services
- [ ] Proxy/networking
- [ ] Documentation
- [ ] Setup process

## 🤝 Additional Context

Add any other context about the problem here. Include:
- When did this issue start occurring?
- Does it happen consistently or intermittently?
- Any recent changes to your setup?
- Any workarounds you've found?

---

**Thanks for helping improve the Argentquest Development Suite! 🚀**

*New to contributing? Check out our [Contributing Guide](../CONTRIBUTING.md) and look for [good first issues](https://github.com/argentquest/fastapi-docker-stack/labels/good%20first%20issue).*