from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime
import os, uuid

from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------
# App + Storage
# ---------------------------
app = FastAPI(title="Mentor Mentorship Backend (FastAPI)")

UPLOAD_DIR = "./storage/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# ---------------------------
# DB (SQLite)
# ---------------------------
DATABASE_URL = "sqlite:///./mentor_chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Models
# ---------------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    role = Column(String(20), default="student")  # student/mentor/admin

class MentorProfile(Base):
    __tablename__ = "mentor_profiles"
    id = Column(Integer, primary_key=True)
    # If you later want real mentor accounts: store user_id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    display_name = Column(String(120), nullable=False)
    is_real = Column(Boolean, default=False)
    bio = Column(Text, default="")
    active = Column(Boolean, default=True)

class MentorSkill(Base):
    __tablename__ = "mentor_skills"
    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("mentor_profiles.id"), nullable=False)
    skill_name = Column(String(80), nullable=False)
    level = Column(Integer, nullable=False)   
class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssessmentResult(Base):
    __tablename__ = "assessment_results"
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    skill_name = Column(String(80), nullable=False)
    score = Column(Integer, nullable=False) 
        

class MentorshipRequest(Base):
   
    __tablename__ = "mentorship_requests"
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentor_profiles.id"), nullable=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------------------
# Schemas
# ---------------------------
class UserCreate(BaseModel):
    name: str
    role: str = "student"

class MentorCreate(BaseModel):
    display_name: str
    is_real: bool = False
    bio: str = ""
    active: bool = True
    user_id: Optional[int] = None

class MentorSkillIn(BaseModel):
    skill_name: str
    level: int = Field(ge=1, le=10)
 
 
 
class AssessmentCreateOut(BaseModel):
    assessment_id: int

class AssessmentResultsIn(BaseModel):
    results: Dict[str, int]  # {"Java":40,"SQL":80}

class ApplyIn(BaseModel):
    mentor_id: int

class ApproveIn(BaseModel):
    status: str  # "approved" or "rejected"

class MessageIn(BaseModel):
    type: str = "text"   # text/image/file
    content: str


def get_me(x_user_id: Optional[str] = None, db: Session = Depends(get_db)) -> User:
    if not x_user_id:
        raise HTTPException(401, "Missing X-User-Id header")
    me = db.get(User, int(x_user_id))
    if not me:
        raise HTTPException(401, "Invalid user")
    return me

# ---------------------------
# Recommendation Engine
# ---------------------------
def recommend_mentors(db: Session, results: Dict[str, int], top_k: int = 5):
    needs = {k.lower(): max(0, 100 - int(v)) for k, v in results.items()}

    mentors = db.query(MentorProfile).filter(MentorProfile.active == True).all()
    scored = []
    for m in mentors:
        skills = db.query(MentorSkill).filter(MentorSkill.mentor_id == m.id).all()
        skill_map = {s.skill_name.lower(): s.level for s in skills}
        score = sum(needs.get(skill, 0) * int(skill_map.get(skill, 0)) for skill in needs.keys())
        scored.append((m, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
# ---------------------------
# Startup: create tables + seed fake mentors
# ---------------------------
@app.on_event("startup")
def startup():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add_all([
                User(name="Student Demo", role="student"),  # id = 1
                User(name="Admin Demo", role="admin"),      # id = 2
            ])
            db.commit()

        if db.query(MentorProfile).count() == 0:
            m1 = MentorProfile(display_name="Mr Ranjan Peter", is_real=False, bio="Former Software Lead. Guides software career paths.")
            m2 = MentorProfile(display_name="Ms Maya Silva", is_real=False, bio="UI/UX Engineer. Guides software design paths.")
            db.add_all([m1, m2])
            db.commit()

            db.add_all([
                MentorSkill(mentor_id=m1.id, skill_name="Java", level=9),
                MentorSkill(mentor_id=m1.id, skill_name="Backend", level=8),
                MentorSkill(mentor_id=m1.id, skill_name="SQL", level=7),

                MentorSkill(mentor_id=m2.id, skill_name="UI/UX", level=9),
                MentorSkill(mentor_id=m2.id, skill_name="Design", level=8),
                MentorSkill(mentor_id=m2.id, skill_name="Frontend", level=7),
            ])
            db.commit()
    finally:
        db.close()
        
# ---------------------------
# Endpoints
# ---------------------------
@app.get("/")
def home():
    return {"message": "Mentor backend running ✅"}

# Users
@app.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    u = User(name=data.name, role=data.role)
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"id": u.id, "name": u.name, "role": u.role}

# Mentors
@app.get("/mentors")
def list_mentors(db: Session = Depends(get_db)):
    mentors = db.query(MentorProfile).all()
    return [{"id": m.id, "display_name": m.display_name, "is_real": m.is_real, "bio": m.bio, "active": m.active} for m in mentors]
@app.post("/mentors")
def create_mentor(data: MentorCreate, db: Session = Depends(get_db), me: User = Depends(get_me)):
    if me.role != "admin":
        raise HTTPException(403, "Admin only")
    m = MentorProfile(
        display_name=data.display_name, is_real=data.is_real,
        bio=data.bio, active=data.active, user_id=data.user_id
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"mentor_id": m.id}

@app.post("/mentors/{mentor_id}/skills")
def add_mentor_skill(mentor_id: int, data: MentorSkillIn, db: Session = Depends(get_db), me: User = Depends(get_me)):
    if me.role != "admin":
        raise HTTPException(403, "Admin only")
    mentor = db.get(MentorProfile, mentor_id)
    if not mentor:
        raise HTTPException(404, "Mentor not found")
    s = MentorSkill(mentor_id=mentor_id, skill_name=data.skill_name, level=data.level)
    db.add(s)
    db.commit()
    return {"ok": True}

# Assessment + Suggestions (your “Suggested Mentors based on Skill Assessment” page)
@app.post("/assessments", response_model=AssessmentCreateOut)
def create_assessment(db: Session = Depends(get_db), me: User = Depends(get_me)):
    a = Assessment(user_id=me.id)
    db.add(a)
    db.commit()
    db.refresh(a)
    return AssessmentCreateOut(assessment_id=a.id)

@app.post("/assessments/{assessment_id}/results")
def submit_assessment_results(assessment_id: int, data: AssessmentResultsIn, db: Session = Depends(get_db), me: User = Depends(get_me)):
    a = db.get(Assessment, assessment_id)
    if not a or a.user_id != me.id:
        raise HTTPException(404, "Assessment not found")

    for skill, score in data.results.items():
        db.add(AssessmentResult(assessment_id=assessment_id, skill_name=skill, score=int(score)))
    db.commit()
    return {"ok": True}


@app.get("/assessments/{assessment_id}/suggestions")
def get_suggestions(assessment_id: int, db: Session = Depends(get_db), me: User = Depends(get_me)):
    a = db.get(Assessment, assessment_id)
    if not a or a.user_id != me.id:
        raise HTTPException(404, "Assessment not found")

    rows = db.query(AssessmentResult).filter(AssessmentResult.assessment_id == assessment_id).all()
    if not rows:
        raise HTTPException(400, "No results submitted")

    results = {r.skill_name: r.score for r in rows}
    top = recommend_mentors(db, results, top_k=5)
    return [{"mentor_id": m.id, "display_name": m.display_name, "bio": m.bio, "match_score": score} for (m, score) in top]

# Apply / Approve (Apply button -> Request pending/approved)
@app.post("/mentorship/apply")
def apply_for_mentor(data: ApplyIn, db: Session = Depends(get_db), me: User = Depends(get_me)):
    mentor = db.get(MentorProfile, data.mentor_id)
    if not mentor or not mentor.active:
        raise HTTPException(404, "Mentor not available")

    req = MentorshipRequest(student_id=me.id, mentor_id=data.mentor_id, status="pending")
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"request_id": req.id, "status": req.status}  
      
@app.get("/mentorship/my-request")
def my_latest_request(db: Session = Depends(get_db), me: User = Depends(get_me)):
    req = (
        db.query(MentorshipRequest)
        .filter(MentorshipRequest.student_id == me.id)
        .order_by(MentorshipRequest.id.desc())
        .first()
    )
    if not req:
        return {"has_request": False}

    mentor = db.get(MentorProfile, req.mentor_id)
    return {
        "has_request": True,
        "request_id": req.id,
        "status": req.status,
        "mentor": {"id": mentor.id, "display_name": mentor.display_name, "bio": mentor.bio}
    }
@app.patch("/mentorship/requests/{request_id}")
def approve_or_reject_request(request_id: int, data: ApproveIn, db: Session = Depends(get_db), me: User = Depends(get_me)):
    if me.role != "admin":
        raise HTTPException(403, "Admin only (for demo)")
    req = db.get(MentorshipRequest, request_id)
    if not req:
        raise HTTPException(404, "Request not found")
    if data.status not in ("approved", "rejected"):
        raise HTTPException(400, "status must be approved or rejected")
    req.status = data.status
    db.commit()
    return {"request_id": req.id, "status": req.status}