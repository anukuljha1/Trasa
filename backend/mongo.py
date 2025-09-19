from motor.motor_asyncio import AsyncIOMotorClient
import os

_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
_MONGO_DB = os.getenv("MONGO_DB", "sai_sports_assess")

_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
	global _client
	if _client is None:
		_client = AsyncIOMotorClient(_MONGO_URI)
	return _client


def get_mongo_db():
	return get_mongo_client()[_MONGO_DB]
