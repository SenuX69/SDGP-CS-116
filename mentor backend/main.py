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
    level = Column(Integer, nullable=False)  # 1-10    
        