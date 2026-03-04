import sys
import os
import json
import pandas as pd

# Add the root directory to path to see core
base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)

from core.recommendation_engine import RecommendationEngine

def run_comprehensive_test(use_cloud=True):
    print("==================================================")
    print(f" COMPREHENSIVE SYSTEM TEST ({'CLOUD' if use_cloud else 'LOCAL'})")
    print("==================================================")
    
    # 1. Initialize Engine
    try:
        if use_cloud:
            engine = RecommendationEngine.from_mongo()
        else:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            jobs_path = os.path.join(base_dir, "data", "processed", "all_jobs_master.csv")
            courses_path = os.path.join(base_dir, "data", "processed", "all_courses_master.csv")
            esco_dir = os.path.join(base_dir, "data", "raw", "esco")
            engine = RecommendationEngine(jobs_path, courses_path, esco_dir, show_progress=False)
    except Exception as e:
        print(f"CRITICAL: Engine Init Failed: {e}")
        return
    
    print("Engine Loaded Successfully")

    # DEFINE PERSONAS
    personas = [
        {
            "name": "The Student (Intern Seeker)",
            "target_role": "Data Scientist",
            "assessment": {
                "status": "Undergraduate",
                "total_experience": "None",
                "responsibility_level": "Followed instructions",
                "budget_range": "< 50k",
                "weekly_time": "10-20 hours",
                "q13": "I learned Python and want to work with data.",
                "q15": "Data Scientist"
            }
        },
        {
            "name": "The Professional (Career Climber)",
            "target_role": "Senior Software Engineer",
            "assessment": {
                "status": "Employed (Full-Time)",
                "total_experience": "3-5 years",
                "responsibility_level": "Planned tasks", # Band 2
                "budget_range": "200k–500k",
                "weekly_time": "5-10 hours",
                "q13": "Led a team of 3 developers to build a React app.",
                "q15": "Senior Software Architect"
            }
        },
        {
            "name": "The Switcher (QA -> DevOps)",
            "target_role": "DevOps Engineer",
            "assessment": {
                "status": "Employed (Full-Time)",
                "total_experience": "1-3 years",
                "responsibility_level": "Completed independent tasks", # Band 1
                "budget_range": "50k–200k",
                "weekly_time": "10-20 hours",
                "q13": "Automated testing with Selenium.",
                "q15": "DevOps Engineer managing CI/CD pipelines"
            }
        }
    ]

    for p in personas:
        print(f"\n--------------------------------------------------")
        print(f"TESTING PERSONA: {p['name']}")
        print(f"--------------------------------------------------")
        
        # 1. Process Assessment
        vector = engine.process_comprehensive_assessment(p['assessment'])
        print(f"   Profile Vector: Status={vector['status_level']}, Exp={vector['experience_years']}, Band={vector['responsibility_band']}")
        print(f"   Intent Skills: {vector['extracted_intent_skills']}")
        
        # 2. Career Path
        progression = engine.get_career_progression(p['target_role'], vector['responsibility_band'], vector['extracted_intent_skills'], assessment_vector=vector)
        print(f"\n   [CAREER PATHS]:")
        for path in progression[:2]:
            print(f"   - {path['type']}: {path['role']} ({path.get('advice', '')[:50]}...)")
            
        # 3. Job Recommendations / Skill Gap

        
        
        # A. Courses
        print(f"\n   [COURSE RECS]:")
        try:
            # [FIX] get_recommendations_from_assessment returns a dict, courses are under 'recommendations' key
            response = engine.get_recommendations_from_assessment(vector, p['target_role'])
            courses = response.get('recommendations', []) 
            
            for c in courses[:3]:
                fee_display = c.get('fee', 'N/A')
                print(f"   - {c['course_name']} ({c['provider']}) | Fee: {fee_display}")
        except Exception as e:
            print(f"   [ERROR] Course Recs Failed: {e}")

        # B. Mentors
        print(f"\n   [MENTOR MATCHES]:")
        try:
            mentors = engine.match_mentors(vector['extracted_intent_skills'])
            for m in mentors:
                is_prem = "[PREMIUM] " if m.get('is_premium') else ""
                print(f"   - {is_prem}{m['name']} ({m['specialization']}) | Score: {m['score']}")
        except AttributeError:
             print("   [ERROR] match_mentors method not found on engine.")
        except Exception as e:
            print(f"   [ERROR] Mentor Match Failed: {e}")

    print("\n==================================================")
    print("      TEST COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    # Check if cloud should be skipped (e.g. no internet)
    run_comprehensive_test(use_cloud=True)
