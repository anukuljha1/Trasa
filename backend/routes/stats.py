from fastapi import APIRouter, Depends
import aiosqlite

from ..db import get_db
from ..mongo import get_mongo_db

router = APIRouter(prefix="", tags=["stats"])


@router.get("/stats")
async def get_stats(db: aiosqlite.Connection = Depends(get_db)):
	# SQLite counts
	cur = await db.execute("SELECT COUNT(*) FROM athletes")
	athletes_count = (await cur.fetchone())[0]
	cur = await db.execute("SELECT COUNT(*) FROM results")
	results_count = (await cur.fetchone())[0]
	# Mongo counts
	db_m = get_mongo_db()
	users_count = await db_m["users"].count_documents({})
	return {
		"sqlite": {"athletes": athletes_count, "results": results_count},
		"mongo": {"users": users_count}
	}
