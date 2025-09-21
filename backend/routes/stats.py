from fastapi import APIRouter, HTTPException, Depends

from mongo import get_mongo_db
from auth import require_admin

router = APIRouter(prefix="", tags=["stats"])


@router.get("/stats")
async def get_stats(current_user: dict = Depends(require_admin)):
	try:
		db = get_mongo_db()
		
		# MongoDB counts
		users_count = await db.users.count_documents({})
		results_count = await db.results.count_documents({})
		audit_logs_count = await db.audit_logs.count_documents({})
		
		return {
			"users": users_count,
			"results": results_count,
			"audit_logs": audit_logs_count
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
