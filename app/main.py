import logging
from fastapi import FastAPI, HTTPException
from uuid import uuid4

from app.routes.resume import router as resume_router
from app.routes.generate import router as generate_router
from pydantic import BaseModel

# Setup logger
logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# In-memory "database" for demo
fake_users_db = {}

# Pydantic models for User endpoints
class UserProfile(BaseModel):
    name: str
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "name",
                "email": "name@example.com"
            }
        }

class UserResponse(UserProfile):
    userId: str

    class Config:
        json_schema_extra = {
            "example": {
                "userId": "123e4567-e89b-12d3-a456-426614174000",
                "name": "name",
                "email": "name@example.com"
            }
        }

# User endpoints
@app.post("/api/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserProfile):
    user_id = str(uuid4())
    fake_users_db[user_id] = user.dict()
    logger.info(f"Created user {user_id}: {user.dict()}")
    return UserResponse(userId=user_id, **user.dict())

@app.get("/api/users/{userId}", response_model=UserResponse)
async def get_user(userId: str):
    user = fake_users_db.get(userId)
    if not user:
        logger.warning(f"User {userId} not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"Fetched user {userId}")
    return UserResponse(userId=userId, **user)

# Include other routers for resume and generate endpoints
app.include_router(resume_router)
app.include_router(generate_router)
