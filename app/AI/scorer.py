import json
import re
import logging
from fireworks.client import Fireworks
from .scraper import scrape_job_description
from langchain.tools import tool
from dotenv import load_dotenv
import os
import sys
from typing import Optional

# ----------------- Logging Setup ----------------- #
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# ----------------- Load API Key ------------------ #
load_dotenv()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise RuntimeError("FIREWORKS_API_KEY not set in environment variables or .env file.")
fw = Fireworks(api_key=FIREWORKS_API_KEY)

# ----------------- Main Function ------------------ #
def score_resume(resume_text: str, job_text_or_url: str, is_url: bool = False) -> dict:
    """
    Score a resume against a job description.
    
    Args:
        resume_text: The resume text
        job_text_or_url: Either job description text OR job posting URL
        is_url: Set to True if job_text_or_url is a URL that needs scraping
    """
    print("Received scoring request")

    # Get job description either from direct input or scraping
    if is_url:
        job_description_text = scrape_job_description(str(job_text_or_url))
        if not job_description_text or len(job_description_text.strip()) < 20:
            raise ValueError("Scraped job description is empty or too short.")
    else:
        job_description_text = job_text_or_url
    
    print("Job description (first 300 chars):", job_description_text[:300])

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
        "Do not include any reasoning, analysis, or thinking in your response. Only output the JSON."
    )

    user_prompt = f"""
Resume:
{resume_text}

Job Description:
{job_description_text}

"""

    try:
        print("Calling Fireworks API...")
        response = fw.chat.completions.create(
            model="accounts/fireworks/models/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=1000  # Increased significantly
        )
        
        # Handle reasoning models (content may be None, reasoning_content has the thinking)
        result_str = None
        
        # Try to get content from message
        if hasattr(response.choices[0].message, 'content'):
            result_str = response.choices[0].message.content
        
        # If content is None, the model might be a reasoning model that puts response elsewhere
        if result_str is None:
            print("Content is None, checking reasoning_content...")
            if hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning = response.choices[0].message.reasoning_content
                print(f"Reasoning content found (first 500 chars): {reasoning[:500]}")
                # Try to extract JSON from reasoning_content
                result_str = reasoning
        
        # If still None, try raw_output
        if result_str is None:
            if hasattr(response.choices[0], 'raw_output'):
                result_str = response.choices[0].raw_output
        
        if result_str is None:
            print(f"Full response: {response}")
            raise ValueError("Model returned None - no content found in response")
        
        print("Raw model response:\n", repr(result_str[:1000]))

    except Exception as e:
        print(f"Error calling Fireworks API: {e}")
        raise ValueError(f"API call failed: {str(e)}")

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
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", json_text)
            raise ValueError(f"JSON parsing failed: {str(e)}")
    else:
        print("Failed to extract JSON from model output:", result_str[:500])
        raise ValueError("No JSON found in model output")

@tool("score_resume")
def score_resume_tool(resume_text: str, job_text_or_url: str, is_url: bool = True) -> dict:
    """
    Score a resume against a job description.
    If is_url is True, job_text_or_url is treated as a URL to scrape.
    Otherwise, it's treated as direct job description text.
    """
    return score_resume(resume_text, job_text_or_url, is_url)