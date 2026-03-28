import os
import sys
from typing import List, Any, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class RecommendRequest(BaseModel):
    target_role: str
    skills: List[str] = []
    interests: List[str] = []
    top_n: int = 5

# --- Path setup ---
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ML_ROOT = os.path.join(REPO_ROOT, "Machine Learning and Data Cleaning")
sys.path.append(ML_ROOT)

try:
    from core.recommendation_engine import RecommendationEngine
except Exception as e:
    raise RuntimeError(
        f"Failed to import RecommendationEngine. Error: {e}"
    )

# --- CSV paths ---
JOBS_CSV = os.path.join(ML_ROOT, "processed", "all_jobs_master.csv")
COURSES_CSV = os.path.join(ML_ROOT, "processed", "all_courses_master.csv")

from fastapi.middleware.cors import CORSMiddleware
from app.routers.users import router as auth_router

app = FastAPI(
    title="SDGP Career & Course Recommendation API",
    version="0.3.0",
)

# ✅ SINGLE CORS CONFIG
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:3001",
        "http://localhost:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load engine ---
try:
    print("Initializing PyTorch engine from MongoDB...")
    engine = RecommendationEngine.from_mongo()
    startup_error = None
except Exception as e:
    engine = None
    startup_error = str(e)
    print(f"CRITICAL ENGINE FAILURE: {startup_error}")

@app.get("/status")
def status():
    if engine is None:
        return {"engine_loaded": False, "error": startup_error}
    return {"engine_loaded": True}

@app.get("/api/market-trends")
def get_market_trends(domain: str = None):
    fallbacks = {
        "Information Technology": [{"title": "Software Engineer", "jobs_active": 150}, {"title": "Data Scientist", "jobs_active": 110}, {"title": "Cloud Architect", "jobs_active": 85}, {"title": "Cybersecurity Analyst", "jobs_active": 60}],
        "Business & Finance": [{"title": "Financial Analyst", "jobs_active": 120}, {"title": "Business Analyst", "jobs_active": 90}, {"title": "Product Analyst", "jobs_active": 75}, {"title": "Account Manager", "jobs_active": 65}],
        "Marketing": [{"title": "SEO Specialist", "jobs_active": 110}, {"title": "Digital Marketing Manager", "jobs_active": 85}, {"title": "Content Strategist", "jobs_active": 70}, {"title": "Growth Hacker", "jobs_active": 50}],
        "Engineering": [{"title": "Civil Engineer", "jobs_active": 80}, {"title": "Mechanical Engineer", "jobs_active": 65}, {"title": "Electrical Engineer", "jobs_active": 55}, {"title": "Quality Engineer", "jobs_active": 45}],
        "Design & Arts": [{"title": "UX Designer", "jobs_active": 95}, {"title": "Product Designer", "jobs_active": 70}, {"title": "Graphic Designer", "jobs_active": 60}, {"title": "Motion Designer", "jobs_active": 40}],
        "Healthcare": [{"title": "Healthcare Admin", "jobs_active": 105}, {"title": "Clinical Analyst", "jobs_active": 90}, {"title": "Medical Researcher", "jobs_active": 75}, {"title": "Nursing Manager", "jobs_active": 65}],
        "Science": [{"title": "Research Scientist", "jobs_active": 60}, {"title": "Data Miner", "jobs_active": 55}, {"title": "Biotech Analyst", "jobs_active": 45}, {"title": "Lab Technician", "jobs_active": 35}],
    }

    default_trends = [
        {"title": "Software Engineering", "jobs_active": 150},
        {"title": "Data Analytics", "jobs_active": 85},
        {"title": "UI/UX Design", "jobs_active": 75},
        {"title": "Product Management", "jobs_active": 60}
    ]

    if engine is None or not hasattr(engine, 'jobs_df') or engine.jobs_df is None:
        return {"trends": fallbacks.get(domain, default_trends)}

    try:
        df = engine.jobs_df

        if domain and 'domain' in df.columns:
            df_slice = df[df['domain'] == domain]
            if df_slice.empty:
                return {"trends": fallbacks.get(domain, default_trends)}

            col_name = 'title' if 'title' in df_slice.columns else 'Job Title'
            if col_name in df_slice.columns:
                counts = df_slice[col_name].value_counts().head(4)

                if len(counts) == 0:
                    return {"trends": fallbacks.get(domain, default_trends)}

                trends = [
                    {"title": str(title)[:28], "jobs_active": int(count)}
                    for title, count in counts.items()
                ]
                return {"trends": trends}

        if 'domain' in df.columns:
            counts = df['domain'].value_counts().head(4)
            trends = [{"title": str(dom), "jobs_active": int(count)} for dom, count in counts.items()]
            return {"trends": trends}

        return {"trends": fallbacks.get(domain, default_trends)}

    except Exception as e:
        print(f"Market Trends Error: {e}")
        return {"trends": fallbacks.get(domain, default_trends)}

@app.post("/api/recommend")
def recommend(req: RecommendRequest) -> Dict[str, Any]:
    if engine is None:
        raise HTTPException(status_code=500, detail=f"Engine not loaded: {startup_error}")

    jobs = engine.recommend_jobs(
        target_role=req.target_role,
        skills=req.skills,
        interests=req.interests,
        top_n=req.top_n,
    )

    courses = engine.recommend_courses(
        target_role=req.target_role,
        skills=req.skills,
        interests=req.interests,
        top_n=req.top_n,
    )

    return {
        "target_role": req.target_role,
        "jobs": jobs,
        "courses": courses,
    }

# --- Routers ---
app.include_router(auth_router)

from app.routers.skill_assessment import router as quiz_router
app.include_router(quiz_router, prefix="/api")

from app.routers.resume_api import router as resume_router
app.include_router(resume_router, prefix="/api")

from app.routers.profile import router as profile_router
app.include_router(profile_router)

from app.routers.resume_scan_tool import router as resume_scan_router
app.include_router(resume_scan_router)

from app.routers.career_paths import router as career_paths_router
app.include_router(career_paths_router, prefix="/api")

from app.routers.chatbot import router as chatbot_router
app.include_router(chatbot_router, prefix="/api/chat")

try:
    from app.routers.mentor import router as mentor_router
    app.include_router(mentor_router)
except Exception as e:
    print(f"Failed to load Mentor WebSockets: {e}")
