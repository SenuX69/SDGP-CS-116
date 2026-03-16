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

