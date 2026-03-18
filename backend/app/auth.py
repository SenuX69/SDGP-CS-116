from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# TEMP database
fake_users_db = []


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
# REGISTER API
# =========================

@router.post("/register")
def register(user: UserRegister):

    # check if email already exists
    for u in fake_users_db:
        if u["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(user.password)

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password
    }

    fake_users_db.append(new_user)

    return {"message": "User registered successfully"}


# =========================
# LOGIN API
# =========================

@router.post("/login")
def login(user: UserLogin):

    for u in fake_users_db:
        if u["email"] == user.email:
            if pwd_context.verify(user.password, u["password"]):
                return {
    "message": "Login successful",
    "name": u["name"]
}

    raise HTTPException(status_code=400, detail="Invalid credentials")