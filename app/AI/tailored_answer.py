import json
import re
import logging
from fireworks.client import Fireworks
from .scraper import scrape_job_description
from langchain.tools import tool
from dotenv import load_dotenv
import os
import sys

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
def tailored_answer(profile_text: str, job_posting_url: str, questions: list) -> dict:
    logging.info("[TAILORED] Starting tailored_answer generation")

    try:
        job_description_text = scrape_job_description(str(job_posting_url))
        logging.debug(f"[TAILORED] Job description scraped, length = {len(job_description_text)}")

        questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
        logging.debug(f"[TAILORED] Formatted questions:\n{questions_text}")

        RUBRIC = """
        Score buckets (use skill_overlap_ratio = intersection / required):
        0.9-1.0  - 90-100 % of required skills AND 80 % experience match
        0.7-0.9  - 70-89 % skills OR experience match
        0.5-0.7  - 50-69 % match
        0.3-0.5  - 30-49 % match
        <0.3     - little relevance
        """

        system_prompt = (
            "You are a career coach AI. Given a user's profile, a job description, and a list of application questions, "
            "write a concise and compelling answer for each question tailored specifically to the user's background and the job requirements.\n"
            "You MUST also score the resume using this rubric based on skill and experience overlap:\n"
            f"{RUBRIC}\n"
            "Extract REQUIRED_SKILLS and PRESENT_SKILLS from job and profile respectively (max 20 items each).\n"
            "Then compute skill_overlap_ratio = |intersection| / |REQUIRED_SKILLS|.\n"
            "Return ONLY this JSON format, nothing else:\n"
            "{\n"
            '  "answers": [\n'
            '    {"question": "question 1 text", "answer": "tailored answer 1"},\n'
            '    {"question": "question 2 text", "answer": "tailored answer 2"},\n'
            '    ...\n'
            '  ],\n'
            '  "overall_quality_score": <float between 0 and 1>\n'
            "}\n"
        )

        user_prompt = (
            f"User Profile:\n{profile_text}\n\n"
            f"Job Description:\n{job_description_text}\n\n"
            f"Application Questions:\n{questions_text}\n\n"
        )

        logging.info("[TAILORED] Sending prompt to Fireworks...")
        response = fw.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p1-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            max_tokens=1000
        )

        result_str = response.choices[0].message.content.strip()
        logging.debug(f"[TAILORED] Raw model output:\n{result_str[:500]}")

        # Try to extract JSON
        json_match = re.search(r"\{[\s\S]*\}", result_str)        
        if not json_match:
            json_match = re.search(r"\{[\s\S]*\}", result_str)

        if json_match:
            json_str = json_match.group(0)
            try:
                result_json = json.loads(json_str)
                logging.info("[TAILORED] Successfully parsed model output into JSON")
                return {
                    "success": True,
                    "data": result_json
                }
            except json.JSONDecodeError as e:
                logging.error("[TAILORED] JSON parsing failed")
                logging.debug(f"[TAILORED] Malformed JSON string:\n{json_str}")
                return {
                    "success": False,
                    "error": "Could not parse model output as JSON",
                    "raw_output": result_str
                }
        else:
            logging.error("[TAILORED] No JSON found in output")
            return {
                "success": False,
                "error": "No JSON object found in model output",
                "raw_output": result_str
            }

    except Exception as e:
        logging.exception("[TAILORED] Unexpected error occurred")
        return {
            "success": False,
            "error": str(e)
        }

# ----------------- Langchain Tool ----------------- #
@tool("tailored_answer")
def tailored_answer_tool(profile_text: str, job_posting_url: str, questions: list) -> dict:
    """
    Given a user profile, a job posting URL, and a list of application questions,
    generate tailored answers for each question using the Fireworks API.
    Returns a dictionary with answers and overall quality score.
    """
    return tailored_answer(profile_text, job_posting_url, questions)
