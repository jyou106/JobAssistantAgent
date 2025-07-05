from gpt4all import GPT4All

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")

def call_gpt4all(prompt: str, max_tokens: int = 200) -> str:
    with model.chat_session():
        return model.generate(prompt, max_tokens=max_tokens)
