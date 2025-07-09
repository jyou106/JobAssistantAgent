import json
import re
from fireworks.client import Fireworks
from .scraper import scrape_job_description
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
if not FIREWORKS_API_KEY:
    raise RuntimeError("FIREWORKS_API_KEY not set in environment variables or .env file.")
fw = Fireworks(api_key=FIREWORKS_API_KEY)

def tailored_answer(profile_text: str, job_posting_url: str, questions: list) -> dict:
    # Scrape job description text
    job_description_text = scrape_job_description.invoke(job_posting_url)
    
    system_prompt = (
        "You are a helpful career coach AI. "
        "Given a user profile, a job description, and a list of application questions, "
        "provide a concise, tailored answer for each question based solely on the profile and job description. "
        "Return ONLY a valid JSON object with this exact structure:\n"
        "{\n"
        '  "answers": [\n'
        "    {\"question\": \"<question text>\", \"answer\": \"<tailored answer>\"},\n"
        "    ...\n"
        "  ],\n"
        '  "overall_quality_score": <float between 0.0 and 1.0>\n'
        "}\n"
        "Do not include any other text, explanations, or formatting."
    )
    
    # Format questions nicely
    questions_text = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
    
    user_prompt = (
        f"User Profile:\n{profile_text}\n\n"
        f"Job Description:\n{job_description_text}\n\n"
        f"Application Questions:\n{questions_text}\n\n"
        "Provide your answers as specified."
    )

    response = fw.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=800
    )
    
    result_str = response.choices[0].message.content
    
    # Try to extract clean JSON from response
    json_match = re.search(r"\{(?:[^{}]|(?R))*\}", result_str, re.DOTALL)
    if not json_match:
        # fallback simple
        json_match = re.search(r"\{[\s\S]*\}", result_str)
    
    if json_match:
        try:
            result_json = json.loads(json_match.group(0))
            return result_json
        except json.JSONDecodeError:
            print("Failed to parse JSON:", json_match.group(0))
            return {
                "error": "Could not parse model output as JSON.",
                "raw_output": result_str
            }
    else:
        print("Failed to find JSON in model output:", result_str)
        return {
            "error": "No JSON object found in model output.",
            "raw_output": result_str
        }

@tool("tailored_answer")
def tailored_answer_tool(profile_text: str, job_posting_url: str, questions: list) -> dict:
    """
    Given a user profile, a job posting URL, and a list of application questions,
    generate tailored answers for each question using the Fireworks API.
    Returns a dictionary with answers and overall quality score.
    """
    return tailored_answer(profile_text, job_posting_url, questions)
