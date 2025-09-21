from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime
import logging

_MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
_MONGO_DB = os.getenv("MONGO_DB", "sai_sports_assess")

_client: AsyncIOMotorClient | None = None
logger = logging.getLogger(__name__)


def get_mongo_client() -> AsyncIOMotorClient:
	global _client
	if _client is None:
		try:
			_client = AsyncIOMotorClient(_MONGO_URI)
			logger.info(f"Connected to MongoDB at {_MONGO_URI}")
		except Exception as e:
			logger.error(f"Failed to connect to MongoDB: {e}")
			raise
	return _client


def get_mongo_db():
	try:
		return get_mongo_client()[_MONGO_DB]
	except Exception as e:
		logger.error(f"Failed to get database {_MONGO_DB}: {e}")
		raise


async def init_mongo_collections():
	"""Initialize MongoDB collections with proper indexes"""
	db = get_mongo_db()
	
	# Create indexes for better performance
	await db.users.create_index("email", unique=True)
	await db.results.create_index("athlete_email")
	await db.results.create_index("created_at")
	await db.audit_logs.create_index("created_at")
