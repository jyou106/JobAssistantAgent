from fastapi import APIRouter, HTTPException
from app.AI.agent import score_resume_workflow, tailored_answer_workflow
from app.AI.schemas import ResumeScoreInputLegacy, TailoredAnswerInputLegacy
from pydantic import BaseModel, HttpUrl
import asyncio
from app.AI.scorer import score_resume

router = APIRouter()

class ScoreRequest(BaseModel):
    resume_text: str
    job_posting_url: HttpUrl  # validates URL format

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


