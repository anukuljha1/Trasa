import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_admin_user():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sai_sports_assess"]
    users = db["users"]
    
    # Admin user credentials
    admin_email = "admin@trasa.com"
    admin_password = "admin123"
    admin_name = "TRASA Admin"
    
    # Check if admin exists
    existing = await users.find_one({"email": admin_email})
    if existing:
        print(f"Admin user already exists: {admin_email}")
        return
    
    # Create admin user
    hashed_password = pwd_ctx.hash(admin_password)
    await users.insert_one({
        "email": admin_email,
        "name": admin_name,
        "password_hash": hashed_password,
        "role": "admin",
        "created_at": datetime.utcnow().isoformat()
    })
    
    print(f"Admin user created successfully!")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
    print(f"Name: {admin_name}")

if __name__ == "__main__":
    asyncio.run(seed_admin_user())
