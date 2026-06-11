from fastapi import APIRouter, HTTPException
from app.AI.agent import score_resume_workflow, tailored_answer_workflow
from app.AI.schemas import ResumeScoreInputLegacy, TailoredAnswerInputLegacy
from pydantic import BaseModel, HttpUrl
from typing import Optional
import asyncio
from app.AI.scorer import score_resume

router = APIRouter()

class ScoreRequest(BaseModel):
    resume_text: str
    job_posting_url: Optional[HttpUrl] = None  # Made optional
    job_description: Optional[str] = None  # NEW: Direct job description input

class ScoreResponse(BaseModel):
    match_score: float
    insights: list[str]

@router.post("/score")
async def score_route(payload: ScoreRequest):
    try:
        print("Received scoring request")
        
        # Validate input
        if not payload.job_description and not payload.job_posting_url:
            raise HTTPException(
                status_code=400, 
                detail="Either job_posting_url or job_description is required"
            )
        
        # Use direct job description if provided, otherwise scrape
        if payload.job_description:
            print("Using direct job description input")
            job_text = payload.job_description
        else:
            print(f"Scraping URL: {payload.job_posting_url}")
            from app.AI.scraper import scrape_job_description
            job_text = scrape_job_description(str(payload.job_posting_url))
            
            if not job_text or len(job_text.strip()) < 100:
                print("Scraping returned insufficient content")
                raise HTTPException(
                    status_code=400,
                    detail="Could not scrape job description. Please provide job_description directly."
                )
        
        # Call the scoring function with resume and job text
        result = await asyncio.to_thread(score_resume, payload.resume_text, job_text)
        print("Scoring complete:", result)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print("Exception during scoring:", e)
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

@router.post("/tailored-answers")
def get_tailored_answers(request: TailoredAnswerInputLegacy):
    result = tailored_answer_workflow(
        request.profile_text,
        request.job_posting_url,
        request.questions
    )

    if isinstance(result, dict):
        if result.get("success"):
            return {"result": result["data"]}
        else:
            return {
                "error": result.get("error", "Unknown error occurred"),
                "raw_output": result.get("raw_output")
            }
    else:
        print("[TAILORED] Unexpected result type:", type(result))
        raise HTTPException(status_code=500, detail="Unexpected result format from tailored_answer_workflow")