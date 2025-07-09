from fastapi import APIRouter, HTTPException
from app.AI.agent import score_resume_workflow, tailored_answer_workflow, comprehensive_workflow
from app.AI.schemas import ResumeScoreInputLegacy, TailoredAnswerInputLegacy
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

# For comprehensive workflow (resume_text, job_posting_url, questions)
class ComprehensiveInputLegacy(BaseModel):
    resume_text: str
    job_posting_url: str
    questions: list = None


@router.post("/score")
def score_resume(request: ResumeScoreInputLegacy):
    try:
        result = score_resume_workflow(request.resume_text, request.job_posting_url)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tailored-answers")
def get_tailored_answers(request: TailoredAnswerInputLegacy):
    result = tailored_answer_workflow(request.profile_text, request.job_posting_url, request.questions)
    return {"result": result}

@router.post("/comprehensive")
def comprehensive(request: ComprehensiveInputLegacy):
    result = comprehensive_workflow(request.resume_text, request.job_posting_url, request.questions)
    return {"result": result}
