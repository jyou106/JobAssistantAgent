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
    print("Received scoring request")

    # Scrape the job description from the URL
    job_description_text = scrape_job_description(str(job_posting_url))
    if not job_description_text or len(job_description_text.strip()) < 20:
        raise ValueError("Scraped job description is empty or too short.")
    print("Scraped job description (first 300 chars):", job_description_text[:300])

    system_prompt = (
        "You are an AI assistant that MUST respond ONLY with a single JSON object "
        "with exactly two keys: "
        "\"match_score\" (a float from 0.0 to 1.0), and "
        "\"insights\" (an array of short strings). "
        "Do NOT include any other text or explanation."
    )

    user_prompt = f"""
Resume:
{resume_text}

Job Description:
{job_description_text}

Return ONLY a JSON object like this example:

{{
  "match_score": 0.75,
  "insights": [
    "Experience with Python",
    "Familiarity with FastAPI"
  ]
}}
"""

    response = fw.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=256
    )
    result_str = response.choices[0].message.content

    print("🔥 Raw model response:\n", repr(result_str))

    # Attempt to extract JSON from response
    json_match = re.search(r"```json\s*({[\s\S]*?})\s*```", result_str)
    if not json_match:
        json_match = re.search(r"\{[\s\S]*?\}", result_str)

    if json_match:
        try:
            json_text = json_match.group(1) if json_match.lastindex else json_match.group(0)
            result_json = json.loads(json_text)
            print("✅ Scoring complete:", result_json)
            return result_json
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON:", json_text)
            raise
    else:
        print("❌ Failed to extract JSON from model output:", result_str)
        raise ValueError("No JSON found in model output")


@tool("score_resume")
def score_resume_tool(resume_text: str, job_posting_url: str) -> dict:
    """
    Scrape the job description from the given URL and score the resume against it.
    Returns a dict with match_score and insights.
    """
    return score_resume(resume_text, job_posting_url)
