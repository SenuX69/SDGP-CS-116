from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from supabase import create_client

router = APIRouter()

SUPABASE_URL = "https://fivqjyegpeatgeatbbdj.supabase.co"
SUPABASE_KEY = "sb_publishable_Bt0svPzhOpYB8X_2tWAv_g_-9bb0D89"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# MODELS
# =========================

class UserRegister(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# =========================
# REGISTER
# =========================

@router.post("/register")
def register(user: UserRegister):

    # check if user exists
    existing = supabase.table("users").select("*").eq("email", user.email).execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="User already exists")

    # hash password
    hashed_password = pwd_context.hash(user.password)

    # insert user
    supabase.table("users").insert({
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }).execute()

    return {"message": "User registered successfully"}


# =========================
# LOGIN
# =========================

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