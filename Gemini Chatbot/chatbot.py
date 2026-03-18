
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

# Step 2: Connect to MongoDB 
def connect_to_mongodb():
    """Connect to MongoDB and return the database object."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")  # Test the connection
        print(" Connected to MongoDB")
        return client[DATABASE_NAME]
    except Exception as e:
        print(f"  Could not connect to MongoDB: {e}")
        print("   The chatbot will still work, but won't use course/job data.")
        return None

#  Step 3: Get data from MongoDB
def get_courses(db, limit=3):
    """Fetch a few courses from the database."""
    if db is None:
        return []
    try:
        courses = list(db["courses"].find({}, {"title": 1, "provider": 1, "url": 1, "_id": 0}).limit(limit))
        return courses
    except Exception as e:
        print(f" Could not fetch courses: {e}")
        return []

def get_jobs(db, limit=3):
    """Fetch a few job listings from the database."""
    if db is None:
        return []
    try:
        jobs = list(db["jobs"].find({}, {"title": 1, "company": 1, "apply_url": 1, "_id": 0}).limit(limit))
        return jobs
    except Exception as e:
        print(f" Could not fetch jobs: {e}")
        return []

# Step 4: Build context from database
def build_context(db):
    """Turn database results into a text block for the AI to use."""
    courses = get_courses(db)
    jobs    = get_jobs(db)

    context = ""

    if courses:
        context += "Available Courses on PathFinder+:\n"
        for c in courses:
            context += f"  - {c.get('title', 'N/A')} by {c.get('provider', 'N/A')} | {c.get('url', '')}\n"
        context += "\n"

    if jobs:
        context += "Available Jobs on PathFinder+:\n"
        for j in jobs:
            context += f"  - {j.get('title', 'N/A')} at {j.get('company', 'N/A')} | {j.get('apply_url', '')}\n"
        context += "\n"

    return context

# Step 5: Set up Gemini AI
def setup_gemini():
    """Configure and return the Gemini AI model."""
    genai.configure(api_key=GEMINI_API_KEY)

    # This is the chatbot's personality and rules
    system_prompt = """
    You are PathFinder+ chatbot, a friendly career guidance assistant for students in Sri Lanka.
    Your job is to help users find suitable careers, courses, and job opportunities.

    Rules:
    - Be friendly, short, and helpful.
    - If the user is given course or job data, mention those first.
    - If no internal data is available, suggest: LinkedIn, Glassdoor, Coursera, or Udemy.
    - Never make up job titles, salaries, or course details.
    - Keep answers under 200 words.
    """

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt
    )
    print(" Gemini AI ready")
    return model

# Step 6: Ask the AI a question 
def ask_gemini(model, chat_history, user_message, db):
    """Send a message to Gemini and get a reply."""

    # Get fresh data from MongoDB to help answer the question
    context = build_context(db)

    # If we have data, add it to the message so AI can use it
    if context:
        full_message = f"[Data from PathFinder+ database from the mongo database:]\n{context}\n[User question:] {user_message}"
    else:
        full_message = user_message

    try:
        # Start a chat session with the conversation history
        chat    = model.start_chat(history=chat_history)
        reply   = chat.send_message(full_message)
        return reply.text
    except Exception as e:
        return f"Sorry, something went wrong: {e}"

# Step 7: Main chat loop
def main():
    print("=" * 50)
    print("  PathFinder+ Career Chatbot")
    print("  Type 'quit' to exit | 'reset' to start over")
    print("=" * 50)

    # Set up everything
    db    = connect_to_mongodb()
    model = setup_gemini()

    # This list stores the conversation (only in memory, never saved to DB)
    chat_history = []

    print("\nPathFinder+: Hi! I'm your career guidance assistant. How can I help you today?\n")

    # Keep chatting until the user quits
    while True:
        user_input = input("You: ").strip()

        # Handle special commands
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "bye"):
            print("PathFinder+: Good luck with your career journey! 🚀")
            break
        if user_input.lower() == "reset":
            chat_history = []
            print("PathFinder+: Conversation cleared! How can I help you?\n")
            continue

        # Get AI response
        response = ask_gemini(model, chat_history, user_input, db)

        # Save this turn to history (so AI remembers the conversation)
        chat_history.append({"role": "user",  "parts": [user_input]})
        chat_history.append({"role": "model", "parts": [response]})

        print(f"\nPathFinder+: {response}\n")


# Run the chatbot
if __name__ == "__main__":
    main()
