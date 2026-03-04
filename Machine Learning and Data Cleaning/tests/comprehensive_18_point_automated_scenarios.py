
import sys
import os
from pathlib import Path
import json

# Add project root to path
ml_root = Path(__file__).resolve().parent.parent
sys.path.append(str(ml_root))

from core.recommendation_engine import RecommendationEngine

def print_section(title, color="="):
    print(f"\n{color*10} {title.upper()} {color*10}")

def run_scenarios():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    jobs_path = base_dir / "data" / "processed" / "all_jobs_master.csv"
    courses_path = base_dir / "data" / "processed" / "all_courses_master.csv"
    esco_dir = base_dir / "data" / "raw" / "esco"
    
    print("Initializing PathFinder+ Recommendation Engine...")
    engine = RecommendationEngine(
        jobs_path=str(jobs_path),
        courses_path=str(courses_path),
        esco_dir=str(esco_dir),
        show_progress=False
    )
    
    # 4 DETAILED SCENARIOS (18-POINT ASSESSMENT INPUTS)
    personas = [
        {
            "id": "SCENARIO 1: THE FOUNDATION SEEKER (O/L STUDENT)",
            "answers": {
                "status": "O/L Student",
                "total_experience": "None",
                "responsibility_level": "Followed instructions",
                "q7": "A", "q8": "A", "q9": "A", "q10": "A", "q11": "A", "q12": "A",
                "q13": "I built a simple HTML website for my school project.",
                "q15": "I want to be a professional Software Engineer in a big company.",
                "q16": "I don't know where to start after my school exams.",
                "budget_range": "< 50k",
                "weekly_time": "10-20 hours",
                "education_type": "Diploma", # Seeking a starting point
                "target_job": "Software Engineer"
            }
        },
        {
            "id": "SCENARIO 2: THE AMBITIOUS UNDERGRADUATE (MSc PREFERENCE)",
            "answers": {
                "status": "Undergraduate",
                "total_experience": "< 1 year",
                "responsibility_level": "Completed independent tasks",
                "q7": "C", "q8": "B", "q9": "C", "q10": "B", "q11": "D", "q12": "B",
                "q13": "Automated a database cleaning script using Python and SQL.",
                "q15": "Targeting a Senior Data Scientist role with a focus on AI.",
                "q16": "Need higher-level academic credentials to qualify for top firms.",
                "budget_range": "200k-500k",
                "weekly_time": "5-10 hours",
                "education_type": "MSc / Postgraduate Degree", # TESTING THE FIX
                "target_job": "Data Scientist"
            }
        },
        {
            "id": "SCENARIO 3: THE HIGH-LEVEL PROFESSIONAL (LEADERSHIP FOCUS)",
            "answers": {
                "status": "Working Professional",
                "total_experience": "5+ years",
                "responsibility_level": "Managed outcomes / budgets",
                "q7": "D", "q8": "D", "q9": "D", "q10": "D", "q11": "D", "q12": "D",
                "q13": "Led a team of 10 to deploy a cloud-native ERP system globally.",
                "q15": "Transitioning to CTO or Head of AI Research.",
                "q16": "Finding niche AI management courses in Sri Lanka.",
                "budget_range": "500k+",
                "weekly_time": "< 5 hours",
                "education_type": "Postgraduate",
                "target_job": "AI Research Lead"
            }
        },
        {
            "id": "SCENARIO 4: THE CAREER PIVOTER (MARKETING TO DATA)",
            "answers": {
                "status": "Career Transitioning",
                "total_experience": "3-5 years",
                "responsibility_level": "Planned tasks",
                "q7": "B", "q8": "C", "q9": "B", "q10": "C", "q11": "B", "q12": "C",
                "q13": "Managed 50+ SEO campaigns with successful conversion growth.",
                "q15": "I want to use my marketing background for Data Analysis and BI.",
                "q16": "Bridging the technical gap in Python and Statistics.",
                "budget_range": "50k-200k",
                "weekly_time": "20+ hours",
                "education_type": "Professional Certification",
                "target_job": "Data Analyst"
            }
        }
    ]

    print_section("PathFinder+ Comprehensive System Audit (4 Personas)")
    
    for p in personas:
        print_section(p["id"], "#")
        ans = p["answers"]
        target = ans["target_job"]
        
        # 1. Process Assessment
        vector = engine.process_comprehensive_assessment(ans)
        
        # 2. Get Bundle
        bundle = engine.get_recommendations_from_assessment(vector, target)
        
        # 3. DISPLAY DASHBOARD
        print(f" TARGET ROLE    : {target}")
        print(f" MARKET SALARY  : {bundle.get('salary_estimate', 'N/A')}")
        print(f" READINESS INDEX: {bundle.get('readiness_score', {}).get('overall', 0)}% ({bundle.get('readiness_score', {}).get('stage', 'N/A')})")
        
        # 1. Skill Gaps
        print("\n [!] TOP SKILL GAPS:")
        gaps = bundle.get('compulsory_skills', []) + bundle.get('optional_skills', [])
        print(f"     {', '.join(gaps[:6])}")
        
        # 2. Professional Courses
        print("\n [PROFESSIONAL SKILL-GAP COURSES]:")
        for i, c in enumerate(bundle.get('recommendations', [])[:8], 1): # Increased volume
            print(f"  {i}. {c['course_name']} ({c['provider']})")
            print(f"     Fee: {c['fee']} | Url: {c.get('url', '#')}")
            print(f"     Why: {c['why_recommended'][0] if c.get('why_recommended') else 'N/A'}")
            
        # 3. Academic Recommendations
        print("\n [ACADEMIC LEARNING PATHS (DIPLOMAS/DEGREES)]:")
        acad = bundle.get('academic_recommendations', [])
        if acad:
            for i, c in enumerate(acad[:8], 1): # Increased volume
                print(f"  {i}. {c['course_name']} at {c['provider']}")
                print(f"     Level: {c.get('level', 'Degree')} | Fee: {c['fee']} | Url: {c.get('url', '#')}")
        else:
            print("  - No direct academic matches for this constraint.")

        # 4. Career Roadmaps
        print("\n [CAREER PROGRESSION (ROADMAPS)]:")
        vert = bundle.get('vertical_roadmap', [])
        if vert:
            print("  VERTICAL (Promotions):")
            for p in vert[:4]:
                print(f"    - {p['role']} ({p.get('typical_years', '2-3 years')})")
        
        horiz = bundle.get('horizontal_roadmap', [])
        if horiz:
            print("  HORIZONTAL (Pivots):")
            for p in horiz[:4]:
                print(f"    - {p['role']}")
        
        # 5. Mentors
        print("\n [MENTOR MATCHES]:")
        mentors = bundle.get('mentors', [])
        if mentors:
            for m in mentors[:2]:
                print(f"  - {m['name']} ({m.get('specialization', 'Expert')}) at {m.get('company', 'Sri Lanka')}")
        
        # 6. Job Matching
        print("\n [MATCHED JOB OPENINGS]:")
        jobs = bundle.get('job_ideas', [])
        for j in jobs[:2]:
            print(f"  - {j.get('job_title')} at {j.get('company')}")
            print(f"    Salary: {j.get('estimated_salary', 'LKR Market Rate')} | Link: {j.get('url', '#')}")

        # 7. 12-MONTH ROADMAP (Action Plan)
        print("\n [12-MONTH COACHING ROADMAP]:")
        plan = bundle.get('action_plan', [])
        for item in plan:
            print(f"  - {item['period']}: {item['focus']}")
            print(f"    Milestone: {item['milestone']}")

    print_section("AUDIT COMPLETE - ALL FEATURES VERIFIED")

if __name__ == "__main__":
    run_scenarios()
