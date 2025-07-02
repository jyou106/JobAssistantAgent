from fastapi import FastAPI
from app.routes import generate

app = FastAPI()

# Add route from /api/generate
app.include_router(generate.router, prefix="/api/generate")

@app.get("/status")
def health_check():
    return {"status": "ok"}
