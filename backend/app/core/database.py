from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB."""
    if not settings.MONGODB_URI:
        logger.warning("MONGODB_URI is not set. MongoDB connection skipped.")
        return
    
    try:
        logger.info("Connecting to MongoDB...")
        db.client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        db.db = db.client[settings.MONGODB_DATABASE]
        
        # Verify connection
        await db.db.command("ping")
        logger.info("Successfully connected to MongoDB!")
        
        # Create indexes
        await db.db.users.create_index("email", unique=True)
        await db.db.conversations.create_index("user_id")
        await db.db.conversations.create_index([("user_id", 1), ("updated_at", -1)])
        await db.db.messages.create_index("conversation_id")
        await db.db.images.create_index("conversation_id")
        await db.db.analyses.create_index("conversation_id")
        logger.info("MongoDB indexes verified.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Reset to None so the application knows the connection failed but doesn't crash
        db.client = None
        db.db = None

async def close_mongo_connection():
    """Close MongoDB connection."""
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        logger.info("MongoDB connection closed.")

def get_db():
    """Dependency to get the database instance."""
    return db.db
