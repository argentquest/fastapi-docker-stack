# Nginx Proxy Manager Setup for pocmaster.argentquest.com

## Prerequisites
1. DNS A record for `pocmaster.argentquest.com` pointing to your server's public IP
2. Docker containers running (`docker-compose up`)
3. Port 80 and 443 open on your firewall

## Step-by-Step NPM Configuration

### 1. Access NPM Admin Interface
- **URL**: `http://your-server-ip:81`
- **Default Login**: 
  - Email: `admin@example.com`
  - Password: `changeme`
- **First Login**: You'll be prompted to change credentials

### 2. Create Proxy Hosts for Each Service

#### A. Main Dashboard (Heimdall)
**Add Proxy Host:**
- **Domain Names**: `pocmaster.argentquest.com`
- **Scheme**: `http`
- **Forward Hostname/IP**: `172.21.0.10` (or `heimdall`)
- **Forward Port**: `80`
- **Cache Assets**: ✓ Enabled
- **Block Common Exploits**: ✓ Enabled
- **Websockets Support**: ✓ Enabled

**SSL Tab:**
- **SSL Certificate**: Request new SSL Certificate with Let's Encrypt
- **Force SSL**: ✓ Enabled
- **HTTP/2 Support**: ✓ Enabled
- **HSTS Enabled**: ✓ Enabled
- **Email**: `admin@argentquest.com`
- **Use DNS Challenge**: ❌ (HTTP challenge is fine)

#### B. API Services

**Production API:**
- **Domain Names**: `pocmaster.argentquest.com/api`
- **Scheme**: `http`
- **Forward Hostname/IP**: `172.22.0.11` (app-prod)
- **Forward Port**: `8000`
- **Advanced**: Add custom location `/api`

**Development API:**
- **Domain Names**: `pocmaster.argentquest.com/api-dev`  
- **Forward Hostname/IP**: `172.22.0.10` (app-dev)
- **Forward Port**: `8000`

#### C. Management Services

**Portainer:**
- **Domain Names**: `pocmaster.argentquest.com/portainer`
- **Scheme**: `https`
- **Forward Hostname/IP**: `172.24.0.10`
- **Forward Port**: `9443`
- **SSL Verification**: ❌ Disabled (self-signed cert)

**pgAdmin:**
- **Domain Names**: `pocmaster.argentquest.com/pgadmin`
- **Forward Hostname/IP**: `172.24.0.11`
- **Forward Port**: `80`

**Mongo Express:**
- **Domain Names**: `pocmaster.argentquest.com/mongo`
- **Forward Hostname/IP**: `172.24.0.12`
- **Forward Port**: `8081`

**Redis Commander:**
- **Domain Names**: `pocmaster.argentquest.com/redis`
- **Forward Hostname/IP**: `172.24.0.13`
- **Forward Port**: `8081`

**MinIO Console:**
- **Domain Names**: `pocmaster.argentquest.com/minio`
- **Forward Hostname/IP**: `172.23.0.13`
- **Forward Port**: `9001`

#### D. Development Tools

**VS Code Server:**
- **Domain Names**: `pocmaster.argentquest.com/code`
- **Forward Hostname/IP**: `172.25.0.10`
- **Forward Port**: `8080`
- **Websockets Support**: ✓ Enabled

**MCP Inspector:**
- **Domain Names**: `pocmaster.argentquest.com/mcp`
- **Forward Hostname/IP**: `172.25.0.11`
- **Forward Port**: `5173`
- **Websockets Support**: ✓ Enabled

**System Monitor:**
- **Domain Names**: `pocmaster.argentquest.com/status`
- **Forward Hostname/IP**: `172.21.0.11`
- **Forward Port**: `80`

### 3. Advanced Configuration

#### Custom Nginx Config (Optional)
For each proxy host, you can add custom Nginx directives:

```nginx
# For API services
client_max_body_size 100M;
proxy_read_timeout 300s;
proxy_connect_timeout 75s;

# For development tools
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

#### Access Lists (Optional)
Create access lists to restrict admin tools:
- **Management Tools**: Allow only your IP ranges
- **Development Tools**: Internal access only
- **Production API**: Public access

### 4. SSL Certificate Management

NPM will automatically:
- ✅ Generate Let's Encrypt certificates
- ✅ Renew certificates before expiration
- ✅ Handle certificate challenges
- ✅ Redirect HTTP to HTTPS

### 5. Testing Checklist

After setup, verify each URL:
- ✅ `https://pocmaster.argentquest.com` → Heimdall
- ✅ `https://pocmaster.argentquest.com/api/health` → FastAPI prod
- ✅ `https://pocmaster.argentquest.com/api-dev/health` → FastAPI dev
- ✅ `https://pocmaster.argentquest.com/portainer` → Docker management
- ✅ `https://pocmaster.argentquest.com/pgadmin` → PostgreSQL admin
- ✅ `https://pocmaster.argentquest.com/mongo` → MongoDB admin
- ✅ `https://pocmaster.argentquest.com/redis` → Redis admin
- ✅ `https://pocmaster.argentquest.com/minio` → Object storage
- ✅ `https://pocmaster.argentquest.com/code` → VS Code Server
- ✅ `https://pocmaster.argentquest.com/mcp` → MCP Inspector
- ✅ `https://pocmaster.argentquest.com/status` → System monitor

### 6. Security Notes

- **Let's Encrypt Rate Limits**: 20 certificates per week per domain
- **Certificate Renewal**: Automatic every 60 days
- **Backup Certificates**: NPM stores certificates in `/data/letsencrypt`
- **Wildcard Certs**: Available with DNS challenge (more complex)

Want me to update the docker-compose.yml to include all the network configuration for NPM?