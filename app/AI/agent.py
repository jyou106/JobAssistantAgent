from typing import Annotated
import builtins
builtins.Annotated = Annotated

import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import Tool, StructuredTool          
from .scraper import scrape_job_description
from .scorer import score_resume_tool
from .tailored_answer import tailored_answer, tailored_answer_tool
from .schemas import (
    UserProfile, ResumeScoreInput, TailoredAnswerInput,
    ResumeScoreInputLegacy, ResumeScoreOutput
)
from fireworks.client import Fireworks
from langchain_fireworks.chat_models import ChatFireworks
from app.AI.scraper import ScrapeJobInput  
import json

load_dotenv()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise RuntimeError("FIREWORKS_API_KEY not set in environment variables or .env file.")
fw = Fireworks(api_key=FIREWORKS_API_KEY)

# Structured tool for resume scoring
score_resume_structured = StructuredTool.from_function(
    name="score_resume",
    func=score_resume_tool,
    args_schema=ResumeScoreInputLegacy,
    description=(
        "Score a resume against a job description. "
        "Input object must contain: resume_text (string) and "
        "job_posting_url (string). Returns match_score and insights."
    ),
    return_direct=False
)


# Standard tools (non-structured)
scrape_job_description_tool = StructuredTool.from_function(
    name="scrape_job_description",
    func=scrape_job_description,
    args_schema=ScrapeJobInput,  
    description="Scrape and extract the job description from a job posting URL.",
    return_direct=True 
)

tailored_answer_tool_structured = StructuredTool.from_function(
    name="tailored_answer",
    func=tailored_answer,
    args_schema=TailoredAnswerInput,
    description="Given a job title and resume text, return a tailored answer to help the user prepare.",
    return_direct=True
)


tools = [
    scrape_job_description_tool,
    score_resume_structured,
    tailored_answer_tool_structured
]


# Initialize the LLM
llm = ChatFireworks(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    temperature=0.0,
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)


# --- Workflows ---
def score_resume_workflow(resume_text: str, job_posting_url: str):
    prompt = f"""
    I need to score a resume against a job posting.

    Resume: {resume_text}
    Job URL: {job_posting_url}

    Please:
    1. Scrape the job description from the URL
    2. Score the resume against the job description
    3. Return the match score and insights
    """
    result = agent.run(prompt)
    return result

def tailored_answer_workflow(profile_text: str, job_posting_url: str, questions: list):
    result = tailored_answer(profile_text, job_posting_url, questions)

    if isinstance(result, dict):
        if result.get("success"):
            return {"success": True, "data": result["data"]}
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error occurred"),
                "raw_output": result.get("raw_output")
            }
    else:
        return {
            "success": False,
            "error": f"Unexpected return type: {type(result)}",
            "raw_output": result
        }


def comprehensive_workflow(resume_text: str, job_posting_url: str, questions: list = None):
    if questions:
        questions_str = "\n".join([f"- {q}" for q in questions])
        prompt = f"""
        I need to perform a comprehensive job application analysis.

        Resume: {resume_text}
        Job URL: {job_posting_url}
        Questions:
        {questions_str}

        Please:
        1. Scrape the job description from the URL
        2. Score the resume against the job description
        3. Generate tailored answers for the questions
        4. Return both the score and the answers
        """
    else:
        prompt = f"""
        I need to score a resume against a job posting.

        Resume: {resume_text}
        Job URL: {job_posting_url}

        Please:
        1. Scrape the job description from the URL
        2. Score the resume against the job description
        3. Return the match score and insights
        """
    result = agent.run(prompt)
    return result

# --- Example Usage ---
def example_resume_scoring():
    resume_text = """AI Intern, Stylework
    May 2025– July 2025
    • Developed and deployed a multimodal AI-powered conversational chatbot using LangChain and LLM agents
    to automate workspace booking, answer company-specific queries via PDF parsing, and handle general user
    interactions."""
    
    job_url = "https://workday.wd5.myworkdayjobs.com/en-US/Workday/job/Principal-Product-Manager---Workday-AI_JR-0097995?source=Careers_Website_mlai"
    result = score_resume_workflow(resume_text, job_url)
    print("Resume Scoring Result:", result)

def example_tailored_answers():
    profile_text = """Experienced AI engineer with background in machine learning and product development."""
    job_url = "https://workday.wd5.myworkdayjobs.com/en-US/Workday/job/Principal-Product-Manager---Workday-AI_JR-0097995?source=Careers_Website_mlai"
    questions = ["Why are you a good fit?", "What is your biggest strength?"]
    
    result = tailored_answer_workflow(profile_text, job_url, questions)
    print("Tailored Answers Result:", result)

if __name__ == "__main__":
    print("Testing Resume Scoring Workflow:")
    example_resume_scoring()
    
    print("\nTesting Tailored Answers Workflow:")
    example_tailored_answers()