import os
import sys
import json
from pathlib import Path

# Setup paths
ml_root = Path(__file__).resolve().parent.parent
sys.path.append(str(ml_root))

from core.recommendation_engine import RecommendationEngine

def run_full_simulation():
    print("\n" + "="*80)
    print("   PATHFINDER+ HIGH-FIDELITY USER JOURNEY SIMULATION (18-POINT ASSESSMENT)")
    print("="*80)
    
    # Initialize Engine
    print("\n[STEP 1/3] Initializing System...")
    engine = RecommendationEngine(
        jobs_path=ml_root / "data/processed/all_jobs_master.csv",
        courses_path=ml_root / "data/processed/all_courses_master.csv",
        esco_dir=ml_root / "data/raw/esco",
        show_progress=False
    )
    
    print("\n[STEP 2/3] Profile Collection (Manual Entry)")
    
    # 1. Base Info
    status = input("Current Status (O/L Student, A/L Student, Undergraduate, Graduate, Working Professional): ") or "Undergraduate"
    exp = input("Total Experience (None, < 1 year, 1-3 years, 3-5 years, 5+ years): ") or "None"
    resp = input("Responsibility Level (Followed instructions, Completed independent tasks, Planned tasks, Supervised others, Managed outcomes / budgets): ") or "Followed instructions"
    
    # 2. Behavioral (Simulating Q7-Q12)
    print("\n[Behavioral Component] Enter A, B, C, or D for the following (Standardized Scoring):")
    q7 = input("Q7 (Problem Solving): ") or "A"
    q8 = input("Q8 (Decision Making): ") or "A"
    q9 = input("Q9 (Team Role): ") or "A"
    q10 = input("Q10 (Adaptability): ") or "A"
    q11 = input("Q11 (Efficiency): ") or "A"
    q12 = input("Q12 (Conflict Resolution): ") or "A"
    
    # 3. Open Prompts (Semantic Intent)
    print("\n[Technical Component] Describe your background:")
    background = input("Career Background / Bio: ") or "I am a computer science student interested in AI."
    q13 = input("Q13 (Most proud project / achievement): ") or "Built a weather station."
    q15 = input("Q15 (Target role or dream job): ") or "Data Scientist"
    
    # 4. Constraints
    budget = input("\nBudget Range (< 50k, 50k-200k, 200k-500k, 500k+): ") or "50k-200k"
    edu_pref = input("Education Preference (BSc, MSc, Diploma, Certification, None): ") or "Certification"
    
    # 5. Resume (Simulating File Upload)
    print("\n[STEP 3/3] Simulating Resume Upload")
    resume_text = input("Paste Resume Text (to extract skills): ") or "Skills: Python, SQL, Machine Learning, Data Analysis."
    
    print("\n" + "-"*60)
    print("   PROCESSING MATCHES...   ".center(60, "-"))
    print("-"*60 + "\n")

    # Construct the Full 18-Point Dictionary
    answers = {
        "status": status,
        "total_experience": exp,
        "responsibility_level": resp,
        "q7": q7, "q8": q8, "q9": q9, "q10": q10, "q11": q11, "q12": q12,
        "career_background": background,
        "q13": q13,
        "q15": q15,
        "budget_range": budget,
        "education_type": edu_pref,
        "weekly_time": "5-10 hours"
    }

    # Process Assessment -> Vector
    vector = engine.process_comprehensive_assessment(answers)
    
    # Process Resume -> Skills
    resume_skills = engine.parse_resume_text(resume_text)
    print(f"[RESUME ANALYZED] Found {len(resume_skills)} skills: {', '.join(resume_skills[:5])}...")
    
    # Merge Skills
    vector["extracted_intent_skills"] = list(set(vector.get("extracted_intent_skills", []) + resume_skills))
    
    # Get Final Recommendations
    target_job = q15 if q15 else "Software Engineer"
    bundle = engine.get_recommendations_from_assessment(vector, target_job)
    
    # FINAL DISPLAY
    print("\n" + " PATHFINDER+ RESULTS BUNDLE ".center(80, "#"))
    print(f"User: TEST-MANUAL-ENTRY | Target: {target_job}")
    print(f"CRI Score: {bundle['readiness_score'].get('overall', 0)}/100")
    print("#"*80)
    
    # Progression
    print("\n[CAREER ROADMAP]")
    vert = bundle.get('vertical_roadmap', [])
    if vert: print(f"  Vertical Path: {vert[0]['role']} ({vert[0]['typical_years']}) -> {vert[0]['advice']}")
    
    horiz = bundle.get('horizontal_roadmap', [])
    if horiz: print(f"  Horizontal Pivot: {horiz[0]['role']} -> {horiz[0]['advice']}")

    # Courses
    print("\n[TOP RECOMMENDATIONS]")
    for r in bundle.get('recommendations', [])[:2]:
        print(f"  - {r['course_name']} ({r['provider']}) | {r['fee']}")
        print(f"    Rationale: {r.get('why_recommended', 'Matched skills')}")

    # Salary
    salary = bundle.get('salary_estimate', {})
    if isinstance(salary, dict):
        print(f"\n[MARKET DATA] Expected Salary: {salary.get('min', 'N/A')} - {salary.get('max', 'N/A')} LKR")

    print("\n" + "="*80)
    print(" In your report, this is called: 'End-to-End User Journey Simulation (EUJS)' ".center(80, "="))
    print("="*80 + "\n")

if __name__ == "__main__":
    run_full_simulation()
