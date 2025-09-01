-- Database Setup Script for All Environments
-- Creates tables and loads sample data for local, dev, and prod databases

-- Common table creation script
\set ON_ERROR_STOP on

-- Function to create tables in a database
CREATE OR REPLACE FUNCTION create_tables_for_db(db_name text) RETURNS void AS $$
BEGIN
    -- This would be executed in each database
    RAISE NOTICE 'Creating tables for database: %', db_name;
END;
$$ LANGUAGE plpgsql;

-- Create tables for LOCAL environment
\c poc_local

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    environment VARCHAR(20) DEFAULT 'local',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS worlds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    environment VARCHAR(20) DEFAULT 'local',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    world_id INTEGER REFERENCES worlds(id),
    environment VARCHAR(20) DEFAULT 'local',
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
    environment VARCHAR(20) DEFAULT 'local',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert LOCAL sample data
INSERT INTO users (username, email, password_hash, environment) 
VALUES 
    ('local_user', 'user@local.com', 'hashed_password_local', 'local'),
    ('test_local', 'test@local.com', 'hashed_password_test', 'local')
ON CONFLICT (username) DO NOTHING;

INSERT INTO worlds (name, description, owner_id, environment)
VALUES 
    ('Local Fantasy World', 'A fantasy world for local development', 1, 'local'),
    ('Local Sci-Fi World', 'A sci-fi world for local testing', 1, 'local')
ON CONFLICT DO NOTHING;

INSERT INTO stories (title, content, world_id, environment)
VALUES 
    ('The Local Adventure', 'A story for local development testing...', 1, 'local'),
    ('Local Space Odyssey', 'Testing story in local environment...', 2, 'local')
ON CONFLICT DO NOTHING;

-- Create tables for DEV environment
\c poc_dev

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    environment VARCHAR(20) DEFAULT 'dev',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS worlds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    environment VARCHAR(20) DEFAULT 'dev',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    world_id INTEGER REFERENCES worlds(id),
    environment VARCHAR(20) DEFAULT 'dev',
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
    environment VARCHAR(20) DEFAULT 'dev',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert DEV sample data
INSERT INTO users (username, email, password_hash, environment) 
VALUES 
    ('dev_user', 'user@dev.com', 'hashed_password_dev', 'dev'),
    ('qa_tester', 'qa@dev.com', 'hashed_password_qa', 'dev'),
    ('dev_admin', 'admin@dev.com', 'hashed_password_admin', 'dev')
ON CONFLICT (username) DO NOTHING;

INSERT INTO worlds (name, description, owner_id, environment)
VALUES 
    ('Development Fantasy World', 'Main testing world for dev environment', 1, 'dev'),
    ('QA Testing World', 'World for QA testing scenarios', 2, 'dev'),
    ('Integration Test World', 'World for integration testing', 3, 'dev')
ON CONFLICT DO NOTHING;

INSERT INTO stories (title, content, world_id, environment)
VALUES 
    ('Dev Story Alpha', 'Development story for testing features...', 1, 'dev'),
    ('QA Test Case 001', 'Story used for QA validation...', 2, 'dev'),
    ('Integration Test Story', 'Story for testing integrations...', 3, 'dev')
ON CONFLICT DO NOTHING;

-- Create tables for PROD environment
\c poc_prod

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    environment VARCHAR(20) DEFAULT 'prod',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS worlds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    owner_id INTEGER REFERENCES users(id),
    environment VARCHAR(20) DEFAULT 'prod',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    world_id INTEGER REFERENCES worlds(id),
    environment VARCHAR(20) DEFAULT 'prod',
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
    environment VARCHAR(20) DEFAULT 'prod',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert PROD sample data (minimal for production)
INSERT INTO users (username, email, password_hash, environment) 
VALUES 
    ('demo_user', 'demo@production.com', 'hashed_password_prod', 'prod'),
    ('admin', 'admin@production.com', 'hashed_password_admin_prod', 'prod')
ON CONFLICT (username) DO NOTHING;

INSERT INTO worlds (name, description, owner_id, environment)
VALUES 
    ('Argentquest Chronicles', 'The official production world', 2, 'prod'),
    ('Demo World', 'A demonstration world for new users', 1, 'prod')
ON CONFLICT DO NOTHING;

INSERT INTO stories (title, content, world_id, environment)
VALUES 
    ('Welcome to Argentquest', 'An introductory story for new users...', 2, 'prod'),
    ('Demo Adventure', 'A sample story showing platform capabilities...', 1, 'prod')
ON CONFLICT DO NOTHING;