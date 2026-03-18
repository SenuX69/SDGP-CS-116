import os
import sys
from typing import List, Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .database import engine
from . import models
from .routers import users 

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PathFinder+ API", version="1.0.0")
app.include_router(users.router)

@app.get("/health")
def health_check():
    return {"status": "PathFinder+ is alive!"}


# --- Path setup: allow importing ML code that lives outside backend/ ---
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ML_ROOT = os.path.join(REPO_ROOT, "Machine Learning and Data Cleaning")
sys.path.append(ML_ROOT)

try:
    from core.recommendation_engine import RecommendationEngine
except Exception as e:
    raise RuntimeError(
        f"Failed to import RecommendationEngine. Check ML folder path. Error: {e}"
    )

# --- CSV paths ---
JOBS_CSV = os.path.join(ML_ROOT, "processed", "all_jobs_master.csv")
COURSES_CSV = os.path.join(ML_ROOT, "processed", "all_courses_master.csv")

app = FastAPI(
    title="SDGP Career & Course Recommendation API",
    version="0.3.0",
)

app.include_router(auth_router, prefix="/api")

from app.routers.quiz import router as quiz_router

app.include_router(quiz_router, prefix="/api")