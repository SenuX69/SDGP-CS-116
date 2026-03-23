from fastapi import APIRouter, UploadFile, File, HTTPException, Form
import json
import os as system_os
import sys
import shutil
import tempfile
import fitz
from pydantic import BaseModel
import google.generativeai as genai
import traceback

# Dynamically link the teammate's original offline Scanner engine
sys.path.append(system_os.path.abspath(system_os.path.join(system_os.path.dirname(__file__), "..", "..", "..", "resume", "frontend")))

router = APIRouter()

@router.post("/api/resume-scan")
async def process_standalone_resume_scan(file: UploadFile = File(...), mode: str = Form("gemini")):
    """
    Dedicated endpoint specifically servicing the standalone Resume Analyzer UI component.
    Ingests PDFs and heavily utilizes the gemini-2.5-flash node to reconstruct the data.
    If mode == "local", it instantly forces original offline regex engine.
    """
    try:
        # Save to temp
        fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
        with system_os.fdopen(fd, 'wb') as out_file:
            shutil.copyfileobj(file.file, out_file)
            
        resume_text = ""
        try:
            with fitz.open(tmp_path) as doc:
                for page in doc:
                    resume_text += page.get_text()
        except Exception as pdf_e:
            raise HTTPException(400, "Unable to parse PDF text.")
            
        api_key = system_os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(500, "Server Configuration Error: Missing GEMINI API Key")
        client = genai.Client(api_key=api_key)
        
        # Original Offline Engine (Colleague's Logic)
        if mode == "local":
            try:
                from main import parse_resume, analyze_resume, format_txt
                
                parsed_offline = parse_resume(resume_text)
                analysis_offline = analyze_resume(parsed_offline)
                preview_string = format_txt(parsed_offline, analysis_offline, file.filename)
                system_os.remove(tmp_path)
                
                return {
                    "parsed": parsed_offline,
                    "analysis": analysis_offline,
                    "filename": file.filename,
                    "preview": preview_string
                }
            except Exception as offline_e:
                 system_os.remove(tmp_path)
                 raise HTTPException(500, f"Local Offline Engine Failed: {offline_e}")
        
        #  Gemini Mode
        try:
            prompt = f"""
            You are an elite Career ATS Resume Parser. Read the extremely messy raw text of this resume.
            Output ONLY valid JSON (no markdown block, no ```json). Do NOT hallucinate.
            
            CRITICAL RULES (MUST FOLLOW STRICTLY):
            1. ONLY extract literal emails, phone numbers, LinkedIn, and GitHub URLs for the "links" and contact sections.
            2. NEVER place a Project Name, Framework (like Spring Boot, Chatbot), or University into the "personal_info" block. Look for the actual human Applicant Name only.
            3. CORRECTLY distinguish between Experience (actual jobs/internships), Projects (personal/academic work like "WhatsApp Chatbot"), Education (Universities/Degrees), and References (People's names/contacts like "Mr Neil Devadasan").
            4. DO NOT mash Projects or References into the Professional Summary. The Summary must strictly be 2-3 sentences about the person.
            5. "REFEREES" or "REFERENCES" must be totally ignored from the Education section. Do NOT list a Referee as an Institution.
            6. In the "suggestions" array, give explicit advice on how to improve the RESUME FORMATTING or STRUCTURE (e.g., advising them to move Projects above Education, how to separate Referees from the main text, or fixing layout columns so ATS can read it). 
            7. IMPORTANT FOR ATS SCORE: Infer what Target Job this resume is aiming for. Then, put ALL the candidate's core technical and soft skills into "matched_skills". Then, list exactly 5-8 crucial industry standard skills for their intended role that are MISSING from their resume in "missing_skills". DO NOT leave these arrays empty, the frontend relies on them for scoring!
            
            Structure exactly like this:
            {{
                "parsed": {{
                    "personal_info": {{"name": "...", "email": "...", "phone": "...", "links": ["...", "..."]}},
                    "summary": "...",
                    "skills": ["...", "..."],
                    "experience": [
                        {{"role": "...", "company": "...", "duration": "...", "description": "..."}}
                    ],
                    "education": [
                        {{"degree": "...", "institution": "...", "duration": "..."}}
                    ]
                }},
                "analysis": {{
                    "matched_skills": ["existing_skill_1", "existing_skill_2", "..."],
                    "missing_skills": ["missing_skill_1", "missing_skill_2", "..."],
                    "suggestions": [
                        "A short sentence suggesting how they can rewrite a specific bullet point for impact.",
                        "Another short sentence on missing corporate frameworks to add.",
                        "Direct advice on how they can improve the layout/structure so ATS scanners don't get confused (like making sections distinct)."
                    ]
                }},
                "filename": "parsed_result",
                "preview": "{resume_text[:300].encode('unicode_escape').decode('utf-8')}..."
            }}
            
            RAW TEXT:
            {resume_text}
            """

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            raw_response = response.text.strip()
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
                
            data = json.loads(raw_response.strip())
            system_os.remove(tmp_path)
            return data
            
        except Exception as gemini_e:
            print(f"[Gemini ATS Failure - Falling Back to Local Math Model]: {gemini_e}")
            # OFFLINE BACKUP MODE: Reroute to original teammate's 500-line Regex script
            try:
                from main import parse_resume, analyze_resume, format_txt
                
                parsed_offline = parse_resume(resume_text)
                analysis_offline = analyze_resume(parsed_offline)
                preview_string = format_txt(parsed_offline, analysis_offline, file.filename)
                
                system_os.remove(tmp_path)
                
                # Transform to exactly match the React TSX payload requirement
                return {
                    "parsed": parsed_offline,
                    "analysis": analysis_offline,
                    "filename": file.filename,
                    "preview": preview_string
                }
            except Exception as offline_e:
                print(f"[CRITICAL] Offline Fallback Failed: {traceback.format_exc()}")
                system_os.remove(tmp_path)
                raise HTTPException(500, f"Both Gemini and Local Engines Failed: {offline_e}")

    except Exception as e:
        print(f"CRITICAL SCANNER ERROR: {e}")
        try:
            system_os.remove(tmp_path)
        except:
             pass
        raise HTTPException(status_code=500, detail=str(e))
