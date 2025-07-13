from fastapi import APIRouter, HTTPException
from app.AI.agent import score_resume_workflow, tailored_answer_workflow
from app.AI.schemas import ResumeScoreInputLegacy, TailoredAnswerInputLegacy
from pydantic import BaseModel, HttpUrl
import asyncio
from app.AI.scorer import score_resume
import uuid

router = APIRouter()

class ScoreRequest(BaseModel):
    resume_text: str
    job_posting_url: HttpUrl  # validates URL format

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    created_at: str

# In-memory storage for users (in production, use a database)
users_db = {}

@router.post("/create-user")
async def create_user(user_data: UserCreate):
    """
    Create a new user profile for the job assistant system.
    
    This endpoint allows users to register with the system and provide
    their basic information for personalized assistance.
    """
    try:
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Create user object
        user = {
            "user_id": user_id,
            "name": user_data.name,
            "email": user_data.email,
            "created_at": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
        
        # Store user in memory (in production, save to database)
        users_db[user_id] = user
        
        return UserResponse(**user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.get("/user/{user_id}")
async def get_user(user_id: str):
    """
    Retrieve user profile by user ID.
    """
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**users_db[user_id])

@router.get("/users")
async def list_users():
    """
    List all users (for development/testing purposes).
    """
    return {"users": list(users_db.values())}

@router.post("/score")
async def score_route(payload: ScoreRequest):
    try:
        print("Received scoring request")
        # Convert job_posting_url to str before passing
        result = await asyncio.to_thread(score_resume, payload.resume_text, str(payload.job_posting_url))
        print("Scoring complete:", result)
        return result
    except Exception as e:
        print("Exception during scoring:", e)
        raise HTTPException(status_code=500, detail="Scoring workflow did not return valid JSON")


@router.post("/tailored-answers")
def get_tailored_answers(request: TailoredAnswerInputLegacy):
    result = tailored_answer_workflow(
        request.profile_text,
        request.job_posting_url,
        request.questions
    )

    # Check if the result is a dict and structured as expected
    if isinstance(result, dict):
        if result.get("success"):
            return {"result": result["data"]}
        else:
            return {
                "error": result.get("error", "Unknown error occurred"),
                "raw_output": result.get("raw_output")
            }
    else:
        # fallback for unexpected return type (e.g. str)
        print("[TAILORED] Unexpected result type:", type(result))
        raise HTTPException(status_code=500, detail="Unexpected result format from tailored_answer_workflow")


