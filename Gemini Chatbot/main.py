
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path

app = FastAPI(title="PathFinder+ Mentor API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths - Adjusted to find mentors.json from the project root
# BASE_DIR is project_root/
BASE_DIR = Path(__file__).resolve().parent.parent
MENTOR_DATA_PATH = BASE_DIR / "Machine Learning and Data Cleaning" / "data" / "processed" / "mentors.json"

# Data Cache
mentors_db = []
chat_history = {} # mentor_id -> list of messages

# Visual Mapping (Generated Assets)
VISUAL_MAPPING = {
    "mentor_001": "/team/mentor_1.png", # Dilshan Fernando
    "mentor_002": "/team/mentor_2.png", # Aisha Gunawardena
    "mentor_003": "/team/mentor_3.png", # Nadeesha Ranasinghe
}

@app.on_event("startup")
async def load_data():
    global mentors_db
    try:
        if MENTOR_DATA_PATH.exists():
            with open(MENTOR_DATA_PATH, "r", encoding="utf-8") as f:
                mentors_db = json.load(f)
            print(f"Successfully loaded {len(mentors_db)} mentors from {MENTOR_DATA_PATH}")
        else:
            print(f"Warning: mentors.json not found at {MENTOR_DATA_PATH}")
    except Exception as e:
        print(f"Error loading mentors: {e}")

class RecommendationRequest(BaseModel):
    skills: List[str]
    target_role: str
    domain: Optional[str] = "General"

class ChatMessage(BaseModel):
    user_id: str
    mentor_id: str
    message: str

@app.get("/")
async def root():
    return {"message": "mentor API is running", "mentors_loaded": len(mentors_db)}

@app.post("/api/v1/mentors/recommend")
async def recommend_mentors(request: RecommendationRequest):
    """
    Semantic & Role-based Mentor Matcher Endpoint.
    """
    if not mentors_db:
        raise HTTPException(status_code=503, detail="Mentor database not initialized. Check if mentors.json exists.")

    scored_mentors = []
    user_skills = set(s.lower() for s in request.skills)
    user_domain = request.domain
    target_role_lower = request.target_role.lower()

    for mentor in mentors_db:
        # Domain Isolation
        mentor_domain = mentor.get("sector", "General")
        
        if user_domain != "General" and mentor_domain != "General" and mentor_domain.lower() != user_domain.lower():
            continue

        mentor_skills = [s.lower() for s in mentor.get("expertise", [])]
        overlap = list(user_skills & set(mentor_skills))
        
        score = len(overlap) * 2
        mentor_role = mentor.get("title", "").lower()
        
        if target_role_lower in mentor_role or mentor_role in target_role_lower:
            score += 10
            
        if mentor.get("company"):
            score += 5

        mentor_id = mentor.get("id")
        scored_mentors.append({
            "id": mentor_id,
            "name": mentor.get("name"),
            "title": mentor.get("title"),
            "company": mentor.get("company"),
            "expertise": mentor.get("expertise"),
            "bio": mentor.get("bio"),
            "matching_score": score,
            "matched_skills": [s.title() for s in overlap[:3]] if overlap else ["Role Match"],
            "avatar": VISUAL_MAPPING.get(mentor_id, f"https://api.dicebear.com/7.x/avataaars/svg?seed={mentor.get('name')}")
        })

    scored_mentors.sort(key=lambda x: x["matching_score"], reverse=True)
    return scored_mentors[:6]

@app.post("/api/v1/chat/send")
async def send_message(msg: ChatMessage):
    """
    Mocked Chat Endpoint with smart simulated responses for MVP demo.
    """
    if msg.mentor_id not in chat_history:
        chat_history[msg.mentor_id] = []
    
    # User message
    chat_history[msg.mentor_id].append({"sender": "user", "text": msg.message})
    
    # Logic for "Smart" Demo Replies
    text_lower = msg.message.lower()
    mentor = next((m for m in mentors_db if m["id"] == msg.mentor_id), {"name": "Mentor"})
    mentor_first_name = mentor.get('name', 'Mentor').split(' ')[0]

    if "resume" in text_lower or "cv" in text_lower:
        reply = f"Great that you're working on your CV! I can definitely review it. Could you please send me a PDF link or a Google Drive link?"
    elif "skill" in text_lower or "learn" in text_lower:
        reply = f"Learning the right stack is crucial. Based on your profile, I'd suggest focusing on {', '.join(mentor.get('expertise', [])[:2])} first. Have you tried any projects in these yet?"
    elif "internship" in text_lower or "job" in text_lower:
        reply = f"Finding an internship at {mentor.get('company', 'top firms')} is all about networking. I can share some tips on how we hire here. Would you like to schedule a quick call?"
    elif "hi" in text_lower or "hello" in text_lower:
        reply = f"Hello! I'm {mentor_first_name}. I saw your profile and I'm impressed by your interest in {mentor.get('sector', 'tech')}. How can I help you today?"
    else:
        reply = f"Thanks for reaching out! I've received your message about '{msg.message[:20]}...' and I'll get back to you with a detailed response shortly. Looking forward to mentoring you!"

    # Simulate mentor reply
    chat_history[msg.mentor_id].append({"sender": "mentor", "text": reply})
    
    return {"status": "sent", "reply": reply}

@app.get("/api/v1/chat/history/{mentor_id}")
async def get_chat_history(mentor_id: str):
    return chat_history.get(mentor_id, [])

if __name__ == "__main__":
    import uvicorn
    # Changed port to 8001 to avoid common 8000 conflicts
    uvicorn.run(app, host="127.0.0.1", port=8001)
