import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_MODEL = "accounts/fireworks/models/llama-v3p1-8b-instruct"
API_URL = f"https://api.fireworks.ai/inference/v1/completions"

HEADERS = {
    "Authorization": f"Bearer {FIREWORKS_API_KEY}",
    "Content-Type": "application/json",
}

def call_fireworks(prompt: str, max_tokens: int = 200) -> str:
    data = {
        "model": FIREWORKS_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    response = requests.post(API_URL, headers=HEADERS, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["text"].strip()
