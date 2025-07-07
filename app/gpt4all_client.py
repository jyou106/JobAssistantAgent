from pathlib import Path
from gpt4all import GPT4All

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "mistral-7b-instruct-v0.1.Q4_0.gguf"

_model_instance = None

def get_model():
    global _model_instance
    if _model_instance is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        _model_instance = GPT4All(str(MODEL_PATH), verbose=True)
    return _model_instance

def call_gpt4all(prompt: str, max_tokens: int = 200) -> str:
    model = get_model()
    with model.chat_session():
        return model.generate(prompt, max_tokens=max_tokens)
