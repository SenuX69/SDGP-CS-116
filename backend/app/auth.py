from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from supabase import create_client
import os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
try:
    supabase = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
except:
    supabase = None

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta=None):
    return "simulated_token"

def verify_token(token: str):
    return {"sub": "dummy@test.com"}


# MODELS
class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# REGISTER

@router.post("/register")
def register(user: UserRegister):

    # check if user exists
    existing = supabase.table("users").select("*").eq("email", user.email).execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="User already exists")

    # hashing password
    hashed_password = pwd_context.hash(user.password)

    # insert user
    supabase.table("users").insert({
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }).execute()

    return {"message": "User registered successfully"}


# LOGIN
@router.post("/login")
def login(user: UserLogin):

    response = supabase.table("users").select("*").eq("email", user.email).execute()

    if not response.data:
        raise HTTPException(status_code=400, detail="User not found")

    db_user = response.data[0]

    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    return {
        "message": "Login successful",
        "name": db_user["name"],
        "email": db_user["email"]
    }
