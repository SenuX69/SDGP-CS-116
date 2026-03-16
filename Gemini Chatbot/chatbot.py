
#PathFinder+ Career Guidance Chatbot

import os
from dotenv import load_dotenv
import google.generativeai as genai
from pymongo import MongoClient

# Step 1: Load API keys from .env file
load_dotenv()
