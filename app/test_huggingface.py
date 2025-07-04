import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load .env variables
load_dotenv()

token = os.getenv("HUGGINGFACE_TOKEN")

# Use a public model to test authentication
client = InferenceClient(
    model="gpt2",
    token=token
)

try:
    output = client.text_generation("Test prompt", max_new_tokens=10)
    print("✅ Hugging Face API token is working!")
    print("Output:", output)
except Exception as e:
    print("❌ Token failed or access issue.")
    print(e)
