import os
import google.generativeai as genai
from dotenv import load_dotenv

class ChatService:
    def __init__(self, db=None):
        self.db = db          #  MongoDB
        self._setup_gemini()

    def _setup_gemini(self):
        """Configure Gemini with a strict persona to save tokens since well this is a free tier accut."""
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Instruction for the model
        self.system_instructions = (
            "You are the PathFinder+ Senior Academic & Career Advisor. The USER is a student or job-seeker "
            "seeking your guidance. "
            "MANDATE: Provide authoritative, professional, and highly specific guidance on Sri Lankan "
            "universities, degree programs, and career paths. "
            "VOICE: Direct, concierge-level helpfulness, and strictly factual. Avoid conversational filler. "
            "IDENTITY: You are the AI Advisor. The USER is the human student. Never confuse these roles. "
            "SILENT KNOWLEDGE: Never reference internal datasets, CSV files, or DATABASE records. "
            "GUARDRAILS: If a user asks non-career personal questions (e.g., 'whats my name'), politely pivot: "
            "'I focus on academic and career advisory. How can I help with your professional goals?'"
        )

        # Using models/gemma-3-1b-it as and it is light and effcient for our needs and uses fewer tokens
        self.model = genai.GenerativeModel(
            model_name="models/gemma-3-1b-it"
        )

    def get_academic_context(self, query):
        """Searches MongoDB for relevant academic programs and skill-gap courses from mongo db to make it cloud capable."""
        if self.db is None: return ""
        try:
            # 1. Smarter Keyword Extraction: Include short but critical terms
            # We keep words > 4 chars, OR specific short academic/tech terms
            critical_terms = {"bsc", "msc", "ba", "ma", "it", "cs", "ai", "law", "imb"}
            words = [kw.lower() for kw in str(query).split() if len(kw) > 4 or kw.lower() in critical_terms]
            
            if not words: words = ["university", "career", "study", "job", "institute", "college", "school"]
            
            # Create a regex pattern for multi-keyword search
            pattern = "|".join(words)
            
            # 2. Query Academic degrees(bsc,msc type ones)
            academic_hits = self.db.courses_academic.find({
                "$or": [
                    {"course_title": {"$regex": pattern, "$options": "i"}},
                    {"category": {"$regex": pattern, "$options": "i"}}
                ]
            }).limit(5)
            
            # 3. Query Skill Gap courses
            skill_hits = self.db.courses.find({
                "$or": [
                    {"course_title": {"$regex": pattern, "$options": "i"}},
                    {"category": {"$regex": pattern, "$options": "i"}}
                ]
            }).limit(5)
            
            results = []
            for r in academic_hits:
                results.append(f"Degree: {r.get('course_title')} at {r.get('provider')}")
            for r in skill_hits:
                results.append(f"Course: {r.get('course_title')} ({r.get('provider')})")
                
            return " | ".join(results[:8]) if results else ""
        except Exception: 
            return ""

    def get_job_context(self, query):
        """Searches MongoDB for relevant Sri Lankan job vacancies from which we scraped from."""
        if self.db is None: return ""
        try:
            words = [kw.lower() for kw in str(query).split() if len(kw) > 3]
            if not words: return ""
            pattern = "|".join(words)
            
            job_hits = self.db.jobs.find({
                "$or": [
                    {"title": {"$regex": pattern, "$options": "i"}},
                    {"company": {"$regex": pattern, "$options": "i"}},
                    {"category": {"$regex": pattern, "$options": "i"}}
                ]
            }).limit(5)
            
            results = [f"Job: {j.get('title')} at {j.get('company')}" for j in job_hits]
            return " | ".join(results) if results else ""
        except Exception:
            return ""

    def get_smart_context(self, user_id, user_message=""):
        """Silent RAG only answers what it is questioned for and based on context and try not to hallucinate."""
        context_parts = []
        acad = self.get_academic_context(user_message)
        jobs = self.get_job_context(user_message)
        if acad: context_parts.append(f"Academic: {acad}")
        if jobs: context_parts.append(f"Live Vacancies: {jobs}")
        if self.db is not None:
            user = self.db.users.find_one({"_id": user_id})
            if user: 
                context_parts.append(f"User Profile: Skills={user.get('skills')}, Goal={user.get('target_job')}")
        
        return " | ".join(context_parts) if context_parts else ""

    def get_reply(self, user_id, user_message, chat_history=None):
        """Standard reply logic using the smart context."""
        try:
            facts = self.get_smart_context(user_id, user_message)
            full_prompt = (
                f"{self.system_instructions}\n\n"
                f"{facts}\n\n"
                f"USER: {user_message}"
            )
            
            chat = self.model.start_chat(history=chat_history or [])
            response = chat.send_message(full_prompt)
            return response.text
 
        except Exception as e:
            print(f"DEBUG - AI Error: {e}")
            return "I'm having a technical hiccup right now. Please try again in a minute!"


if __name__ == "__main__":
    # This allows you to run the file directly for testing
    from pymongo import MongoClient
    
    # Setup connection from the env files
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DATABASE_NAME")]
    
    # Initialize (we'll skip the RecommendationEngine for now to keep it simple otherwise too problematic for now probably a future feature)
    service = ChatService(db=db)
    
    print("--- PathFinder+ Chatbot CLI Test ---")
    while True:
        user_in = input("You: ")
        if user_in.lower() in ["exit", "quit"]: break
        print(f"Assistant: {service.get_reply('test_user', user_in)}\n")
