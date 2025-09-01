-- Create tables for V2 POC Application
-- This script creates the necessary database tables for the application

-- Create ai_test_logs table
CREATE TABLE IF NOT EXISTS ai_test_logs (
    id SERIAL PRIMARY KEY,
    system_prompt TEXT NOT NULL,
    user_context TEXT NOT NULL,
    ai_result TEXT NOT NULL,
    embedding vector(1536),  -- Assuming 1536 dimensions for embeddings
    file_url TEXT,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on created_at for faster queries
CREATE INDEX IF NOT EXISTS idx_ai_test_logs_created_at ON ai_test_logs(created_at DESC);

-- Create index on embedding for vector similarity search (if using pgvector)
-- CREATE INDEX IF NOT EXISTS idx_ai_test_logs_embedding ON ai_test_logs USING ivfflat (embedding vector_cosine_ops);

-- Add any other tables needed for the application here

-- Example: Users table (if needed)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example: API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pocuser;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pocuser;