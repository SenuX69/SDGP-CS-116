import sys
import os
from pathlib import Path
import json

# Add the scripts directory to path
ml_root = Path(__file__).resolve().parent.parent
sys.path.append(str(ml_root))

from core.recommendation_engine import RecommendationEngine

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    print("\n" + "="*80)
    print(f" {text.center(78)} ")
    print("="*80 + "\n")

def get_choice(prompt, options):
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")
    while True:
        choice = input(f"Select (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice)-1]
        print("Invalid selection. Try again.")

def final_simulation():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    jobs_path = base_dir / "data" / "processed" / "all_jobs_master.csv"
    courses_path = base_dir / "data" / "processed" / "all_courses_master.csv"
    esco_dir = base_dir / "data" / "raw" / "esco"
    
    clear_screen()
    print_header("PathFinder+ | THE ULTIMATE CAREER ECOSYSTEM SIMULATION")
    print("Initializing Engine... [Loading SBERT, ESCO Taxonomy, and Market Trend Data]")
    
    try:
        engine = RecommendationEngine(
            jobs_path=str(jobs_path),
            courses_path=str(courses_path),
            esco_dir=str(esco_dir),
            show_progress=False
        )
    except Exception as e:
        print(f"\n[ERROR] Engine failed to start: {e}")
        return

    print("\n[SUCCESS] Engine Ready!")
    input("\nPress Enter to start your personalized career assessment...")

    answers = {}

    #  PART 1: IDENTITY & STAGE 
    clear_screen()
    print_header("PART 1: WHO ARE YOU?")
    
    target_job = input("What is your Target Job Role? (e.g., Data Scientist): ").strip() or "Software Engineer"
    
    answers["status"] = get_choice("What is your current career/education stage?", 
                                  ["O/L Student", "A/L Student", "Undergraduate", "Working Professional", "Career Transitioning"])
    
    answers["highest_education"] = get_choice("Your highest level of education?", 
                                           ["GCE O/L", "GCE A/L", "Diploma", "Bachelor's Degree", "Master's / PhD"])

    answers["total_experience"] = get_choice("Total professional experience?", 
                                          ["0 (None)", "< 1 year", "1-3 years", "3-5 years", "5+ years"])

    answers["responsibility_level"] = get_choice("Your typical level of technical responsibility?",
        ["Followed instructions", "Completed independent tasks", "Planned tasks", "Supervised others", "Managed outcomes / budgets"])

    #  PART 2: ASPIRATIONS & SKILLS 
    clear_screen()
    print_header("PART 2: CAREER GOALS & SKILL EXTRACTION")
    print("Answer briefly to help our AI profile your potential.")

    answers["q13"] = input("\n[STRENGTH] Describe a project, tool, or skill you are most proud of: ").strip()
    answers["q15"] = input("[VIRTUAL GOAL] Where do you want to be in 3 years? (Specify role/field): ").strip()
    answers["q16"] = input("[BARRIER] What is the biggest hurdle in your way right now?: ").strip()

    # --- PART 3: BUDGET & LOGISTICS ---
    clear_screen()
    print_header("PART 3: EDUCATION PLANNING PREFERENCES")

    answers["budget_range"] = get_choice("What is your Course Budget Preference?", 
                                      ["< 50k", "50k-200k", "200k-500k", "500k+"])
    
    answers["weekly_time"] = get_choice("Weekly time commitment for learning?", 
                                     ["< 5 hours", "5-10 hours", "10-20 hours", "20+ hours"])
    
    answers["education_type"] = get_choice("What type of education are you currently looking for?", 
                                        ["BSc / Undergraduate Degree", "MSc / Postgraduate Degree", "Professional Certification", "Diploma", "No preference"])

    # --- GENERATION ---
    clear_screen()
    print_header("ANALYZING YOUR PROFILE & REAL-TIME MARKET TRENDS")
    print("Matching your skills against 5,000+ Sri Lankan jobs and 2,000+ courses...")
    
    # Process Vector
    vector = engine.process_comprehensive_assessment(answers)
    
    # Get Results
    courses_res = engine.get_recommendations_from_assessment(vector, target_job)
    career_paths = engine.get_career_progression(target_job, vector["responsibility_band"], vector.get("extracted_intent_skills", []), vector)
    mentors = engine.match_mentors(vector.get("extracted_intent_skills", []))
    salary = engine.get_salary_for_role(target_job)
    readiness = engine.calculate_readiness_score(vector.get("extracted_intent_skills", []), vector, target_job)
    trends = engine.get_market_trends(target_job)

    # --- FINAL DASHBOARD ---
    clear_screen()
    print_header("YOUR PathFinder+ CAREER DASHBOARD")
    
    print(f"TARGET ROLE : {target_job.upper()}")
    print(f"PROFILE     : {answers['status']} (Edu: {answers['highest_education']})")
    print("-" * 80)
    
    # 1. READINESS & SALARY
    print(f"CAREER READINESS INDEX: {readiness['overall']}%")
    print(f"  Stage   : {readiness['stage']}")
    print(f"  Salary  : {salary} (SL Market Average)")
    
    # 2. SKILL GAP
    print("\n[!] CRITICAL SKILL GAP (Missing for your role):")
    gaps = courses_res.get('skill_gap', [])
    if gaps:
        print(f"  - {', '.join(gaps[:8])}...")
    else:
        print("  - No major gaps detected! You are market-ready.")

    # 3. MARKET TRENDS
    print(f"\n MARKET INSIGHTS FOR '{trends.get('field', 'General')}':")
    top_skills = [s.upper() for s in list(trends.get('top_demanded_skills', {}).keys())[:4]]
    print(f"  HOT SKILLS : {', '.join(top_skills)}")
    segments = trends.get('segments', [])
    if segments:
        print(f"  DEMAND     : High in '{segments[0]['segment']}' and related roles.")

    # 4. COURSES (With Prices)
    print("\n PROFESSIONAL SKILL-GAP COURSES (QUICK UPSKILLING):")
    for i, c in enumerate(courses_res.get('recommendations', [])[:8], 1): # Increased
        fee = c.get('fee', 'N/A')
        print(f"  {i}. {c['course_name']} [{c['provider']}]")
        print(f"     Fee: {fee} | Url: {c.get('url', '#')}")
        print(f"     Why: {c.get('why_recommended', '')[:80]}...")

    # 4b. ACADEMIC LEARNING PATHS (DIPLOMAS/DEGREES)
    print("\n ACADEMIC LEARNING PATHS (LONG-TERM GAPS):")
    acad = courses_res.get('academic_recommendations', [])
    if acad:
        for i, c in enumerate(acad[:8], 1): # Increased
            fee = c.get('fee', 'N/A')
            print(f"  {i}. {c['course_name']} [{c['provider']}]")
            print(f"     Level: {c.get('level', 'Degree')} | Fee: {fee} | Url: {c.get('url', '#')}")
            print(f"     Why: {', '.join(c.get('why_recommended', [])) if isinstance(c.get('why_recommended'), list) else c.get('why_recommended')}")
    else:
        print("  - No direct academic matches found for this specific gap.")

    # 5. CAREER GROWTH MILESTONES (Roadmaps)
    print("\n VERTICAL CAREER ROADMAP (Promotions):")
    vert = courses_res.get('vertical_roadmap', [])
    if vert:
        for i, p in enumerate(vert[:5], 1):
            print(f"  - {p['role']} (Typical: {p['typical_years']})")
            print(f"    Advice: {p.get('advice', '')[:100]}...")
    else:
        print("  - Standard progression path applies.")

    print("\n HORIZONTAL CAREER PIVOTS (Alternative Roles):")
    horiz = courses_res.get('horizontal_roadmap', [])
    if horiz:
        for i, p in enumerate(horiz[:5], 1):
            print(f"  - {p['role']}")
            print(f"    Advice: {p.get('advice', '')[:100]}...")
    else:
        print("  - Highly specialized role; few horizontal pivots found.")

    # 6. JOB RECOMMENDATIONS (with Salary)
    print("\n SIMILAR JOB OPPORTUNITIES (PAYLAB INTEGRATED):")
    for i, j in enumerate(courses_res.get('job_ideas', [])[:3], 1):
        print(f"  {i}. {j['job_title']} at {j['company']}")
        print(f"     Est. Salary: {j['estimated_salary']} | Link: {j.get('url', '#')}")

    # 6b. 12-MONTH COACHING ROADMAP
    print("\n 12-MONTH COACHING ROADMAP (MONTH-BY-MONTH):")
    plan = courses_res.get('action_plan', [])
    for item in plan:
        print(f"  - {item['period']}: {item['focus']}")
        print(f"    Milestone: {item['milestone']}")

    # 7. MENTORS
    print("\n MENTOR MATCHES:")
    for i, m in enumerate(mentors[:2], 1):
        print(f"  - {m['name']} ({m['specialization']}) at {m.get('company', 'Sri Lanka Tech')}")

    print("\n" + "="*80)
    print(" Simulation Complete. PathFinder+ handles everything from Gap Analysis to Mentorship.")
    print("="*80)

if __name__ == "__main__":
    final_simulation()
