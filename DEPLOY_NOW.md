# 🚀 QUICK DEPLOYMENT TO pocmaster.argentquest.com

## ⚡ Fast Deployment (Copy & Paste)

SSH into your server and run these commands:

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
sudo docker-compose -f docker-compose.prod.yml down

# 4. Build and start production services
sudo docker-compose -f docker-compose.prod.yml build
sudo docker-compose -f docker-compose.prod.yml up -d

# 5. Check status
sudo docker-compose -f docker-compose.prod.yml ps
```

## 📝 Required Environment Variables

Edit `.env.prod` and set these values:

```bash
# OpenRouter Configuration (REQUIRED)
OPENROUTER_API_KEY=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
OPENROUTER_SITE_URL=https://pocmaster.argentquest.com
OPENROUTER_APP_NAME=V2-POC-Production
OPENROUTER_DEFAULT_MODEL=google/gemini-2.5-flash-lite

# Google AI Configuration (Optional)
GOOGLE_API_KEY=your-google-api-key-here
GOOGLE_DEFAULT_MODEL=gemini-2.5-flash-image-preview

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
- 🏠 **Frontend**: https://pocmaster.argentquest.com/claude/
- ❤️ **Health**: https://pocmaster.argentquest.com/health

## 🐛 Troubleshooting

### If services won't start:

```bash
# Check logs
sudo docker-compose -f docker-compose.prod.yml logs app

# Check container status
sudo docker ps -a

# Restart services
sudo docker-compose -f docker-compose.prod.yml restart

# Full reset
sudo docker-compose -f docker-compose.prod.yml down -v
sudo docker-compose -f docker-compose.prod.yml up -d --build
```

### If OpenRouter has authentication issues:

```bash
# The service caches the API key, so restart is required
sudo docker-compose -f docker-compose.prod.yml restart app
```

### Check Docker is installed:

```bash
# Install Docker if not present
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

## 📊 Monitor Services

```bash
# View real-time logs
sudo docker-compose -f docker-compose.prod.yml logs -f

# Check resource usage
sudo docker stats

# View all containers
sudo docker ps -a
```

## 🆘 Emergency Commands

```bash
# Stop everything
sudo docker-compose -f docker-compose.prod.yml down

# Remove everything (including data)
sudo docker-compose -f docker-compose.prod.yml down -v

# Rebuild from scratch
sudo docker-compose -f docker-compose.prod.yml build --no-cache
sudo docker-compose -f docker-compose.prod.yml up -d
```

## 📱 Latest Updates (as of commit ac2547e)

- ✅ Fixed Dockerfile to include frontend directories
- ✅ Updated all .env templates with AI model configuration
- ✅ Fixed docker-compose.prod.yml with all environment variables
- ✅ Added Windows startup scripts
- ✅ Enhanced dashboard with frontend URLs
- ✅ Fixed OpenRouter authentication headers

## 🎯 Expected Result

After successful deployment, you should see:

```
NAME            STATUS                    PORTS
v2-poc-app      Up 2 minutes (healthy)    8000/tcp
v2-poc-nginx    Up 2 minutes              0.0.0.0:80->80/tcp
v2-poc-postgres Up 2 minutes (healthy)    5432/tcp
v2-poc-redis    Up 2 minutes (healthy)    6379/tcp
v2-poc-minio    Up 2 minutes (healthy)    9000/tcp
```

---

**Need help?** Check the logs first: `sudo docker-compose -f docker-compose.prod.yml logs`