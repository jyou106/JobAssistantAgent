import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = "accounts/fireworks/models/gpt-oss-20b"
API_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {FIREWORKS_API_KEY}",
    "Content-Type": "application/json",
}

def call_fireworks(prompt: str, max_tokens: int = 500) -> str:
    data = {
        "model": FIREWORKS_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Respond using ONLY plain paragraphs of complete sentences. NEVER use markdown, tables, bullet points, asterisks, dashes, numbers, or any formatting characters. Just write normal sentences separated by spaces and periods."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9,
    }

    response = requests.post(API_URL, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()