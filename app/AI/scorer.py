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

    RUBRIC = """
        Score buckets (use skill_overlap_ratio = intersection / required):
        0.9-1.0  - 90-100 % of required skills AND 80 % experience match
        0.7-0.9  - 70-89 % skills OR experience match
        0.5-0.7  - 50-69 % match
        0.3-0.5  - 30-49 % match
        <0.3     - little relevance
    """
    system_prompt = (
        "You are an ATS-style scorer.\n"
        "First, read the job description and extract a JSON array REQUIRED_SKILLS "
        "(max 20 items, lowercase single words/phrases).\n"
        "Then read the resume and extract PRESENT_SKILLS the same way.\n"
        "Compute skill_overlap_ratio = |intersection| / |REQUIRED_SKILLS| (round 2 dp).\n"
        f"{RUBRIC}\n"
        "Finally, output ONLY the JSON object "
        "{\"match_score\": <float>, \"insights\": [<short strings>]}.\n"
        "Do NOT output REQUIRED_SKILLS or PRESENT_SKILLS."
        "Respond with ONLY the JSON object, inside a ```json code block, and nothing else."
    )

    user_prompt = f"""
Resume:
{resume_text}

Job Description:
{job_description_text}


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

    print("Raw model response:\n", repr(result_str))

    # Attempt to extract JSON from response
    json_match = re.search(r"```json\s*({[\s\S]*?})\s*```", result_str)
    if not json_match:
        json_match = re.search(r"\{[\s\S]*?\}", result_str)

    if json_match:
        try:
            json_text = json_match.group(1) if json_match.lastindex else json_match.group(0)
            result_json = json.loads(json_text)
            print("Scoring complete:", result_json)
            return result_json
        except json.JSONDecodeError:
            print("Failed to parse JSON:", json_text)
            raise
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
