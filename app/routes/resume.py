from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Pydantic model with example
class ResumeRequest(BaseModel):
    resume_text: str

    class Config:
        json_schema_extra  = {
            "example": {
                "resume_text": "Experienced software engineer with a focus on backend development, Python, and system design."
            }
        }

@router.post("/api/resume/analyze")
def analyze_resume(request: ResumeRequest):
    # You can plug in your GPT4All analysis logic here later
    return {
        "score": 85,
        "feedback": "Your resume demonstrates strong backend experience. Highlight specific projects and metrics for greater impact."
    }
