from fastapi import FastAPI
from app.routes import generate

app = FastAPI()
app.include_router(generate.router)
