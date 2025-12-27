#!/usr/bin/env python3
"""
Heimdall Auto-Setup Script
Populates the Heimdall dashboard with links to all exposed services.
"""
import sqlite3
import os
import sys
import datetime

# Configuration
DB_PATH = "/heimdall_config/www/app.sqlite"
DOMAIN_BASE = "pocmaster.argentquest.com"

# Define the apps to add
APPS = [
    {
        "title": "Application (Prod)",
        "url": f"https://api.{DOMAIN_BASE}",
        "icon": "fastapi.png",
        "description": "Main Production API",
        "colour": "#009688"
    },
    {
        "title": "Application (Dev)",
        "url": f"https://api-dev.{DOMAIN_BASE}",
        "icon": "fastapi.png",
        "description": "Development API with Hot Reload",
        "colour": "#4DB6AC"
    },
    {
        "title": "Heimdall",
        "url": f"https://heimdall.{DOMAIN_BASE}",
        "icon": "heimdall.png",
        "description": "This Dashboard",
        "colour": "#C2185B"
    },
    {
        "title": "Nginx Proxy Manager",
        "url": f"http://{DOMAIN_BASE}:81",
        "icon": "nginxproxymanager.png",
        "description": "Proxy & SSL Management",
        "colour": "#212121"
    },
    {
        "title": "System Monitor",
        "url": f"https://{DOMAIN_BASE}",
        "icon": "server.png",
        "description": "Server Stats & Health",
        "colour": "#607D8B"
    },
    {
        "title": "Portainer",
        "url": f"https://portainer.{DOMAIN_BASE}",
        "icon": "portainer.png",
        "description": "Docker Management",
        "colour": "#2196F3"
    },
    {
        "title": "VS Code",
        "url": f"https://code.{DOMAIN_BASE}",
        "icon": "visual-studio-code.png",
        "description": "Online IDE",
        "colour": "#0288D1"
    },
    {
        "title": "Jupyter Lab",
        "url": f"https://jupyter.{DOMAIN_BASE}",
        "icon": "jupyter.png",
        "description": "Data Science Notebooks",
        "colour": "#F57C00"
    },
    {
        "title": "n8n",
        "url": f"https://n8n.{DOMAIN_BASE}",
        "icon": "n8n.png",
        "description": "Workflow Automation",
        "colour": "#EA1E63"
    },
    {
        "title": "MinIO",
        "url": f"https://minio.{DOMAIN_BASE}",
        "icon": "minio.png",
        "description": "Object Storage Console",
        "colour": "#C62828"
    },
    {
        "title": "pgAdmin",
        "url": f"https://pgadmin.{DOMAIN_BASE}",
        "icon": "postgresql.png",
        "description": "PostgreSQL Management",
        "colour": "#3F51B5"
    },
    {
        "title": "Mongo Express",
        "url": f"https://mongo.{DOMAIN_BASE}",
        "icon": "mongodb.png",
        "description": "MongoDB Management",
        "colour": "#4CAF50"
    },
    {
        "title": "Redis Commander",
        "url": f"https://redis.{DOMAIN_BASE}",
        "icon": "redis.png",
        "description": "Redis Management",
        "colour": "#D32F2F"
    },
    {
        "title": "Beszel",
        "url": f"https://beszel.{DOMAIN_BASE}",
        "icon": "dashboard.png",
        "description": "Performance Monitoring",
        "colour": "#7B1FA2"
    },
    {
        "title": "Beszel Agent",
        "url": f"https://beszel-agent.{DOMAIN_BASE}",
        "icon": "server.png",
        "description": "Node Agent Status",
        "colour": "#9C27B0"
    },
     {
        "title": "Monitor API",
        "url": f"https://monitor-api.{DOMAIN_BASE}",
        "icon": "api.png",
        "description": "Monitoring Backend API",
        "colour": "#546E7A"
    }
]

def wait_for_db():
    print(f"Checking for database at {DB_PATH}...")
    # Initialize timestamp for created_at
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    if not os.path.exists(DB_PATH):
        print(f"⚠️  Database not found at {DB_PATH}. Heimdall might not be initialized yet.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("✅ Connected to Heimdall database.")
        
        # Check if items table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='items'")
        if not cursor.fetchone():
            print("⚠️  'items' table not found. Is the database initialized?")
            conn.close()
            return

        # Insert or Update items
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Processing {len(APPS)} application links...")
        
        count = 0
        for i, app in enumerate(APPS):
            # Check if exists by title or URL (heuristic)
            cursor.execute("SELECT id FROM items WHERE title = ? OR url = ?", (app['title'], app['url']))
            existing = cursor.fetchone()
            
            if existing:
                # Update
                cursor.execute("""
                    UPDATE items 
                    SET url=?, description=?, colour=?, "order"=?, updated_at=?
                    WHERE id=?
                """, (app['url'], app['description'], app['colour'], i, now, existing[0]))
            else:
                # Insert
                cursor.execute("""
                    INSERT INTO items (title, url, description, colour, icon, "order", pinned, created_at, updated_at, type, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 0, 1)
                """, (app['title'], app['url'], app['description'], app['colour'], app['icon'], i, now, now))
                count += 1
                
        conn.commit()
        conn.close()
        print(f"✅ Heimdall updated successfully! Added {count} new items.")
        
    except Exception as e:
        print(f"❌ Error updating Heimdall: {e}")

if __name__ == "__main__":
    main()
