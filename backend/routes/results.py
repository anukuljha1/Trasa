from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi import status
from typing import Optional
from pathlib import Path
import json
import aiosqlite

from ..db import get_db

router = APIRouter(prefix="", tags=["results"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/results")
async def submit_result(
	athlete_email: str = Form(...),
	test_type: str = Form(...),
	metrics_json: str = Form(...),
	video: Optional[UploadFile] = File(None),
	db: aiosqlite.Connection = Depends(get_db),
):
	# Resolve athlete id
	cur = await db.execute("SELECT id FROM athletes WHERE email = ?", (athlete_email,))
	athlete = await cur.fetchone()
	if not athlete:
		raise HTTPException(status_code=404, detail="Athlete not found")

	video_path: Optional[str] = None
	if video is not None:
		filename = f"{athlete[0]}_{test_type}_{video.filename}"
		dest = UPLOAD_DIR / filename
		with open(dest, "wb") as f:
			f.write(await video.read())
		video_path = dest.name

	await db.execute(
		"INSERT INTO results (athlete_id, test_type, metrics_json, video_path) VALUES (?, ?, ?, ?)",
		(athlete[0], test_type, metrics_json, video_path),
	)
	await db.commit()
	return {"ok": True}


@router.get("/admin/results")
async def list_results(db: aiosqlite.Connection = Depends(get_db)):
	cur = await db.execute(
		"""
		SELECT r.id, a.name, a.email, r.test_type, r.metrics_json, r.video_path, r.status, r.created_at
		FROM results r JOIN athletes a ON r.athlete_id = a.id
		ORDER BY r.created_at DESC
		"""
	)
	rows = await cur.fetchall()
	return [dict(row) for row in rows]


@router.post("/admin/results/{result_id}/{action}")
async def decide_result(result_id: int, action: str, db: aiosqlite.Connection = Depends(get_db)):
	if action not in {"accept", "reject"}:
		raise HTTPException(status_code=400, detail="Invalid action")
	status_val = "accepted" if action == "accept" else "rejected"
	await db.execute("UPDATE results SET status = ? WHERE id = ?", (status_val, result_id))
	await db.execute(
		"INSERT INTO audit_logs (action, details) VALUES (?, ?)",
		("admin_decision", json.dumps({"result_id": result_id, "action": action})),
	)
	await db.commit()
	return {"ok": True}
