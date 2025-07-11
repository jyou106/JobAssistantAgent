import logging
from fastapi import FastAPI, HTTPException
from uuid import uuid4

from app.routes.resume import router as resume_router
from app.routes.autonomous import router as autonomous_router
from pydantic import BaseModel

# Setup logger
logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Core functionality endpoints only

app.include_router(resume_router)
app.include_router(autonomous_router)
