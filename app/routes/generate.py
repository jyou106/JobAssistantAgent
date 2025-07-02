from fastapi import APIRouter
from pydantic import BaseModel
from app.agent_core import generate_tailored_answer

router = APIRouter()

class GenerateRequest(BaseModel):
    user_profile: str
    job_description: str

@router.post("/answer")
def generate_answer(request: GenerateRequest):
    response = generate_tailored_answer(request.user_profile, request.job_description)
    return {"answer": response}
