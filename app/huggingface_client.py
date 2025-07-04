from transformers import pipeline

generator = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.1")

def call_huggingface(prompt: str) -> str:
    outputs = generator(prompt, max_new_tokens=200)
    return outputs[0]["generated_text"]
