from fastapi import APIRouter
from pydantic import BaseModel
from app.gpt4all_client import call_gpt4all

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "What are good projects for a beginner Python programmer?"
            }
        }


class GenerateResponse(BaseModel):
    generated_text: str

@router.post("/api/generate/answer", response_model=GenerateResponse)
def generate_answer(request: GenerateRequest):
    response = call_gpt4all(request.prompt)
    return GenerateResponse(generated_text=response)
