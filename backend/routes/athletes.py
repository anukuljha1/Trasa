from fastapi import APIRouter, Depends, HTTPException, Query
import aiosqlite
import json
from typing import Dict, Any

from ..db import get_db

router = APIRouter(prefix="", tags=["athletes"])


@router.get("/profile")
async def get_profile(email: str = Query(...), db: aiosqlite.Connection = Depends(get_db)):
	cur = await db.execute("SELECT id, name, email, created_at FROM athletes WHERE email = ?", (email,))
	row = await cur.fetchone()
	if not row:
		raise HTTPException(status_code=404, detail="Athlete not found")
	return dict(row)


@router.put("/profile")
async def update_profile(payload: Dict[str, Any], db: aiosqlite.Connection = Depends(get_db)):
	email = payload.get('email')
	name = payload.get('name')
	if not email:
		raise HTTPException(status_code=400, detail="email required")
	if name is None:
		raise HTTPException(status_code=400, detail="name required")
	cur = await db.execute("UPDATE athletes SET name = ? WHERE email = ?", (name, email))
	await db.commit()
	if cur.rowcount == 0:
		raise HTTPException(status_code=404, detail="Athlete not found")
	return {"ok": True}


@router.get("/profile/best")
async def get_best_results(email: str = Query(...), db: aiosqlite.Connection = Depends(get_db)):
	# Find athlete
	cur = await db.execute("SELECT id FROM athletes WHERE email = ?", (email,))
	athlete = await cur.fetchone()
	if not athlete:
		raise HTTPException(status_code=404, detail="Athlete not found")
	athlete_id = athlete[0]
	# Fetch results
	cur = await db.execute(
		"SELECT test_type, metrics_json FROM results WHERE athlete_id = ?",
		(athlete_id,),
	)
	rows = await cur.fetchall()
	best = {}
	for row in rows:
		try:
			metrics = json.loads(row[1]) if isinstance(row[1], str) else row[1]
		except Exception:
			metrics = {}
		if row[0] == 'situps':
			val = metrics.get('reps', 0)
			if 'situps' not in best or val > best['situps']['reps']:
				best['situps'] = { 'reps': val }
		elif row[0] == 'jump':
			val = metrics.get('peakDisplacementPx', 0)
			if 'jump' not in best or val > best['jump']['peakDisplacementPx']:
				best['jump'] = { 'peakDisplacementPx': val }
	return best
