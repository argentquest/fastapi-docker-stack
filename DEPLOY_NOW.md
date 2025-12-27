# 🚀 QUICK DEPLOYMENT (Production Slim Stack)

This guide deploys the **Lean Production Stack** (5 containers), which is different from the full **Development Suite** (22 containers). For the full suite, see `README.md`.

## ⚡ Fast Deployment (Copy & Paste)

SSH into your server (e.g., Kubuntu 24.04) and run these commands:

```bash
# 1. Clone or update the repository
cd /opt
sudo git clone https://github.com/argentquest/fastapi-docker-stack.git
cd fastapi-docker-stack

# Or if already cloned:
cd /opt/fastapi-docker-stack
sudo git pull origin main

# 2. Create production environment file if not exists
if [ ! -f .env.prod ]; then
    sudo cp .env.template .env.prod
    echo "⚠️  EDIT .env.prod with your API keys!"
    sudo nano .env.prod
fi

# 3. Stop any running containers
sudo docker compose -f docker-compose.prod.yml down

# 4. Build and start production services
sudo docker compose -f docker-compose.prod.yml build
sudo docker compose -f docker-compose.prod.yml up -d

# 5. Check status
sudo docker compose -f docker-compose.prod.yml ps
```

## 📝 Required Environment Variables

Edit `.env.prod` and set these values:

```bash
# OpenRouter Configuration (REQUIRED)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_SITE_URL=https://pocmaster.argentquest.com
OPENROUTER_APP_NAME=V2-POC-Production
OPENROUTER_DEFAULT_MODEL=google/gemini-2.5-flash-lite

# Database Configuration
POSTGRES_USER=pocuser
POSTGRES_PASSWORD=pocpass
POSTGRES_DB=poc_prod
DATABASE_URL=postgresql://pocuser:pocpass@postgres:5432/poc_prod

# MinIO Configuration
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

## 🔍 Verify Deployment

After deployment, check these URLs:

- 🌐 **Main Site**: https://pocmaster.argentquest.com
- 📚 **API Docs**: https://pocmaster.argentquest.com/docs
- ❤️ **Health**: https://pocmaster.argentquest.com/health

## 🐛 Troubleshooting

### If services won't start:

```bash
# Check logs
sudo docker compose -f docker-compose.prod.yml logs app

# Check container status
sudo docker ps -a

# Restart services
sudo docker compose -f docker-compose.prod.yml restart

# Full reset
sudo docker compose -f docker-compose.prod.yml down -v
sudo docker compose -f docker-compose.prod.yml up -d --build
```

### Check Docker is installed:

On Kubuntu/Ubuntu 24.04:
```bash
# Install Docker if not present (using our convenience script method recommended)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

## 📊 Monitor Services

```bash
# View real-time logs
sudo docker compose -f docker-compose.prod.yml logs -f

# Check resource usage
sudo docker stats
```

## 🆘 Emergency Commands

```bash
# Stop everything
sudo docker compose -f docker-compose.prod.yml down

# Remove everything (including data)
sudo docker compose -f docker-compose.prod.yml down -v
```

## 📱 Latest Updates (December 2025)

- ✅ **OS Support**: Validated for Kubuntu/Ubuntu 24.04 LTS
- ✅ **Syntax**: Updated to `docker compose` (V2)
- ✅ **Configuration**: Updated `.env.prod` for Gemini 2.5 Flash
- ✅ **Networking**: Verified Bridged Adapter support for verified VM setups

## 🎯 Expected Result (5 Containers)

You should see 5 healthy containers running:

```
NAME            STATUS                    PORTS
v2-poc-app      Up (healthy)              8000/tcp
v2-poc-nginx    Up                        0.0.0.0:80->80/tcp
v2-poc-postgres Up (healthy)              5432/tcp
v2-poc-redis    Up (healthy)              6379/tcp
v2-poc-minio    Up (healthy)              9000/tcp
```

---

**Need help?** Check the logs: `sudo docker compose -f docker-compose.prod.yml logs`