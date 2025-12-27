# Nginx Proxy Manager Setup for pocmaster.argentquest.com

## 🚀 Recommended: Automated Setup
We strictly recommend using the provided Python automation script. It automatically detects your Docker network configuration and creates all proxy hosts using stable container hostnames.

```bash
# Run the setup script
python scripts/npm-simple-setup.py
```

**What this script does:**
1.  Connects to NPM Admin API
2.  Authenticates with default or current credentials
3.  Cleans up old/stale proxy hosts
4.  Creates new proxy hosts for all 14 services using internal Docker DNS names (`aq-devsuite-app-prod`, etc.)
5.  Configures correct ports and websocket support

---

## 🛠️ Manual Configuration (Fallback Only)

**⚠️ Warning:** The IP addresses listed below (e.g., `172.21.0.10`) are **examples only**. Docker dynamically assigns IPs. If doing this manually, you must verify the actual IP of each container using:
```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container_name>
```

### 1. Access NPM Admin Interface
- **URL**: `http://your-server-ip:81`
- **Default Login**: 
  - Email: `admin@example.com`
  - Password: `changeme`

### 2. Create Proxy Hosts
If the script fails, you can manually add hosts. Use the **Container Name** as the "Forward Hostname" if NPM is on the same Docker network (recommended), or the IP address if not.

#### A. Main Services

| Service | Domain | Forward Hostname | Port |
|---------|--------|------------------|------|
| **Heimdall** | `pocmaster.argentquest.com` | `aq-devsuite-heimdall` | 80 |
| **API Prod** | `api.pocmaster.argentquest.com` | `aq-devsuite-app-prod` | 8000 |
| **API Dev** | `api-dev.pocmaster.argentquest.com` | `aq-devsuite-app-dev` | 8000 |
| **Portainer** | `portainer.pocmaster.argentquest.com` | `aq-devsuite-portainer` | 9443 |
| **pgAdmin** | `pgadmin.pocmaster.argentquest.com` | `aq-devsuite-pgadmin` | 80 |
| **Mongo Express** | `mongo.pocmaster.argentquest.com` | `aq-devsuite-mongo-express` | 8081 |
| **MinIO** | `minio.pocmaster.argentquest.com` | `aq-devsuite-minio` | 9001 |
| **VS Code** | `code.pocmaster.argentquest.com` | `aq-devsuite-vscode` | 8080 |

### 3. SSL Configuration
For each host in the "SSL" tab:
- **SSL Certificate**: Request a new Let's Encrypt certificate
- **Force SSL**: Enabled
- **HTTP/2 Support**: Enabled
- **Email**: `admin@argentquest.com`