import os
import sys

# Setup paths
ml_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ml_root)

from core.recommendation_engine import RecommendationEngine

def run_interactive_simulation():
    print("\n" + "="*60)
    print("   PATHFINDER+ INTERACTIVE USER SIMULATION")
    print("="*60)
    
    # Initialize Engine
    print("[1/3] Loading Engine Components...")
    engine = RecommendationEngine(
        jobs_path=os.path.join(ml_root, "data/processed/all_jobs_master.csv"),
        courses_path=os.path.join(ml_root, "data/processed/all_courses_master.csv"),
        esco_dir=os.path.join(ml_root, "data/raw/esco"),
        show_progress=False
    )
    
    print("[2/3] Initialization Complete.")
    print("[3/3] Please enter your profile details below:\n")

    # User Inputs
    name = input("Enter Name (for report): ") or "Test User"
    
    print("\n--- Current Status ---")
    print("0: O/L Student | 1: A/L / UG | 2: Working Professional | 3: Senior")
    status_idx = input("Enter Status Level (0-3): ") or "1"
    status_level = int(status_idx)
    
    skills_input = input("\nEnter your current skills (comma separated): ") or "Python, Logic"
    user_skills = [s.strip() for s in skills_input.split(",")]
    
    target_job = input("\nEnter your Target Career Goal: ") or "Software Engineer"
    
    budget_pref = input("\nEnter Budget Preference (< 50k, 50k-200k, 200k-500k, 500k+): ") or "50k-200k"

    print("\n" + "-"*40)
    print(f"SIMULATING ASSESSMENT FOR: {name}")
    print(f"Targeting: {target_job}")
    print("-"*40 + "\n")

    # Construct a minimal assessment vector
    assessment_vector = {
        "status_level": status_level,
        "extracted_intent_skills": user_skills,
        "budget_category": budget_pref,
        "experience_years": 0 if status_level <= 1 else 3
    }

    # Get Recommendations
    try:
        results = engine.get_recommendations_from_assessment(assessment_vector, target_job)
        
        # Display Results
        print(f"\n>>> [RESULTS] Overall Readiness: {results['readiness_score'].get('overall', 0)}/100")
        
        print("\n--- ROADMAPS ---")
        if results.get('vertical_roadmap'):
            v = results['vertical_roadmap'][0]
            print(f"Vertical: {v['role']} ({v['typical_years']})")
            print(f"Advice: {v['advice']}")
            
        if results.get('horizontal_roadmap'):
            h = results['horizontal_roadmap'][0]
            print(f"Horizontal Pivot: {h['role']}")
            print(f"Advice: {h['advice']}")

        print("\n--- TOP COURSE ---")
        if results.get('recommendations'):
            r = results['recommendations'][0]
            print(f"Course: {r['course_name']} ({r['provider']})")
            print(f"Fee: {r['fee']} | Rationale: {r.get('why_recommended', 'Matched goals')}")

        print("\n--- MARKET DATA ---")
        salary = results.get('salary_estimate', {})
        if isinstance(salary, dict):
             print(f"Typical Salary: {salary.get('min', 'N/A')} - {salary.get('max', 'N/A')} LKR")
        
        print("\nSimulation complete. In reports, this is called 'Interactive Scenario Validation (ISV)'.")
        
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")

if __name__ == "__main__":
    run_interactive_simulation()
