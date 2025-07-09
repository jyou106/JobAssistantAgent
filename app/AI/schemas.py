from typing import List, Dict, Optional
from pydantic import BaseModel, Field

# ============================================================================
# INPUT DATA CONTRACTS
# ============================================================================

class WorkExperience(BaseModel):
    """Individual work experience entry"""
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    start_date: str = Field(..., description="Start date (YYYY-MM or YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM or YYYY-MM-DD), None for current")
    description: str = Field(..., description="Job description and achievements")
    skills_used: List[str] = Field(default=[], description="Skills used in this role")

class Education(BaseModel):
    """Education entry"""
    institution: str = Field(..., description="School/University name")
    degree: str = Field(..., description="Degree type (e.g., Bachelor's, Master's)")
    field_of_study: str = Field(..., description="Major/Field of study")
    graduation_date: str = Field(..., description="Graduation date (YYYY-MM)")
    gpa: Optional[float] = Field(None, description="GPA if available")

class UserProfile(BaseModel):
    """Complete user profile for resume scoring and tailored answers"""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State/Country")
    
    # Professional Information
    summary: str = Field(..., description="Professional summary/objective")
    work_history: List[WorkExperience] = Field(..., description="List of work experiences")
    education: List[Education] = Field(..., description="List of education entries")
    skills: List[str] = Field(..., description="List of skills")
    
    # Optional fields
    certifications: List[str] = Field(default=[], description="Professional certifications")
    projects: List[str] = Field(default=[], description="Notable projects")
    languages: List[str] = Field(default=[], description="Languages spoken")
    
    # For tailored answers
    career_goals: Optional[str] = Field(None, description="Career objectives and goals")
    preferred_roles: List[str] = Field(default=[], description="Preferred job roles/titles")

# ============================================================================
# RESUME SCORING CONTRACTS
# ============================================================================

class ResumeScoreInput(BaseModel):
    """Input for resume scoring"""
    user_profile: UserProfile = Field(..., description="Complete user profile")
    job_posting_url: str = Field(..., description="URL of the job posting to score against")

class MatchScoreResult(BaseModel):
    """Output from resume scoring"""
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score between 0 and 1")
    insights: List[str] = Field(..., description="List of insights for improvement")
    skill_matches: List[str] = Field(default=[], description="Skills that match the job")
    skill_gaps: List[str] = Field(default=[], description="Skills missing from resume")
    experience_alignment: str = Field(..., description="How well experience aligns with job requirements")

# ============================================================================
# TAILORED ANSWER CONTRACTS
# ============================================================================

class TailoredAnswerInput(BaseModel):
    """Input for tailored answer generation"""
    user_profile: UserProfile = Field(..., description="Complete user profile")
    job_posting_url: str = Field(..., description="URL of the job posting")
    questions: List[str] = Field(..., description="List of application questions to answer")

class AnswerItem(BaseModel):
    """Individual answer to an application question"""
    question: str = Field(..., description="The original question")
    answer: str = Field(..., description="Tailored answer to the question")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence in the answer quality")

class TailoredAnswers(BaseModel):
    """Output from tailored answer generation"""
    answers: List[AnswerItem] = Field(..., description="List of tailored answers")
    overall_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall quality of all answers")

# ============================================================================
# LEGACY COMPATIBILITY (for existing code)
# ============================================================================

class ResumeScoreInputLegacy(BaseModel):
    """Legacy input format for backward compatibility"""
    resume_text: str = Field(..., description="Raw resume text")
    job_posting_url: str = Field(..., description="URL of the job posting")

class TailoredAnswerInputLegacy(BaseModel):
    """Legacy input format for backward compatibility"""
    profile_text: str = Field(..., description="Raw profile text")
    job_posting_url: str = Field(..., description="URL of the job posting")
    questions: List[str] = Field(..., description="List of application questions")

class TailoredAnswerOutput(BaseModel):
    """Legacy output format for backward compatibility"""
    answers: List[Dict[str, str]] = Field(..., description="List of question-answer pairs") 