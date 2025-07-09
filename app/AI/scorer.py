import os
from dotenv import load_dotenv
from fireworks.client import Fireworks
from .scraper import scrape_job_description
import json
import re
from langchain.tools import tool

# Load environment variables
load_dotenv()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise RuntimeError("FIREWORKS_API_KEY not set in environment variables or .env file.")
fw = Fireworks(api_key=FIREWORKS_API_KEY)

def score_resume(resume_text, job_posting_url):
    job_description_text = scrape_job_description.invoke(job_posting_url)
    system_prompt = (
        "You are an AI assistant. Compare the following resume with the job description. "
        "Return JSON: {\"match_score\": float, \"insights\": [string, ...]}"
    )
    user_prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{job_description_text}"

    response = fw.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=512
    )
    result_str = response.choices[0].message.content

    # Extract JSON from Markdown code block or anywhere in the string
    json_match = re.search(r"\{[\s\S]*?\}", result_str)
    if json_match:
        result_json = json.loads(json_match.group(0))
        return result_json
    else:
        print("Failed to extract JSON from model output:", result_str)
        raise ValueError("No JSON found in model output")

@tool("score_resume")
def score_resume_tool(resume_text: str, job_posting_url: str) -> dict:
    """
    Scrape the job description from the given URL and score the resume against it.
    Returns a dict with match_score and insights.
    """
    return score_resume(resume_text, job_posting_url)