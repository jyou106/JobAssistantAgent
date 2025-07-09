import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.tools import StructuredTool          
from .scraper import scrape_job_description
from .scorer import score_resume_tool
from .tailored_answer import tailored_answer_tool
from .schemas import UserProfile, ResumeScoreInput, TailoredAnswerInput, ResumeScoreInputLegacy
import json

# Initialize the LLM for the agent (using OpenAI-compatible API)
# You can use Fireworks AI or any other OpenAI-compatible provider
from fireworks.client import Fireworks
from langchain_fireworks.chat_models import ChatFireworks

load_dotenv()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise RuntimeError("FIREWORKS_API_KEY not set in environment variables or .env file.")
fw = Fireworks(api_key=FIREWORKS_API_KEY)

# Define all available tools
score_resume_structured = StructuredTool.from_function(
    name="score_resume",
    func=score_resume_tool,            # ← your real business logic
    args_schema=ResumeScoreInputLegacy,
    description=(
        "Score a resume against a job description. "
        "Input object must contain: resume_text (string) and "
        "job_posting_url (string). Returns match_score and insights."
    ),
)
tools = [
    Tool(
        name="scrape_job_description",
        func=scrape_job_description,
        description="Scrape and extract the job description from a job posting URL. Use this when you need to get the job description text from a URL."
    ),
    score_resume_structured,
    Tool(
        name="tailored_answer",
        func=tailored_answer_tool,
        description="Generate tailored answers for application questions. Input: profile_text (string), job_posting_url (string), questions (list of strings). Returns a dict with answers."
    )
]

# Initialize the agent
llm = ChatFireworks(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    temperature=0.0,
    # fireworks_api_key is picked up automatically from FIREWORKS_API_KEY
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# Convenience functions for common workflows
def score_resume_workflow(resume_text: str, job_posting_url: str):
    """
    Complete resume scoring workflow using the agent.
    """
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
    """
    Complete tailored answer workflow using the agent.
    """
    questions_str = "\n".join([f"- {q}" for q in questions])
    prompt = f"""
    I need to generate tailored answers for application questions.
    
    Profile: {profile_text}
    Job URL: {job_posting_url}
    Questions:
    {questions_str}
    
    Please:
    1. Scrape the job description from the URL
    2. Generate tailored answers for each question
    3. Return the answers in a structured format
    """
    
    result = agent.run(prompt)
    return result

def comprehensive_workflow(resume_text: str, job_posting_url: str, questions: list = None):
    """
    Complete workflow: score resume AND generate tailored answers if questions provided.
    """
    if questions:
        prompt = f"""
        I need to perform a comprehensive job application analysis.
        
        Resume: {resume_text}
        Job URL: {job_posting_url}
        Questions: {questions}
        
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

# Example usage functions
def example_resume_scoring():
    """Example of resume scoring workflow"""
    resume_text = """AI Intern, Stylework
    May 2025– July 2025
    • Developed and deployed a multimodal AI-powered conversational chatbot using LangChain and LLM agents
    to automate workspace booking, answer company-specific queries via PDF parsing, and handle general user
    interactions."""
    
    job_url = "https://workday.wd5.myworkdayjobs.com/en-US/Workday/job/Principal-Product-Manager---Workday-AI_JR-0097995?source=Careers_Website_mlai"
    
    result = score_resume_workflow(resume_text, job_url)
    print("Resume Scoring Result:", result)

def example_tailored_answers():
    """Example of tailored answer workflow"""
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