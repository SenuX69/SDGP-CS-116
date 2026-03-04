import sys
import os
from pathlib import Path

# Setup paths relative to project root (Machine Learning and Data Cleaning)
ml_root = Path(__file__).resolve().parent.parent
sys.path.append(str(ml_root))

from core.recommendation_engine import RecommendationEngine

def run_comprehensive_scenarios():
    output_file = ml_root / "final_comprehensive_results.txt"
    def log(msg):
        print(msg)
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    if output_file.exists(): 
        output_file.unlink()

    log("="*80)
    log("PATHFINDER+ FINAL COMPREHENSIVE VERIFICATION: 10 GLOBAL SCENARIOS")
    log("="*80)
    
    # Initialize Engine
    engine = RecommendationEngine(
        jobs_path=ml_root / "data/processed/all_jobs_master.csv",
        courses_path=ml_root / "data/processed/all_courses_master.csv",
        esco_dir=ml_root / "data/raw/esco",
        show_progress=False
    )
    
    log(f"DEBUG: Loaded {len(engine.market_skills)} unique market skills for extraction.")
    
    scenarios = [
        {
            "id": 1,
            "name": "Nimal (Computer Science Graduate)",
            "assessment": {
                "status": "Fresh Graduate",
                "total_experience": "None",
                "responsibility_level": "Followed instructions",
                "q13": "I did my final project in Django and built a small IoT weather station.",
                "q14": "Startup or innovative tech firm.",
                "q15": "Full Stack Developer",
                "budget_range": "50k-100k"
            },
            "target": "Full Stack Developer"
        },
        {
            "id": 2,
            "name": "Aruni (Bank Manager Transitioning)",
            "assessment": {
                "status": "Career Transitioning",
                "total_experience": "10+ years",
                "responsibility_level": "Defined strategy",
                "q13": "Led a team of 15; managed branch operations and customer relations.",
                "q14": "FinTech or Data Analysis in Banking.",
                "q15": "Wants to move into Fintech Product Management.",
                "budget_range": "200k-500k"
            },
            "target": "Product Manager"
        },
        {
            "id": 3,
            "name": "Sandun (Self-taught Freelancer)",
            "assessment": {
                "status": "Working Professional",
                "total_experience": "1-3 years",
                "career_background": "I am a self-taught developer mainly focused on frontend development. I know HTML, CSS, JavaScript, and some TypeScript. I have been freelancing for a few years and want a stable role.",
                "problem_solving": "B", "decision_making": "B", "team_role": "A", "adaptability": "D", "efficiency": "B", "conflict": "A"
            },
            "target": "Frontend Developer"
        },
        {
            "id": 4,
            "name": "Tharaka (Systems Admin -> DevOps)",
            "assessment": {
                "status": "Working Professional",
                "total_experience": "5-10 years",
                "career_background": "I manage Linux servers and networking infrastructure. I have started learning Docker, Kubernetes, and CI/CD pipelines. I am looking to transition into a DevOps Engineer role.",
                "problem_solving": "C", "decision_making": "C", "team_role": "B", "adaptability": "C", "efficiency": "C", "conflict": "B"
            },
            "target": "DevOps Engineer"
        },
        {
            "id": 5,
            "name": "Zahra (Graphic Designer -> UX)",
            "assessment": {
                "status": "Career Transitioning",
                "total_experience": "3-5 years",
                "career_background": "I am a visual designer with 4 years of experience using Adobe Creative Suite. I want to specialze in user experience and interface design using Figma and user research methods.",
                "problem_solving": "B", "decision_making": "B", "team_role": "C", "adaptability": "B", "efficiency": "A", "conflict": "C"
            },
            "target": "UX Designer"
        },
        {
            "id": 6,
            "name": "Kumara (O/L Drop-out Explorer)",
            "assessment": {
                "status": "O/L Student",
                "total_experience": "None",
                "career_background": "I like fixing electronics and building small hardware gadgets. I want to learn more about embedded systems and computer hardware engineering.",
                "problem_solving": "A", "decision_making": "A", "team_role": "D", "adaptability": "A", "efficiency": "C", "conflict": "A"
            },
            "target": "Hardware Engineer"
        },
        {
            "id": 7,
            "name": "Malini (Return-to-work Mom)",
            "assessment": {
                "status": "Career Break",
                "total_experience": "3-5 years",
                "career_background": "I previously worked as a quality assurance tester for 3 years before taking a gap. I am familiar with manual testing, bug reporting, and software development lifecycles.",
                "problem_solving": "B", "decision_making": "C", "team_role": "B", "adaptability": "C", "efficiency": "B", "conflict": "B"
            },
            "target": "QA Engineer"
        },
        {
            "id": 8,
            "name": "Roshan (Marketing -> Digital Marketing)",
            "assessment": {
                "status": "Working Professional",
                "total_experience": "1-3 years",
                "career_background": "I have a background in traditional marketing. I am learning SEO, SEM, and social media advertising to transition fully into digital marketing roles.",
                "problem_solving": "B", "decision_making": "B", "team_role": "C", "adaptability": "B", "efficiency": "B", "conflict": "C"
            },
            "target": "Digital Marketing Specialist"
        },
        {
            "id": 9,
            "name": "Shehani (Data Entry -> Data Analyst)",
            "assessment": {
                "status": "Working Professional",
                "total_experience": "3-5 years",
                "career_background": "My current role is in data entry and database maintenance. I am learning SQL and Python for data analysis and visualization to move into a more analytical career.",
                "problem_solving": "B", "decision_making": "A", "team_role": "B", "adaptability": "C", "efficiency": "D", "conflict": "B"
            },
            "target": "Data Analyst"
        },
        {
            "id": 10,
            "name": "Anonymous (Free Cert Seeker)",
            "assessment": {
                "status": "A/L Student",
                "total_experience": "None",
                "career_background": "I am a student self-learning Python and machine learning through free online resources. I want to build a career as a backend developer focusing on AI integration.",
                "problem_solving": "B", "decision_making": "B", "team_role": "B", "adaptability": "B", "efficiency": "B", "conflict": "B"
            },
            "target": "Python Developer"
        }
    ]
    
    for s in scenarios:
        log(f"\n>>> PROCESSING SCENARIO {s['id']}: {s['name']} -> Target: {s['target']}")
        try:
            # 1. Process Assessment
            vector = engine.process_comprehensive_assessment(s['assessment'])
            skills = vector.get('extracted_intent_skills', [])
            log(f"   [PROFILE] Band: {vector['responsibility_band']} | Experience: {vector.get('experience_years')} yrs | Status Level: {vector.get('status_level')}")
            log(f"   [DETECTED SKILLS] {skills if skills else 'None (Semantic match only)'}")
            
            # 2. Get Bundle Recommendations
            bundle = engine.get_recommendations_from_assessment(vector, s['target'])
            
            # 3. Score Breakdown
            cri = bundle.get('readiness_score', {})
            log(f"   [CRI BREAKDOWN] Overall: {cri.get('overall')}/100")
            log(f"     - Skills Match: {cri.get('skills_match')}% | Experience: {cri.get('experience')}%")
            log(f"     - Responsibility: {cri.get('responsibility')}% | Clarity: {cri.get('clarity')}%")
            log(f"     - Comm/Intent: {cri.get('communication')}% | Stage: {cri.get('stage')}")
            
            # 4. Detailed Recommendations
            log(f"   [TOP PROFESSIONAL COURSES]")
            for i, r in enumerate(bundle.get('recommendations', [])[:3]):
                log(f"     {i+1}. {r['course_name']} ({r['provider']})")
                log(f"        - Level: {r['level']} | Score: {r['relevance_score']:.2f} | Fee: {r['fee']}")
                log(f"        - Rationale: {', '.join(r.get('why_recommended', ['Matched goals']))}")
            
            acad = bundle.get('academic_recommendations', [])
            if acad:
                log(f"   [TOP ACADEMIC COURSES]")
                for i, r in enumerate(acad[:2]):
                    log(f"     {i+1}. {r['course_name']} ({r['provider']})")
                    log(f"        - Level: {r['level']} | Score: {r['relevance_score']:.2f} | Fee: {r['fee']}")
            
            # 5. Job & Salary
            log(f"   [MARKET DATA]")
            salary = bundle.get('salary_estimate', {})
            if isinstance(salary, dict):
                log(f"     - Typical Salary Range: {salary.get('min', 'N/A')} - {salary.get('max', 'N/A')} LKR")
            else:
                log(f"     - Typical Salary Range: {salary}")
            
            job = bundle.get('job_ideas', [{}])[0]
            if isinstance(job, dict):
                log(f"     - Sample Job: {job.get('job_title', 'N/A')} at {job.get('company', 'Unknown')}")
                log(f"     - Skill Gap Pct: {job.get('skill_gap_pct', 'N/A')}%")
            else:
                log(f"     - Sample Job Info: {job}")
            
            # 6. Roadmaps & Trends
            vert = bundle.get('vertical_roadmap', [])
            horiz = bundle.get('horizontal_roadmap', [])
            if vert:
                log(f"   [VERTICAL ROADMAP] {vert[0]['role']} (Typical: {vert[0]['typical_years']})")
                log(f"      - Advice: {vert[0]['advice']}")
            if horiz:
                # Log up to 2 horizontal pivots for brevity
                pivots = [h['role'] for h in horiz[:2]]
                log(f"   [HORIZONTAL PIVOTS] {', '.join(pivots)}")
                log(f"      - Advice: {horiz[0]['advice']}")
            
            trends = bundle.get('market_trends', {})
            log(f"   [TRENDS] {trends.get('recommendation', 'Keep upskilling!')}")
            
            # 7. Skill Gaps
            gaps = bundle.get('compulsory_skills', [])
            log(f"   [SKILL GAPS] Critical focus: {gaps[:5]}")
            
            log(f"   {'-'*40}")
            
        except Exception as e:
            log(f"   [ERROR] Scenario {s['id']} failed: {str(e)}")
            # log(traceback.format_exc()) # Optional: more detail

    log("\n" + "="*80)
    log("COMPREHENSIVE VERIFICATION COMPLETE - ALL 10 PERSONAS PROCESSED")
    log("="*80)

if __name__ == "__main__":
    run_comprehensive_scenarios()
