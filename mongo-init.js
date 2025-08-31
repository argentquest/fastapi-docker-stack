// MongoDB Initialization Script
// This script runs when MongoDB container starts for the first time

// Switch to poc_mongo_db database
db = db.getSiblingDB('poc_mongo_db');

// Create collections with schema validation
db.createCollection('users', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['username', 'email', 'full_name'],
            properties: {
                username: { bsonType: 'string' },
                email: { bsonType: 'string' },
                full_name: { bsonType: 'string' },
                bio: { bsonType: 'string' },
                writing_style: { bsonType: 'string' },
                ai_preference: { bsonType: 'string' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

db.createCollection('documents');
db.createCollection('world_building');
db.createCollection('ai_conversations');
db.createCollection('sessions');

// Insert test users
db.users.insertMany([
    {
        username: 'alice_writer',
        email: 'alice@example.com',
        full_name: 'Alice Johnson',
        bio: 'Fantasy writer and world builder with 10 years of experience',
        writing_style: 'Descriptive and immersive',
        ai_preference: 'High AI assistance',
        favorite_genres: ['Fantasy', 'Adventure', 'Epic'],
        word_count_goal: 2000,
        created_at: new Date()
    },
    {
        username: 'bob_cyberpunk',
        email: 'bob@example.com',
        full_name: 'Robert Chen',
        bio: 'Cyberpunk novelist and tech enthusiast',
        writing_style: 'Technical and fast-paced',
        ai_preference: 'Medium AI assistance',
        favorite_genres: ['Cyberpunk', 'Thriller', 'Noir'],
        word_count_goal: 1500,
        created_at: new Date()
    },
    {
        username: 'carol_scifi',
        email: 'carol@example.com',
        full_name: 'Dr. Carol Martinez',
        bio: 'Science fiction author and physicist',
        writing_style: 'Scientific and detailed',
        ai_preference: 'Low AI assistance',
        favorite_genres: ['Hard Sci-Fi', 'Space Opera', 'Time Travel'],
        word_count_goal: 3000,
        created_at: new Date()
    },
    {
        username: 'david_mystery',
        email: 'david@example.com',
        full_name: 'David Thompson',
        bio: 'Mystery and thriller writer',
        writing_style: 'Suspenseful with plot twists',
        ai_preference: 'High AI assistance',
        favorite_genres: ['Mystery', 'Thriller', 'Detective'],
        word_count_goal: 2500,
        created_at: new Date()
    },
    {
        username: 'eva_dystopian',
        email: 'eva@example.com',
        full_name: 'Eva Rodriguez',
        bio: 'Dystopian fiction specialist',
        writing_style: 'Atmospheric and philosophical',
        ai_preference: 'Medium AI assistance',
        favorite_genres: ['Dystopian', 'Post-Apocalyptic', 'Social Sci-Fi'],
        word_count_goal: 1800,
        created_at: new Date()
    }
]);

// Insert test documents
db.documents.insertMany([
    {
        title: 'The Crystal Kingdom',
        author: 'alice_writer',
        content: 'In the realm of Aethermoor, crystals hold the power of creation...',
        genre: 'Fantasy',
        word_count: 5420,
        chapters: 3,
        status: 'in_progress',
        created_at: new Date(),
        last_modified: new Date()
    },
    {
        title: 'Neon Dreams',
        author: 'bob_cyberpunk',
        content: 'The rain never stopped in Neo-Tokyo 2087...',
        genre: 'Cyberpunk',
        word_count: 3200,
        chapters: 2,
        status: 'draft',
        created_at: new Date(),
        last_modified: new Date()
    },
    {
        title: 'Quantum Paradox',
        author: 'carol_scifi',
        content: 'The equations were clear, but the implications were staggering...',
        genre: 'Science Fiction',
        word_count: 8900,
        chapters: 5,
        status: 'published',
        created_at: new Date(),
        last_modified: new Date()
    }
]);

// Insert world building elements
db.world_building.insertMany([
    {
        name: 'Aethermoor',
        type: 'location',
        description: 'A floating kingdom powered by crystal energy',
        created_by: 'alice_writer',
        properties: {
            climate: 'Temperate magical',
            population: 500000,
            government: 'Crystal Council',
            magic_level: 'High'
        },
        created_at: new Date()
    },
    {
        name: 'Zara the Wise',
        type: 'character',
        description: 'Ancient dragon sage and keeper of knowledge',
        created_by: 'alice_writer',
        properties: {
            age: 'Unknown (over 1000)',
            race: 'Elder Dragon',
            abilities: ['Prophecy', 'Time Magic', 'Telepathy'],
            alignment: 'Neutral Good'
        },
        created_at: new Date()
    },
    {
        name: 'The Data Wars',
        type: 'event',
        description: 'Corporate conflict that reshaped cyberspace',
        created_by: 'bob_cyberpunk',
        properties: {
            year: 2075,
            duration: '3 years',
            casualties: 'Unknown',
            outcome: 'Corporate dominance established'
        },
        created_at: new Date()
    }
]);

// Insert AI conversation samples
db.ai_conversations.insertMany([
    {
        user: 'alice_writer',
        session_id: 'sess_001',
        messages: [
            {
                role: 'user',
                content: 'Help me describe a crystal cave',
                timestamp: new Date()
            },
            {
                role: 'assistant',
                content: 'The crystal cave sparkles with ethereal light...',
                timestamp: new Date(),
                tokens_used: 150
            }
        ],
        total_tokens: 180,
        model: 'gpt-4',
        created_at: new Date()
    },
    {
        user: 'bob_cyberpunk',
        session_id: 'sess_002',
        messages: [
            {
                role: 'user',
                content: 'Generate cyberpunk street names',
                timestamp: new Date()
            },
            {
                role: 'assistant',
                content: 'Neon Boulevard, Data Stream Avenue, Binary Lane...',
                timestamp: new Date(),
                tokens_used: 120
            }
        ],
        total_tokens: 145,
        model: 'gpt-4',
        created_at: new Date()
    }
]);

// Insert session data
db.sessions.insertMany([
    {
        user: 'alice_writer',
        session_id: 'sess_001',
        start_time: new Date(),
        duration_minutes: 45,
        words_written: 850,
        ai_assists: 5,
        features_used: ['World Builder', 'AI Assistant', 'Character Generator']
    },
    {
        user: 'bob_cyberpunk',
        session_id: 'sess_002',
        start_time: new Date(),
        duration_minutes: 30,
        words_written: 620,
        ai_assists: 3,
        features_used: ['AI Assistant', 'Name Generator']
    }
]);

// Create indexes for better performance
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ email: 1 }, { unique: true });
db.documents.createIndex({ author: 1 });
db.documents.createIndex({ genre: 1 });
db.world_building.createIndex({ created_by: 1 });
db.world_building.createIndex({ type: 1 });
db.ai_conversations.createIndex({ user: 1 });
db.sessions.createIndex({ user: 1 });
db.sessions.createIndex({ session_id: 1 });

print('MongoDB initialization complete!');
print('Collections created: users, documents, world_building, ai_conversations, sessions');
print('Test data inserted successfully');