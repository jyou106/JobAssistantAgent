from app.deepseek_client import call_deepseek

def generate_tailored_answer(profile: str, job_desc: str):
    prompt = f"""
    Use the information below to generate a tailored answer for the question:
    "Why are you a good fit for this role?"

    User Profile:
    {profile}

    Job Description:
    {job_desc}
    """
    return call_deepseek(prompt)
