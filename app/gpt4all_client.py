from gpt4all import GPT4All

model_path = "./models/ggml-gpt4all-j-v1.3-groovy.bin"  # Adjust path if needed
model = GPT4All(model_name="gpt4all", model_path=model_path)

def call_gpt4all(prompt: str) -> str:
    with model.chat_session():
        return model.generate(prompt, max_tokens=200)
