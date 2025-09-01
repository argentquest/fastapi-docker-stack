#!/bin/bash
# MongoDB Enhanced Setup Script for V2 POC
# This script executes the MongoDB setup JavaScript file

echo "🚀 Starting MongoDB Enhanced Setup for V2 POC..."

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 5

# Check if MongoDB is accessible
if ! mongosh --host mongodb:27017 --username mongoadmin --password mongopass123 --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "❌ Error: Cannot connect to MongoDB"
    echo "Make sure MongoDB container is running and accessible"
    exit 1
fi

echo "✅ MongoDB connection successful"

# Execute the setup script
echo "📝 Executing MongoDB setup script..."
mongosh --host mongodb:27017 --username mongoadmin --password mongopass123 --authenticationDatabase admin < /mongo-config/setup.js

# Verify databases were created
echo "🔍 Verifying database creation..."
mongosh --host mongodb:27017 --username mongoadmin --password mongopass123 --authenticationDatabase admin --eval "
console.log('Available databases:');
db.adminCommand('listDatabases').databases.forEach(db => {
    console.log('  📂', db.name, '(' + (db.sizeOnDisk/1024/1024).toFixed(2) + ' MB)');
});
"

echo ""
echo "🎉 MongoDB Enhanced Setup Complete!"
echo "📊 You can now access all databases via Mongo Express:"
echo "   🌐 URL: http://localhost:8082"
echo "   👤 Username: admin"
echo "   🔐 Password: admin"
echo ""
echo "📚 Available databases:"
echo "   • poc_mongo_db (Main application)"
echo "   • poc_test_db (Testing)"  
echo "   • poc_analytics_db (Metrics)"
echo "   • poc_vector_db (RAG embeddings)"