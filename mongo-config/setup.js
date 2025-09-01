// MongoDB Enhanced Setup Script for V2 POC
// This script creates multiple databases and collections for comprehensive management

// Authentication as admin
use('admin');

// Create application databases with proper collections
print("Setting up V2 POC MongoDB databases...");

// 1. Main Application Database (poc_mongo_db)
use('poc_mongo_db');
db.createCollection('users');
db.createCollection('worlds'); 
db.createCollection('stories');
db.createCollection('characters');
db.createCollection('locations');
db.createCollection('lore_items');
db.createCollection('ai_sessions');
db.createCollection('embeddings');
db.createCollection('rag_documents');

// Insert sample data for testing
db.users.insertOne({
    username: "demo_user",
    email: "demo@example.com",
    created_at: new Date(),
    settings: {
        theme: "dark",
        ai_model: "openai/gpt-5-nano"
    }
});

db.worlds.insertOne({
    name: "Demo Fantasy World",
    description: "A sample fantasy world for testing",
    owner_id: "demo_user",
    created_at: new Date(),
    settings: {
        genre: "fantasy",
        tone: "heroic"
    }
});

// 2. Test Database for automated testing
use('poc_test_db');
db.createCollection('test_users');
db.createCollection('test_data');
db.createCollection('test_vectors');

// Insert test data
db.test_data.insertOne({
    test_case: "sample_test",
    created_at: new Date(),
    status: "active"
});

// 3. Analytics Database for metrics and logging
use('poc_analytics_db');
db.createCollection('api_logs');
db.createCollection('user_sessions');
db.createCollection('ai_usage');
db.createCollection('performance_metrics');

// Insert sample analytics data
db.api_logs.insertOne({
    endpoint: "/ai-test",
    method: "POST", 
    status_code: 200,
    response_time_ms: 150,
    timestamp: new Date(),
    user_id: "demo_user"
});

// 4. Vector Database for RAG and embeddings
use('poc_vector_db');
db.createCollection('document_embeddings');
db.createCollection('world_embeddings');
db.createCollection('character_embeddings');

// Create indexes for better performance
db.document_embeddings.createIndex({ "metadata.source": 1 });
db.document_embeddings.createIndex({ "metadata.created_at": -1 });

// Insert sample vector data
db.document_embeddings.insertOne({
    content: "This is a sample document for RAG testing",
    embedding: Array.from({length: 384}, () => Math.random()),
    metadata: {
        source: "sample_doc.txt",
        chunk_id: 1,
        created_at: new Date()
    }
});

print("✅ MongoDB setup completed successfully!");
print("📊 Created databases:");
print("  - poc_mongo_db (Main application data)");
print("  - poc_test_db (Testing data)");
print("  - poc_analytics_db (Metrics and logs)");
print("  - poc_vector_db (RAG embeddings)");
print("");
print("🔍 Access via Mongo Express: http://localhost:8082");
print("👤 Login: admin / admin");