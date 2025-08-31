#!/bin/bash

# pgAdmin Configuration Setup Script
# This script sets up the correct permissions for pgAdmin configuration files

echo "Setting up pgAdmin configuration..."

# Set correct permissions for pgpass file (600 = read/write for owner only)
chmod 600 /var/lib/pgadmin/.pgpass

# Set ownership to pgadmin user (UID 5050)
chown 5050:5050 /var/lib/pgadmin/.pgpass

echo "pgAdmin configuration setup complete!"