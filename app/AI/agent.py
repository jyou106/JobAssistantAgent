from typing import Annotated
import builtins
builtins.Annotated = Annotated

import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType, AgentExecutor
# Removed unused ChatOpenAI import to avoid version conflicts
from langchain.tools import Tool, StructuredTool          
from .scraper import scrape_job_description
from .scorer import score_resume_tool, score_resume
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

# Simple tool definitions to avoid Pydantic schema issues
from langchain.tools import Tool

score_resume_tool_simple = Tool(
    name="score_resume",
    func=lambda input_str: score_resume_tool(input_str),
    description=(
        "Score a resume against a job description. "
        "Input should be a string with resume text and job URL separated by '||'"
    )
)

scrape_job_description_tool_simple = Tool(
    name="scrape_job_description",
    func=scrape_job_description,
    description="Scrape and extract the job description from a job posting URL. Input: URL string"
)

tailored_answer_tool_simple = Tool(
    name="tailored_answer", 
    func=lambda input_str: tailored_answer_tool(input_str),
    description="Generate tailored answers for job application questions. Input: profile||job_url||questions"
)


tools = [
    scrape_job_description_tool_simple,
    score_resume_tool_simple,
    tailored_answer_tool_simple
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
    # Step 1: Call tailored answer
    answer_result = tailored_answer(profile_text, job_posting_url, questions)

    # Step 2: Also call resume scoring to reuse the match_score
    try:
        match_result = score_resume(profile_text, job_posting_url)
        match_score = match_result.get("match_score", None)
    except Exception as e:
        match_score = None  # fallback if scoring fails

    if isinstance(answer_result, dict) and answer_result.get("success"):
        return {
            "success": True,
            "data": {
                "match_score": match_score,
                "answers": answer_result["data"].get("answers")
            }
        }
    else:
        return {
            "success": False,
            "error": answer_result.get("error", "Unknown error"),
            "raw_output": answer_result.get("raw_output")
        }


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