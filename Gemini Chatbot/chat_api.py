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

# Setup Database connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DATABASE_NAME")]

# Initialize the ChatService (Standalone mode: no engine passed)
chat_service = ChatService(db=db)

# Data structure for the incoming request
class ChatRequest(BaseModel):
    user_id: str
    message: str
    history: Optional[List[Dict[str, Any]]] = []

<<<<<<< HEAD
import time

# Rate limiting storage (user_id -> last_timestamp)
user_last_request: Dict[str, float] = {}
RATE_LIMIT_SECONDS = 5.0  # 1 message per 5 seconds

=======
>>>>>>> d46034006fbfab04e3addc49f7ed278fccc8bba9
@app.post("/api/chat")
async def chat_with_ui(request: ChatRequest):
    """
    Endpoint that the frontend or Postman will call.
    """
<<<<<<< HEAD
    current_time = time.time()
    last_req_time = user_last_request.get(request.user_id, 0.0)
    
    # Enforce Rate Limit
    if current_time - last_req_time < RATE_LIMIT_SECONDS:
        return {"reply": "You're sending queries too quickly! Our AI needs a moment to catch its breath. Please wait 5 seconds before asking again."}
    
    user_last_request[request.user_id] = current_time

=======
>>>>>>> d46034006fbfab04e3addc49f7ed278fccc8bba9
    try:
        reply = chat_service.get_reply(
            user_id=request.user_id,
            user_message=request.message,
            chat_history=request.history
        )
        return {"reply": reply}
    
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    # Runs the server on port 8002
    uvicorn.run(app, host="0.0.0.0", port=8002)
