from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta

from mongo import get_mongo_db

router = APIRouter(prefix="", tags=["auth"])

# Add mongo prefix routes for frontend compatibility
mongo_router = APIRouter(prefix="/mongo", tags=["mongo-auth"])

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
async def register(payload: RegisterPayload):
    try:
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
            "role": "user",
            "created_at": datetime.utcnow().isoformat()
        })
        return {"ok": True}
    except HTTPException as he:
        # Preserve deliberate HTTP errors (e.g., 400 duplicate email)
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/login")
async def login(payload: LoginPayload):
    try:
        db = get_mongo_db()
        users = db["users"]
        user = await users.find_one({"email": payload.email})
        if not user or not pwd_ctx.verify(payload.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        # Include role in token
        user_role = user.get("role", "user")
        token = jwt.encode({
            "sub": payload.email, 
            "role": user_role,
            "exp": datetime.utcnow() + timedelta(hours=12)
        }, JWT_SECRET, algorithm=JWT_ALG)
        return {"access_token": token, "token_type": "bearer", "role": user_role}
    except HTTPException as he:
        # Do not wrap auth errors as 500
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Add mongo prefix routes for frontend compatibility
@mongo_router.post("/register")
async def mongo_register(payload: RegisterPayload):
	return await register(payload)

@mongo_router.post("/login")
async def mongo_login(payload: LoginPayload):
	return await login(payload)
