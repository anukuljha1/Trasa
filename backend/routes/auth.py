from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
import aiosqlite

from ..db import get_db
from ..models import AthleteCreate, AthleteLogin

router = APIRouter(prefix="", tags=["auth"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = "dev-secret"
JWT_ALG = "HS256"


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"


@router.post("/register")
async def register(payload: AthleteCreate, db: aiosqlite.Connection = Depends(get_db)):
	hashed = pwd_ctx.hash(payload.password)
	try:
		await db.execute(
			"INSERT INTO athletes (name, email, password_hash) VALUES (?, ?, ?)",
			(payload.name, payload.email, hashed),
		)
		await db.commit()
	except aiosqlite.IntegrityError:
		raise HTTPException(status_code=400, detail="Email already registered")
	return {"ok": True}


@router.post("/login", response_model=TokenResponse)
async def login(payload: AthleteLogin, db: aiosqlite.Connection = Depends(get_db)):
	cur = await db.execute(
		"SELECT id, password_hash FROM athletes WHERE email = ?",
		(payload.email,),
	)
	row = await cur.fetchone()
	if not row:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
	if not pwd_ctx.verify(payload.password, row[1]):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	token = jwt.encode(
		{"sub": payload.email, "exp": datetime.utcnow() + timedelta(hours=12)},
		JWT_SECRET,
		algorithm=JWT_ALG,
	)
	return TokenResponse(access_token=token)
