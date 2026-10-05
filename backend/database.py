from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.scans.create_index("user_id")
    await db.scans.create_index("scanned_at")
    await db.reviews.create_index([("product_id", 1), ("user_id", 1)])
    await db.reviews.create_index([("product_name", 1), ("status", 1), ("created_at", -1)])
    print(f"✅ Connected to MongoDB: {settings.MONGO_DB}")

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    return db
