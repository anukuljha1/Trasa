import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def seed_test_user():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sai_sports_assess"]
    users = db["users"]
    
    # Test user credentials
    test_email = "test@trasa.com"
    test_password = "test123"
    test_name = "Test User"
    
    # Check if user exists
    existing = await users.find_one({"email": test_email})
    if existing:
        print(f"Test user already exists: {test_email}")
        return
    
    # Create test user
    hashed_password = pwd_ctx.hash(test_password)
    await users.insert_one({
        "email": test_email,
        "name": test_name,
        "password_hash": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    })
    
    print(f"Test user created successfully!")
    print(f"Email: {test_email}")
    print(f"Password: {test_password}")
    print(f"Name: {test_name}")

if __name__ == "__main__":
    asyncio.run(seed_test_user())
