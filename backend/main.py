import sys
from pathlib import Path

# Add the backend directory to Python path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from mongo import init_mongo_collections
from routes import mongo_auth, results, athletes
from routes import stats, ml_analysis

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
	await init_mongo_collections()


app.include_router(mongo_auth.router)
app.include_router(mongo_auth.mongo_router)
app.include_router(results.router)
app.include_router(athletes.router)
app.include_router(stats.router)
app.include_router(ml_analysis.router)

# Serve uploaded files
UPLOADS_DIR = Path(__file__).parent / "uploads"
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/")
async def root():
	return {"status": "ok"}
