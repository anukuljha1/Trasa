from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

from ..mongo import get_mongo_db

router = APIRouter(prefix="/mongo", tags=["auth-mongo"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = "dev-secret"
JWT_ALG = "HS256"


class RegisterPayload(BaseModel):
	email: EmailStr
	name: str
	password: str


class LoginPayload(BaseModel):
	email: EmailStr
	password: str


@router.post("/register")
async def mongo_register(payload: RegisterPayload):
	db = get_mongo_db()
	users = db["users"]
	existing = await users.find_one({"email": payload.email})
	if existing:
		raise HTTPException(status_code=400, detail="Email already registered")
	hashed = pwd_ctx.hash(payload.password)
	await users.insert_one({
		"email": payload.email,
		"name": payload.name,
		"password_hash": hashed,
		"created_at": datetime.utcnow().isoformat()
	})
	return {"ok": True}


@router.post("/login")
async def mongo_login(payload: LoginPayload):
	db = get_mongo_db()
	users = db["users"]
	user = await users.find_one({"email": payload.email})
	if not user or not pwd_ctx.verify(payload.password, user.get("password_hash", "")):
		raise HTTPException(status_code=401, detail="Invalid credentials")
	token = jwt.encode({"sub": payload.email, "exp": datetime.utcnow() + timedelta(hours=12)}, JWT_SECRET, algorithm=JWT_ALG)
	return {"access_token": token, "token_type": "bearer"}
