from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorClient] = None  # This should also be AsyncIOMotorClient for consistency

    @staticmethod
    async def connect(db_url: str, db_name: str):
        try:
            Database.client = AsyncIOMotorClient(db_url)
            Database.db = Database.client[db_name]
            # This command forces a round trip to the server.
            await Database.db.command("ping")
            print("Connected to MongoDB")
        except OperationFailure as e:
            # Extracting error message directly from the exception
            error_msg = str(e)
            print(f"Failed to connect to MongoDB: {error_msg}")
        except Exception as e:
            # For any other exceptions, print a simplified message
            print(f"Failed to connect to MongoDB: {e}")

    @staticmethod
    async def close():
        await Database.client.close()
        print("Disconnected from MongoDB")
