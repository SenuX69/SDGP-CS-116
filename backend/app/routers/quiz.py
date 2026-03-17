from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class QuizData(BaseModel):
    name: str
    email: str
    role: str
    goal: str
    education: str
    answers: Dict[str, int]


@router.post("/quiz")
def save_quiz(data: QuizData):
    return {
        "career": "Software Engineer",
        "description": "You are analytical and problem-solving oriented.",
        "skills": ["Python", "Problem Solving", "Algorithms"],
        "courses": ["CS50", "React Course", "Data Structures"],
        "jobs": ["Intern Developer", "Junior Engineer"]
    }