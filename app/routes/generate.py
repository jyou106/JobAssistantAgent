# app/routes/generate.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class GenerateRequest(BaseModel):
    user_profile: str
    job_description: str

@router.post("/answer")
def generate_answer(request: GenerateRequest):
    return {
        "answer": f"This is a mocked answer based on profile '{request.user_profile}' and job '{request.job_description}'"
    }
