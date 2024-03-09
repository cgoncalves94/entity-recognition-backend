from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure


class Database:
    client: Optional[AsyncIOMotorClient] = None  # type: ignore
    db: Optional[AsyncIOMotorClient] = None  # type: ignore

    @staticmethod
    async def connect(db_url: str, db_name: str):
        """
        Connects to the MongoDB database.

        Args:
          db_url (str): The URL of the MongoDB server.
          db_name (str): The name of the database to connect to.
        """
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
    def close():
        """
        Closes the connection to the MongoDB database.
        """
        if Database.client is not None:
            Database.client.close()
            Database.client = None
            print("Disconnected from MongoDB")
