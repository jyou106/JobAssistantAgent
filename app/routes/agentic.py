from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from app.AI.true_agentic_agent import autonomous_career_workflow
import logging

router = APIRouter()

class AgenticRequest(BaseModel):
    user_id: str
    resume_text: str
    job_url: Optional[HttpUrl] = None
    questions: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "resume_text": "Your complete resume text here...",
                "job_url": "https://example-job-posting.com",
                "questions": [
                    "Why are you interested in this position?",
                    "What is your greatest strength?"
                ]
            }
        }

class AgenticResponse(BaseModel):
    success: bool
    autonomous_analysis: Optional[Dict[str, Any]] = None
    agent_goals: Optional[List[str]] = None
    identified_obstacles: Optional[List[str]] = None
    agent_actions: Optional[List[str]] = None
    execution_results: Optional[Dict[str, Any]] = None
    learning_applied: Optional[bool] = None
    strategy_adaptation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    fallback_to_basic: Optional[bool] = None

@router.post("/autonomous-workflow", response_model=AgenticResponse)
async def autonomous_career_assistance(request: AgenticRequest):
    """
    🤖 **True Agentic Career Assistant**
    
    This is your most powerful AI agent that:
    - Makes autonomous decisions about your career
    - Learns from interactions and adapts strategies
    - Provides comprehensive career guidance
    - Tracks progress and identifies goals
    - Suggests personalized improvements
    
    **Features:**
    - Autonomous situation analysis
    - Goal identification and obstacle detection
    - Strategy adaptation based on outcomes
    - Memory system that learns over time
    - Multi-action execution (resume analysis, job recommendations, skill development)
    """
    try:
        # Convert HttpUrl to string if provided
        job_url_str = str(request.job_url) if request.job_url else None
        
        # Call the autonomous workflow
        result = autonomous_career_workflow(
            user_id=request.user_id,
            resume_text=request.resume_text,
            job_url=job_url_str,
            questions=request.questions
        )
        
        if result.get("success"):
            return AgenticResponse(**result)
        else:
            # Handle failure cases
            return AgenticResponse(
                success=False,
                error=result.get("error", "Unknown error in autonomous workflow"),
                fallback_to_basic=result.get("fallback_to_basic", False)
            )
            
    except Exception as e:
        logging.error(f"Autonomous workflow failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Autonomous career workflow failed: {str(e)}"
        )

@router.post("/quick-analysis")
async def quick_career_analysis(request: AgenticRequest):
    """
    ⚡ **Quick Career Analysis**
    
    A simplified version of the autonomous workflow for faster responses.
    Focuses on immediate insights and recommendations.
    """
    try:
        # For quick analysis, we'll call the autonomous workflow but focus on key insights
        job_url_str = str(request.job_url) if request.job_url else None
        
        result = autonomous_career_workflow(
            user_id=request.user_id,
            resume_text=request.resume_text,
            job_url=job_url_str,
            questions=request.questions
        )
        
        if result.get("success"):
            # Extract key insights for quick response
            quick_insights = {
                "success": True,
                "key_strengths": result.get("autonomous_analysis", {}).get("opportunities", [])[:3],
                "improvement_areas": result.get("autonomous_analysis", {}).get("skill_gaps", [])[:3],
                "recommended_focus": result.get("autonomous_analysis", {}).get("recommended_focus"),
                "agent_goals": result.get("agent_goals", [])[:2],
                "quick_tips": result.get("execution_results", {}).get("resume_and_job_matching", {}).get("resume_analysis", {})
            }
            return quick_insights
        else:
            return {"success": False, "error": result.get("error")}
            
    except Exception as e:
        logging.error(f"Quick analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")
