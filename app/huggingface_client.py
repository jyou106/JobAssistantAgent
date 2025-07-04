from transformers import pipeline

generator = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1")

def call_huggingface(user_profile: str, job_description: str) -> str:
    prompt = (
        "[INST] Based on the user profile and job description below, generate a short paragraph "
        "explaining why the user is a good fit.\n\n"
        f"User profile: {user_profile}\n"
        f"Job description: {job_description} [/INST]"
    )

    outputs = generator(
        prompt,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.2,
        pad_token_id=50256
    )
    return outputs[0]["generated_text"]
