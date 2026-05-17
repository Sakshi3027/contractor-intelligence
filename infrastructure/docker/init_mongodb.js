// Switch to our database
db = db.getSiblingDB('contractor_raw');

// =====================
// RAW BUSINESS PROFILES
// Unstructured scraped data
// =====================
db.createCollection('raw_businesses', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['google_place_id', 'name', 'scraped_at'],
            properties: {
                google_place_id: { bsonType: 'string' },
                name: { bsonType: 'string' },
                scraped_at: { bsonType: 'date' }
            }
        }
    }
});

// =====================
// AGENT RESEARCH NOTES
// CrewAI agent outputs
// =====================
db.createCollection('agent_research', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['business_id', 'created_at'],
            properties: {
                business_id: { bsonType: 'string' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

// =====================
// EMAIL DRAFTS
// LLM generated emails
// =====================
db.createCollection('email_drafts', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['business_id', 'created_at'],
            properties: {
                business_id: { bsonType: 'string' },
                created_at: { bsonType: 'date' }
            }
        }
    }
});

// =====================
// SCRAPED WEBSITE DATA
// Raw playwright output
// =====================
db.createCollection('scraped_websites', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['business_id', 'url', 'scraped_at'],
            properties: {
                business_id: { bsonType: 'string' },
                url: { bsonType: 'string' },
                scraped_at: { bsonType: 'date' }
            }
        }
    }
});

// =====================
// INDEXES
// =====================
db.raw_businesses.createIndex({ google_place_id: 1 }, { unique: true });
db.raw_businesses.createIndex({ scraped_at: -1 });
db.raw_businesses.createIndex({ 'google_data.rating': -1 });

db.agent_research.createIndex({ business_id: 1 });
db.agent_research.createIndex({ created_at: -1 });

db.email_drafts.createIndex({ business_id: 1 });
db.email_drafts.createIndex({ status: 1 });
db.email_drafts.createIndex({ created_at: -1 });

db.scraped_websites.createIndex({ business_id: 1 });
db.scraped_websites.createIndex({ scraped_at: -1 });

print('MongoDB collections and indexes created successfully');