#!/bin/bash
# V2 POC Complete Database Setup Script
# Sets up PostgreSQL and MongoDB with all databases and collections

set -e  # Exit on any error

echo "🚀 V2 POC Complete Database Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if containers are running
check_container() {
    local container_name=$1
    if ! docker ps | grep -q "$container_name"; then
        log_error "$container_name container is not running"
        log_info "Please start containers with: docker-compose up -d"
        exit 1
    fi
}

log_info "Checking container status..."
check_container "postgres"
check_container "mongodb"
log_success "All database containers are running"

# PostgreSQL Setup
echo ""
log_info "Setting up PostgreSQL databases..."

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
sleep 3

# Create test database if it doesn't exist
docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -c "
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'test_db') THEN
        CREATE DATABASE test_db OWNER pocuser;
    END IF;
END
\$\$;
" 2>/dev/null || docker exec aq-devsuite-postgres createdb -U pocuser test_db 2>/dev/null || true

# Create additional tables in main database
docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -c "
-- Create users table if not exists
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create worlds table if not exists  
CREATE TABLE IF NOT EXISTS worlds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create stories table if not exists
CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    world_id INTEGER REFERENCES worlds(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ai_cost_logs table if not exists
CREATE TABLE IF NOT EXISTS ai_cost_logs (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    estimated_cost DECIMAL(10,6) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (username, email, password_hash) 
VALUES ('demo_user', 'demo@example.com', 'hashed_password') 
ON CONFLICT (username) DO NOTHING;

INSERT INTO worlds (name, description, owner_id)
VALUES ('Demo Fantasy World', 'A sample world for testing', 1)
ON CONFLICT DO NOTHING;
"

log_success "PostgreSQL setup completed"

# MongoDB Setup
echo ""
log_info "Setting up MongoDB databases..."

# Execute MongoDB setup
if [ -f "mongo-config/setup.js" ]; then
    docker exec aq-devsuite-mongodb mongosh --username mongoadmin --password mongopass123 --authenticationDatabase admin < mongo-config/setup.js
    log_success "MongoDB setup completed"
else
    log_warning "MongoDB setup script not found, creating databases manually..."
    
    # Create databases manually if setup.js doesn't exist
    docker exec aq-devsuite-mongodb mongosh --username mongoadmin --password mongopass123 --authenticationDatabase admin --eval "
    // Create main application database
    use('poc_mongo_db');
    db.createCollection('users');
    db.createCollection('worlds');
    db.createCollection('stories');
    
    // Create test database
    use('poc_test_db');
    db.createCollection('test_data');
    
    // Create analytics database
    use('poc_analytics_db');
    db.createCollection('api_logs');
    
    print('MongoDB databases created successfully');
    "
fi

# Verification
echo ""
log_info "Verifying database setup..."

# Check PostgreSQL databases
PG_DATABASES=$(docker exec aq-devsuite-postgres psql -U pocuser -t -c "SELECT datname FROM pg_database WHERE datname IN ('poc_db', 'test_db');" | tr -d ' ' | grep -v '^$')
echo "PostgreSQL databases:"
for db in $PG_DATABASES; do
    log_success "  📊 $db"
done

# Check MongoDB databases  
echo "MongoDB databases:"
docker exec aq-devsuite-mongodb mongosh --username mongoadmin --password mongopass123 --authenticationDatabase admin --quiet --eval "
db.adminCommand('listDatabases').databases.forEach(db => {
    if (db.name.startsWith('poc_')) {
        console.log('  📊', db.name);
    }
});
"

echo ""
log_success "Database setup completed successfully!"
echo ""
echo "📚 Access Information:"
echo "  🐘 PostgreSQL:"
echo "    • PgAdmin: http://localhost:5050"
echo "    • Direct: localhost:5432"
echo "    • Username: pocuser"
echo "    • Password: pocpass"
echo ""
echo "  🍃 MongoDB:"
echo "    • Mongo Express: http://localhost:8082"
echo "    • Direct: localhost:27017"  
echo "    • Username: mongoadmin"
echo "    • Password: mongopass123"
echo ""
echo "  ⚡ Redis:"
echo "    • Redis Commander: http://localhost:8084"
echo "    • Direct: localhost:6379"
echo ""
echo "🎉 All databases are ready for development!"