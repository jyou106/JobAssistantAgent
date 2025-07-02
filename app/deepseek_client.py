import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("DEEPSEEK_API_URL")
API_KEY = os.getenv("DEEPSEEK_API_KEY")

def call_deepseek(prompt: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": prompt
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()
