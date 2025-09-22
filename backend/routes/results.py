from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi import status
from typing import Optional
from pathlib import Path
import json
from datetime import datetime
from bson import ObjectId

from mongo import get_mongo_db
from auth import get_current_user, require_admin

router = APIRouter(prefix="", tags=["results"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/results/mine")
async def get_my_results(current_user: dict = Depends(get_current_user)):
	try:
		db = get_mongo_db()
		cursor = db.results.find({"athlete_email": current_user.get("email")}).sort("created_at", -1)
		items = []
		async for doc in cursor:
			# normalize fields for frontend
			doc_id = str(doc.get("_id")) if doc.get("_id") else None
			items.append({
				"id": doc_id,
				"email": doc.get("athlete_email"),
				"name": doc.get("athlete_name", ""),
				"test_type": doc.get("test_type"),
				"metrics_json": doc.get("metrics_json"),
				"video_path": doc.get("video_path"),
				"status": doc.get("status", "pending"),
				"created_at": doc.get("created_at"),
			})
		return items
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/results")
async def submit_result(
	athlete_email: str = Form(...),
	test_type: str = Form(...),
	metrics_json: str = Form(...),
	video: Optional[UploadFile] = File(None),
	current_user: dict = Depends(get_current_user)
):
	try:
		db = get_mongo_db()
		
		# Check if user exists
		user = await db.users.find_one({"email": athlete_email})
		if not user:
			raise HTTPException(status_code=404, detail="Athlete not found")

		video_path: Optional[str] = None
		if video is not None:
			filename = f"{user['_id']}_{test_type}_{video.filename}"
			dest = UPLOAD_DIR / filename
			with open(dest, "wb") as f:
				f.write(await video.read())
			video_path = dest.name

		# Insert result into MongoDB
		result_doc = {
			"athlete_email": athlete_email,
			"athlete_name": user["name"],
			"test_type": test_type,
			"metrics_json": metrics_json,
			"video_path": video_path,
			"status": "pending",
			"created_at": datetime.utcnow().isoformat()
		}
		
		await db.results.insert_one(result_doc)
		return {"ok": True}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/admin/results")
async def list_results(current_user: dict = Depends(require_admin)):
	try:
		db = get_mongo_db()
		
		# Get all results with user info
		cursor = db.results.find({}).sort("created_at", -1)
		results = []
		async for result in cursor:
			# Convert ObjectId to string for JSON serialization
			result["_id"] = str(result["_id"])
			# Also convert any other ObjectId fields if they exist
			if "athlete_id" in result and isinstance(result["athlete_id"], ObjectId):
				result["athlete_id"] = str(result["athlete_id"])
			results.append(result)
		
		return results
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/admin/results/{result_id}/{action}")
async def decide_result(result_id: str, action: str, current_user: dict = Depends(require_admin)):
	try:
		if action not in {"accept", "reject"}:
			raise HTTPException(status_code=400, detail="Invalid action")
		
		db = get_mongo_db()
		status_val = "accepted" if action == "accept" else "rejected"
		
		# Update result status
		await db.results.update_one(
			{"_id": ObjectId(result_id)},
			{"$set": {"status": status_val}}
		)
		
		# Log the action
		audit_log = {
			"action": "admin_decision",
			"details": json.dumps({"result_id": result_id, "action": action}),
			"created_at": datetime.utcnow().isoformat()
		}
		await db.audit_logs.insert_one(audit_log)
		
		return {"ok": True}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
