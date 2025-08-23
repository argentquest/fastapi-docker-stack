-- V2 POC Database Initialization
-- This script runs automatically when PostgreSQL container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the ai_test_logs table for POC testing
CREATE TABLE IF NOT EXISTS ai_test_logs (
    id SERIAL PRIMARY KEY,
    system_prompt TEXT NOT NULL,
    user_context TEXT NOT NULL,
    ai_result TEXT NOT NULL,
    embedding vector(1024),  -- BGE-large embeddings (1024 dimensions)
    file_url TEXT,           -- MinIO storage URL
    response_time_ms INTEGER, -- Performance tracking
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_ai_test_logs_created_at ON ai_test_logs (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ai_test_logs_response_time ON ai_test_logs (response_time_ms);

-- Create vector similarity index (IVFFlat for pgvector)
-- Lists parameter: rough rule is sqrt(num_rows), we'll start with 100
CREATE INDEX IF NOT EXISTS idx_ai_test_logs_embedding 
ON ai_test_logs USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Insert some sample data for testing (optional)
INSERT INTO ai_test_logs (system_prompt, user_context, ai_result, response_time_ms)
VALUES 
    ('You are a helpful assistant.', 
     'Hello, this is a test message.', 
     'Hello! I''m here to help you. This is a test response from the V2 POC system.',
     1250),
    ('You are a creative storyteller.',
     'Write a short story about a dragon.',
     'Once upon a time, in a land far away, there lived a wise dragon named Ember who protected a village of kind-hearted people...',
     2100),
    ('You are a technical expert.',
     'Explain how vector databases work.',
     'Vector databases store high-dimensional vectors and enable similarity search through mathematical operations like cosine similarity...',
     1875)
ON CONFLICT DO NOTHING;

-- Create a function to clean up old logs (for maintenance)
CREATE OR REPLACE FUNCTION cleanup_old_ai_logs(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM ai_test_logs 
    WHERE created_at < NOW() - INTERVAL '%s days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create a function to get embedding similarity statistics
CREATE OR REPLACE FUNCTION get_embedding_stats()
RETURNS TABLE(
    total_embeddings INTEGER,
    avg_similarity NUMERIC,
    min_similarity NUMERIC,
    max_similarity NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH similarity_matrix AS (
        SELECT 
            a.id as id1,
            b.id as id2,
            1 - (a.embedding <=> b.embedding) as similarity
        FROM ai_test_logs a
        CROSS JOIN ai_test_logs b
        WHERE a.id != b.id
        AND a.embedding IS NOT NULL 
        AND b.embedding IS NOT NULL
    )
    SELECT 
        (SELECT COUNT(*) FROM ai_test_logs WHERE embedding IS NOT NULL)::INTEGER as total_embeddings,
        ROUND(AVG(similarity), 4) as avg_similarity,
        ROUND(MIN(similarity), 4) as min_similarity,
        ROUND(MAX(similarity), 4) as max_similarity
    FROM similarity_matrix;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions to the poc user
GRANT ALL PRIVILEGES ON DATABASE poc_db TO pocuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pocuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pocuser;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO pocuser;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'V2 POC Database initialized successfully';
    RAISE NOTICE 'pgvector extension: %', (SELECT extversion FROM pg_extension WHERE extname = 'vector');
    RAISE NOTICE 'Sample data inserted: % rows', (SELECT COUNT(*) FROM ai_test_logs);
END $$;