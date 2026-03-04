
import sys
from pathlib import Path

# Add project root to path
ml_root = Path(__file__).resolve().parent.parent
sys.path.append(str(ml_root))

from core.recommendation_engine import RecommendationEngine

def verify_fixes():
    base_dir = Path(__file__).resolve().parent.parent
    jobs_path = base_dir / "data" / "processed" / "all_jobs_master.csv"
    courses_path = base_dir / "data" / "processed" / "all_courses_master.csv"
    esco_dir = base_dir / "data" / "raw" / "esco"
    
    print("--- VERIFICATION START ---")
    
    # 1. Test Unified Loading
    print("\n[1] Testing Unified Data Loading...")
    engine = RecommendationEngine(
        jobs_path=str(jobs_path),
        courses_path=str(courses_path),
        esco_dir=str(esco_dir),
        show_progress=True
    )
    
    print(f"Professional Courses: {len(engine.courses_df)}")
    print(f"Academic Courses: {len(engine.academic_df)}")
    
    if len(engine.academic_df) == 0:
        print("[FAIL] No academic courses loaded from unified dataset!")
    else:
        print("[PASS] Academic courses extracted correctly.")

    # 2. Test MSc Preference Fix
    print("\n[2] Testing MSc Preference Bug Fix...")
    # Simulate an Undergraduate wanting an MSc
    vector = {
        "status_level": 2, # Undergraduate/Professional
        "education_preference": "MSc",
        "budget_category": "200k-500k",
        "extracted_intent_skills": ["Machine Learning", "Python", "Data Analysis"],
        "responsibility_band": 1
    }
    
    results = engine.get_recommendations_from_assessment(vector, "Data Scientist")
    
    academic_hits = results.get('academic_recommendations', [])
    print(f"Total Academic Recommendations: {len(academic_hits)}")
    
    msc_found = False
    for r in academic_hits[:5]:
        print(f"  - {r['course_name']}")
        if "MSc" in r['course_name'] or "Master" in r['course_name']:
            msc_found = True
            
    if msc_found:
        print("[PASS] MSc courses found in recommendations (Bug Fixed).")
    else:
        print("[FAIL] No MSc courses found despite preference.")

    # 3. Verify Roadmap Split
    print("\n[3] Verifying Roadmap Split...")
    if 'vertical_roadmap' in results and 'horizontal_roadmap' in results:
        print(f"Vertical Paths: {len(results['vertical_roadmap'])}")
        print(f"Horizontal Paths: {len(results['horizontal_roadmap'])}")
        print("[PASS] Roadmaps are separated for backend.")
    else:
        print("[FAIL] Roadmaps are not separated.")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    verify_fixes()
