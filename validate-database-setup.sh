#!/bin/bash
# Database Setup Validation Script
# Validates that both PostgreSQL and MongoDB contain expected test data

echo "🔍 Validating Database Setup..."
echo "================================"

# Test PostgreSQL connection and data
echo "📊 PostgreSQL Validation:"
echo "-------------------------"

if docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -c "SELECT version();" > /dev/null 2>&1; then
    echo "✅ PostgreSQL connection: SUCCESS"
    
    # Check table counts
    PG_RESULTS=$(docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -t -c "
    SELECT 
        (SELECT COUNT(*) FROM users) as users,
        (SELECT COUNT(*) FROM stories) as stories,
        (SELECT COUNT(*) FROM world_elements) as world_elements,
        (SELECT COUNT(*) FROM ai_test_logs) as ai_logs;
    " | xargs)
    
    echo "📈 PostgreSQL Data Counts: $PG_RESULTS"
    
    # Verify pgvector extension
    if docker exec aq-devsuite-postgres psql -U pocuser -d poc_db -c "SELECT extname FROM pg_extension WHERE extname='vector';" | grep -q vector; then
        echo "✅ pgvector extension: LOADED"
    else
        echo "❌ pgvector extension: MISSING"
    fi
else
    echo "❌ PostgreSQL connection: FAILED"
fi

echo ""

# Test MongoDB connection and data
echo "🍃 MongoDB Validation:"
echo "---------------------"

if docker exec aq-devsuite-mongodb mongosh -u mongoadmin -p mongopass123 --authenticationDatabase admin --eval "db.runCommand('ping')" --quiet > /dev/null 2>&1; then
    echo "✅ MongoDB connection: SUCCESS"
    
    # Check collection counts
    MONGO_RESULTS=$(docker exec aq-devsuite-mongodb mongosh -u mongoadmin -p mongopass123 --authenticationDatabase admin --eval "
    db = db.getSiblingDB('poc_mongo_db');
    print(db.users.countDocuments() + ' users, ' + 
          db.documents.countDocuments() + ' docs, ' + 
          db.world_building.countDocuments() + ' world, ' + 
          db.ai_conversations.countDocuments() + ' convos, ' + 
          db.sessions.countDocuments() + ' sessions');
    " --quiet 2>/dev/null)
    
    echo "📈 MongoDB Data Counts: $MONGO_RESULTS"
    
    # Test sample query
    if docker exec aq-devsuite-mongodb mongosh -u mongoadmin -p mongopass123 --authenticationDatabase admin --eval "db.getSiblingDB('poc_mongo_db').users.findOne({username: 'alice_writer'})" --quiet > /dev/null 2>&1; then
        echo "✅ MongoDB queries: WORKING"
    else
        echo "❌ MongoDB queries: FAILED"
    fi
else
    echo "❌ MongoDB connection: FAILED"
fi

echo ""

# Test Management Tools
echo "🛠️ Management Tools:"
echo "-------------------"

if curl -s http://localhost:5050 | grep -q "Redirecting"; then
    echo "✅ pgAdmin: ACCESSIBLE (http://localhost:5050)"
else
    echo "❌ pgAdmin: NOT ACCESSIBLE"
fi

if docker ps | grep -q aq-devsuite-mongo-express; then
    echo "✅ Mongo Express: RUNNING"
else
    echo "❌ Mongo Express: NOT RUNNING"
fi

echo ""
echo "🏁 Validation Complete!"
echo "======================"

# Summary
TOTAL_CONTAINERS=$(docker ps | wc -l)
echo "📦 Total running containers: $((TOTAL_CONTAINERS-1))"
echo "🌐 Access URLs:"
echo "   • pgAdmin: http://localhost:5050 (admin@example.com / admin)"
echo "   • System Monitor: http://localhost:8085"
echo "   • Database Credentials: http://localhost:8085/database-credentials.html"