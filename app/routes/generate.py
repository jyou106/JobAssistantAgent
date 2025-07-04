from fastapi import APIRouter
from pydantic import BaseModel
from app.huggingface_client import call_huggingface

router = APIRouter()

class GenerateRequest(BaseModel):
    user_profile: str
    job_description: str

class GenerateResponse(BaseModel):
    generated_text: str

@router.post("/api/generate/answer", response_model=GenerateResponse)
def generate_answer(request: GenerateRequest):
    prompt = f"User profile: {request.user_profile}\nJob description: {request.job_description}"
    generated_text = call_huggingface(prompt)
    return GenerateResponse(generated_text=generated_text)
