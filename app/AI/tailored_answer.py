from fireworks.client import Fireworks
from .scraper import scrape_job_description
from langchain.tools import tool
import json
import re

# Set your Fireworks API key
FIREWORKS_API_KEY = "fw_3ZT4iwybrTCAcpcVEwTeGSv7"
fw = Fireworks(api_key=FIREWORKS_API_KEY)

def tailored_answer(profile_text: str, job_posting_url: str, questions: list) -> dict:
    job_description_text = scrape_job_description.invoke(job_posting_url)
    system_prompt = (
        "You are a career coach AI. Given a user profile, a job description, and a list of application questions, "
        "write a compelling answer for each question. "
        "Return JSON: {\"answers\": [{\"question\": str, \"answer\": str}, ...]}"
    )
    user_prompt = f"""Profile:\n{profile_text}\n\nJob Description:\n{job_description_text}\n\nQuestions:\n{questions}\n"""

    response = fw.chat.completions.create(
        model="accounts/fireworks/models/llama-v3p1-8b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=750
    )
    result_str = response.choices[0].message.content
    json_match = re.search(r"\{[\s\S]*?\}", result_str)
    if json_match:
        result_json = json.loads(json_match.group(0))
        return result_json
    else:
        print("Failed to extract JSON from model output:", result_str)
        raise ValueError("No JSON found in model output")

@tool("tailored_answer")
def tailored_answer_tool(profile_text: str, job_posting_url: str, questions: list) -> dict:
    """
    Given a user profile, job posting URL, and a list of application questions, generate tailored answers for each question.
    Returns a dict: {"answers": [{"question": str, "answer": str}, ...]}
    """
    return tailored_answer(profile_text, job_posting_url, questions) 