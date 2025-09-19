from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .db import init_db
from .routes import auth, results, athletes
from .routes import mongo_auth, stats

app = FastAPI(title="sai-sports-assess API")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
	await init_db()


app.include_router(auth.router)
app.include_router(results.router)
app.include_router(athletes.router)
app.include_router(mongo_auth.router)
app.include_router(stats.router)

# Serve uploaded files
UPLOADS_DIR = Path(__file__).parent / "uploads"
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/")
async def root():
	return {"status": "ok"}
