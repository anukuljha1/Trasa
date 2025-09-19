import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "sports.db"

SCHEMA_SQL = """
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS athletes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	email TEXT UNIQUE NOT NULL,
	password_hash TEXT NOT NULL,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS results (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	athlete_id INTEGER NOT NULL REFERENCES athletes(id) ON DELETE CASCADE,
	test_type TEXT NOT NULL,
	metrics_json TEXT NOT NULL,
	video_path TEXT,
	status TEXT NOT NULL DEFAULT 'pending',
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	action TEXT NOT NULL,
	actor_email TEXT,
	details TEXT,
	created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db() -> None:
	async with aiosqlite.connect(DB_PATH.as_posix()) as db:
		await db.executescript(SCHEMA_SQL)
		await db.commit()


async def get_db():
	db = await aiosqlite.connect(DB_PATH.as_posix())
	db.row_factory = aiosqlite.Row
	try:
		yield db
	finally:
		await db.close()
