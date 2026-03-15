from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

# Import our modular service
from chat_service import ChatService

# Load .env from the current folder
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="PathFinder+ Chatbot API")

# Setup CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev; narrow this down for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
