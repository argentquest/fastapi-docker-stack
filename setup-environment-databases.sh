#!/bin/bash
# Setup script for all environment databases with sample data

echo "🚀 Setting up environment databases with sample data..."

# Function to create tables and load data for a database
setup_database() {
    local db_name=$1
    local env_name=$2
    
    echo "📊 Setting up $db_name ($env_name environment)..."
    
    docker exec aq-devsuite-postgres psql -U pocuser -d $db_name -c "
    -- Create tables
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        environment VARCHAR(20) DEFAULT '$env_name',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS worlds (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        owner_id INTEGER REFERENCES users(id),
        environment VARCHAR(20) DEFAULT '$env_name',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS stories (
        id SERIAL PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        content TEXT,
        world_id INTEGER REFERENCES worlds(id),
        environment VARCHAR(20) DEFAULT '$env_name',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS ai_cost_logs (
        id SERIAL PRIMARY KEY,
        model_name VARCHAR(100) NOT NULL,
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        total_tokens INTEGER DEFAULT 0,
        estimated_cost DECIMAL(10,6) DEFAULT 0.0,
        environment VARCHAR(20) DEFAULT '$env_name',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    "
    
    # Load environment-specific sample data
    case $env_name in
        "local")
            docker exec aq-devsuite-postgres psql -U pocuser -d $db_name -c "
            INSERT INTO users (username, email, password_hash) 
            VALUES 
                ('local_user', 'user@local.com', 'hashed_password_local'),
                ('test_local', 'test@local.com', 'hashed_password_test')
            ON CONFLICT (username) DO NOTHING;

            INSERT INTO worlds (name, description, owner_id)
            SELECT 'Local Fantasy World', 'A fantasy world for local development', id
            FROM users WHERE username = 'local_user'
            ON CONFLICT DO NOTHING;

            INSERT INTO stories (title, content, world_id)
            SELECT 'The Local Adventure', 'A story for local development testing...', w.id
            FROM worlds w
            JOIN users u ON w.owner_id = u.id
            WHERE u.username = 'local_user' AND w.name = 'Local Fantasy World'
            ON CONFLICT DO NOTHING;
            "
            ;;
        "dev")
            docker exec aq-devsuite-postgres psql -U pocuser -d $db_name -c "
            INSERT INTO users (username, email, password_hash) 
            VALUES 
                ('dev_user', 'user@dev.com', 'hashed_password_dev'),
                ('qa_tester', 'qa@dev.com', 'hashed_password_qa'),
                ('dev_admin', 'admin@dev.com', 'hashed_password_admin')
            ON CONFLICT (username) DO NOTHING;

            INSERT INTO worlds (name, description, owner_id)
            SELECT 'Development Fantasy World', 'Main testing world for dev environment', id
            FROM users WHERE username = 'dev_user'
            ON CONFLICT DO NOTHING;

            INSERT INTO worlds (name, description, owner_id)
            SELECT 'QA Testing World', 'World for QA testing scenarios', id
            FROM users WHERE username = 'qa_tester'
            ON CONFLICT DO NOTHING;

            INSERT INTO stories (title, content, world_id)
            SELECT 'Dev Story Alpha', 'Development story for testing features...', w.id
            FROM worlds w
            JOIN users u ON w.owner_id = u.id
            WHERE u.username = 'dev_user' AND w.name = 'Development Fantasy World'
            ON CONFLICT DO NOTHING;

            INSERT INTO stories (title, content, world_id)
            SELECT 'QA Test Case 001', 'Story used for QA validation...', w.id
            FROM worlds w
            JOIN users u ON w.owner_id = u.id
            WHERE u.username = 'qa_tester' AND w.name = 'QA Testing World'
            ON CONFLICT DO NOTHING;
            "
            ;;
        "prod")
            docker exec aq-devsuite-postgres psql -U pocuser -d $db_name -c "
            INSERT INTO users (username, email, password_hash) 
            VALUES 
                ('demo_user', 'demo@production.com', 'hashed_password_prod'),
                ('admin', 'admin@production.com', 'hashed_password_admin_prod')
            ON CONFLICT (username) DO NOTHING;

            INSERT INTO worlds (name, description, owner_id)
            SELECT 'Argentquest Chronicles', 'The official production world', id
            FROM users WHERE username = 'admin'
            ON CONFLICT DO NOTHING;

            INSERT INTO worlds (name, description, owner_id)
            SELECT 'Demo World', 'A demonstration world for new users', id
            FROM users WHERE username = 'demo_user'
            ON CONFLICT DO NOTHING;

            INSERT INTO stories (title, content, world_id)
            SELECT 'Welcome to Argentquest', 'An introductory story for new users...', w.id
            FROM worlds w
            JOIN users u ON w.owner_id = u.id
            WHERE u.username = 'admin' AND w.name = 'Argentquest Chronicles'
            ON CONFLICT DO NOTHING;
            "
            ;;
    esac
    
    echo "✅ $db_name setup complete!"
}

# Setup all three databases
setup_database "poc_local" "local"
setup_database "poc_dev" "dev"
setup_database "poc_prod" "prod"

# Verify the setup
echo ""
echo "🔍 Verifying database setup..."
echo ""

for db in poc_local poc_dev poc_prod; do
    echo "📊 Database: $db"
    docker exec aq-devsuite-postgres psql -U pocuser -d $db -c "
    SELECT 
        (SELECT COUNT(*) FROM users) as users,
        (SELECT COUNT(*) FROM worlds) as worlds,
        (SELECT COUNT(*) FROM stories) as stories;
    " 2>/dev/null
done

echo ""
echo "✅ All environment databases set up successfully!"
echo ""
echo "📚 Available databases:"
echo "  • poc_local - Local development environment"
echo "  • poc_dev   - Development/testing environment"
echo "  • poc_prod  - Production environment"
echo "  • poc_db    - Legacy/backward compatibility"