
#PathFinder+ Career Guidance Chatbot

import os
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient

# Step 1: Load API keys from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI      = os.getenv("MONGO_URI")
DATABASE_NAME  = os.getenv("DATABASE_NAME", "pathfinder_plus")
