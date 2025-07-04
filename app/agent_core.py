from app.huggingface_client import call_huggingface

def generate_tailored_answer(profile: str, job: str) -> str:
    prompt = (
    "Write a tailored explanation of why the following user is a good fit for the job described.\n\n"
    f"User Profile:\n{profile}\n\n"
    f"Job Description:\n{job}\n\n"
    "Tailored Explanation:")


    return call_huggingface(prompt)
