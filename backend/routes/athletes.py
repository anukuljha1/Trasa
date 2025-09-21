from fastapi import APIRouter, Depends, HTTPException, Query
import json
from typing import Dict, Any
from bson import ObjectId

from mongo import get_mongo_db
from auth import get_current_user

router = APIRouter(prefix="", tags=["athletes"])


@router.get("/profile")
async def get_profile(email: str = Query(...), current_user: dict = Depends(get_current_user)):
	try:
		db = get_mongo_db()
		user = await db.users.find_one({"email": email})
		if not user:
			raise HTTPException(status_code=404, detail="Athlete not found")
		
		# Convert ObjectId to string for JSON serialization
		user["_id"] = str(user["_id"])
		return {
			"id": user["_id"],
			"name": user["name"],
			"email": user["email"],
			"created_at": user["created_at"]
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/profile")
async def update_profile(payload: Dict[str, Any], current_user: dict = Depends(get_current_user)):
	try:
		email = payload.get('email')
		name = payload.get('name')
		if not email:
			raise HTTPException(status_code=400, detail="email required")
		if name is None:
			raise HTTPException(status_code=400, detail="name required")
		
		db = get_mongo_db()
		result = await db.users.update_one(
			{"email": email},
			{"$set": {"name": name}}
		)
		if result.matched_count == 0:
			raise HTTPException(status_code=404, detail="Athlete not found")
		return {"ok": True}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/profile/best")
async def get_best_results(email: str = Query(...), current_user: dict = Depends(get_current_user)):
	try:
		db = get_mongo_db()
		
		# Check if user exists
		user = await db.users.find_one({"email": email})
		if not user:
			raise HTTPException(status_code=404, detail="Athlete not found")
		
		# Fetch results for this athlete
		cursor = db.results.find({"athlete_email": email})
		best = {}
		
		async for result in cursor:
			try:
				metrics = json.loads(result["metrics_json"]) if isinstance(result["metrics_json"], str) else result["metrics_json"]
			except Exception:
				metrics = {}
			
			test_type = result["test_type"]
			if test_type == 'situps':
				val = metrics.get('reps', 0)
				if 'situps' not in best or val > best['situps']['reps']:
					best['situps'] = { 'reps': val }
			elif test_type == 'jump':
				val = metrics.get('peakDisplacementPx', 0)
				if 'jump' not in best or val > best['jump']['peakDisplacementPx']:
					best['jump'] = { 'peakDisplacementPx': val }
		
		return best
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
