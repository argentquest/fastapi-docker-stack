# VS Code Development and Deployment Guide

This document outlines the recommended workflow for developing and deploying code using VS Code within the Argentquest Development Suite architecture. The stack uses three environment files (`.env`, `.env.dev`, `.env.prod`) for flexible development and deployment scenarios.

## 1. Local Development Workflow (Hot-Reloading for Dev API)

For local development, you will work directly on your machine, and changes will be instantly reflected in the `app-dev` container thanks to hot-reloading and Docker volume mounts.

### 1.1 Environment Configuration Setup

Before starting development, ensure your environment files are properly configured:

1. **Main Configuration (`.env`)**: Used for local development apps
   - Database connections use Docker network names (`postgres:5432`, `mongodb:27017`)
   - Configured for Docker internal communication

2. **Development Container (`.env.dev`)**: Used by `app-dev` container
   - Debug logging, hot reload enabled
   - Single worker for easier debugging
   - Relaxed security settings

3. **Production Container (`.env.prod`)**: Used by `app-prod` container
   - Multiple workers, performance optimized
   - Strict security and logging settings

### 1.2 Start Your Local Development Environment

1.  Open your terminal or command prompt.
2.  Navigate to the root directory of your `argentquest-suite` project.
3.  Ensure your `.env` file is configured (copy from `.env.template` if needed):
    ```bash
    cp .env.template .env
    # Edit .env with your API keys and settings
    ```
4.  Start the Docker containers for your development environment:
    ```bash
    docker-compose up -d
    ```
    This command starts all 22 services including dual FastAPI containers (`app-dev` and `app-prod`).

5.  Validate your setup:
    ```bash
    ./validate-database-setup.sh
    ```

### 1.3 Make Code Changes in VS Code

1.  Open the `argentquest-suite` project folder in VS Code.
2.  Navigate to the `app` directory (e.g., `app/main.py`, `app/services/database_service.py`).
3.  Make your desired code changes.

As you save your changes, the `app-dev` container, configured with `uvicorn --reload`, will automatically detect these changes and restart, applying them instantly.

**Development URLs:**
- **Development API:** http://api-dev.pocmaster.argentquest.com
- **Production API:** http://api.pocmaster.argentquest.com  
- **API Documentation:** http://api-dev.pocmaster.argentquest.com/docs
- **Database Management:** 
  - pgAdmin: http://localhost:5050 (admin@example.com / admin)
  - System Monitor: http://localhost:3000

### 1.4 Database Development Access

For database connections during development:

**From your local development code (using `.env` file):**
- PostgreSQL: `postgresql://pocuser:pocpass@postgres:5432/poc_db`
- MongoDB: `mongodb://mongoadmin:mongopass123@mongodb:27017/poc_mongo_db`

**From external database tools:**
- PostgreSQL: `localhost:5432` (poc_db, pocuser/pocpass)
- MongoDB: `localhost:27017` (poc_mongo_db, mongoadmin/mongopass123)

Both databases come pre-loaded with comprehensive test data including users, stories, world-building elements, and AI conversation history.

## 2. Preparing Code for Production (Git Workflow)

Once your changes are tested and stable in the development environment, you will prepare them for deployment to the production environment via Git.

### 2.1 Commit Your Changes

1.  Open the Source Control view in VS Code (Ctrl+Shift+G or Cmd+Shift+G).
2.  Stage your changes by clicking the `+` icon next to the files you've modified, or by clicking `Stage All Changes`.
3.  Enter a descriptive commit message in the message box (e.g., "feat: Add new user authentication endpoint").
4.  Click the `Commit` button.

### 2.2 Push Changes to GitHub

1.  Ensure you are on the `main` or `master` branch (or the designated production branch).
2.  Click the `Push` button in the Source Control view, or use the `Synchronize Changes` button to pull and then push.

This will push your committed changes to the remote GitHub repository.

## 3. Manual Deployment to Production

Deployment to the production instance is a manual process that involves connecting to your production server and updating the running Docker containers.

### 3.1 Connect to the Production Server

1.  Use an SSH client (like PuTTY on Windows or the built-in Terminal on macOS/Linux) to connect to your production server.
    ```bash
    ssh your_username@your_production_server_ip
    ```
    Replace `your_username` and `your_production_server_ip` with your actual credentials.

### 3.2 Pull Latest Changes and Redeploy

1.  Once connected to the production server, navigate to the root directory of your `argentquest-suite` project.
2.  Pull the latest code changes from your GitHub repository:
    ```bash
    git pull origin main
    ```
    (Replace `main` with `master` if that is your production branch name).
3.  Rebuild and restart the `app-prod` container (and any other affected services) to apply the new code:
    ```bash
    docker-compose up -d --build app-prod
    ```
    This command will rebuild only the `app-prod` service and restart it, ensuring your changes are live. If other services also need to be rebuilt due to changes in their Dockerfiles or contexts, you can list them or run `docker-compose up -d --build` without specifying a service name to rebuild all services.

## 4. VS Code Tips and Extensions

To enhance your development experience with VS Code:

### Recommended Extensions:

*   **Docker:** Provides an explorer to manage Docker images, containers, and registries directly from VS Code.
*   **Python:** (Microsoft) Rich support for Python development, including IntelliSense, linting, debugging, and more.
*   **Remote - SSH:** Allows you to open any folder on a remote machine using SSH and take advantage of VS Code's full feature set.

### VS Code Server (Included in Stack)

The stack includes a browser-based VS Code Server for remote development:

- **URL:** http://code.pocmaster.argentquest.com
- **Password:** `dev123` (configurable in `.env`)
- **Features:** Full VS Code experience in your browser
- **Usage:** Ideal for server-based development or when you can't install VS Code locally

**Benefits:**
- Access your development environment from any device
- No local VS Code installation required
- Direct access to running containers and logs
- Integrated terminal with Docker access

### Useful VS Code Features:

*   **Integrated Terminal:** Access your host machine's terminal directly within VS Code.
*   **Debugging:** Set breakpoints and step through your Python code running in the `app-dev` container.
*   **Linting & Formatting:** Configure linters (e.g., Black, Flake8) and formatters (e.g., Black) to maintain code quality and consistency.

## 5. Environment-Specific Development

### 5.1 Working with Different Environments

The stack provides three distinct environments:

1. **Local Development** (`.env`):
   - Use for standalone Python applications
   - Docker network connections to shared databases
   - Full access to all services

2. **Development Container** (`app-dev`):
   - Hot-reload enabled for rapid development
   - Debug logging for detailed troubleshooting
   - Single worker for easier debugging

3. **Production Container** (`app-prod`):
   - Production-like testing environment
   - Multiple workers for performance testing
   - Strict logging and security

### 5.2 Testing Environment Differences

```bash
# Test development container
curl http://api-dev.pocmaster.argentquest.com/health

# Test production container  
curl http://api.pocmaster.argentquest.com/health

# Compare response times and behavior
```

### 5.3 Database Debugging

Access database directly for debugging:

```bash
# PostgreSQL via Docker
docker exec -it aq-devsuite-postgres psql -U pocuser -d poc_db

# MongoDB via Docker  
docker exec -it aq-devsuite-mongodb mongosh -u mongoadmin -p mongopass123 --authenticationDatabase admin

# View container logs
docker-compose logs -f app-dev
docker-compose logs -f app-prod
```

## 6. Common Development Issues

### 6.1 Environment File Problems

**Issue:** Container not using updated environment variables
**Solution:** 
```bash
# Restart containers to reload environment files
docker-compose restart app-dev app-prod
```

**Issue:** Database connection refused
**Solution:** 
- Ensure containers use Docker network names (`postgres`, `mongodb`)  
- External tools should use `localhost` connections
- Verify credentials match environment files

### 6.2 Hot Reload Not Working

**Issue:** Changes not reflected in app-dev
**Solution:**
```bash
# Check volume mount and restart
docker-compose logs app-dev
docker-compose restart app-dev
```

### 6.3 Environment Validation

Run comprehensive validation:
```bash
./validate-database-setup.sh
python health-check.py
```
