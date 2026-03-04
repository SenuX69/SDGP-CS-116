import os
import sys
from typing import List, Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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

@app.get("/health")
def health_check():
    return {"status": "ok"}

class RecommendRequest(BaseModel):
    target_role: str = Field(..., examples=["Software Engineer"])
    skills: List[str] = Field(default_factory=list, examples=[["python", "sql", "java"]])
    top_n: int = Field(default=5, ge=1, le=20)

class AnalyzeRequest(BaseModel):
    target_job: str
    answers: Dict[str, Any] # Full 18-point assessment answers

# --- Load engine once (startup) ---
try:
    engine = RecommendationEngine(
        jobs_path=JOBS_CSV,
        courses_path=COURSES_CSV,
        show_progress=False
    )
    startup_error = None
except Exception as e:
    engine = None
    startup_error = str(e)

@app.get("/status")
def status():
    if engine is None:
        return {"engine_loaded": False, "error": startup_error}
    return {"engine_loaded": True}

@app.post("/api/recommend")
def recommend(req: RecommendRequest) -> Dict[str, Any]:
    """
    Generate job and course recommendations using ML engine
    """
    if engine is None:
        raise HTTPException(status_code=500, detail=f"Engine not loaded: {startup_error}")

    jobs = engine.recommend_jobs(
        user_skills=req.skills,
        target_role=req.target_role,
        top_n=req.top_n
    )

    courses = engine.recommend_courses(
        target_job=req.target_role,
        user_skills=req.skills,
        top_n=req.top_n
    )

    return {
        "target_role": req.target_role,
        "jobs": jobs,
        "courses": courses,
    }

@app.post("/api/analyze")
def analyze_assessment(req: AnalyzeRequest) -> Dict[str, Any]:
    """
    Comprehensive analysis based on 18-point assessment
    """
    if engine is None:
        raise HTTPException(status_code=500, detail=f"Engine not loaded: {startup_error}")

    try:
        # 1. Process 18-point assessment into feature vector
        vector = engine.process_comprehensive_assessment(req.answers)
        
        # 2. Generate full dashboard bundle
        bundle = engine.get_recommendations_from_assessment(vector, req.target_job)
        
        return bundle
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
