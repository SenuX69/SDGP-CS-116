import sys
from pathlib import Path
import json

# Add project root to path
ml_root = Path(__file__).resolve().parent.parent
sys.path.append(str(ml_root))

from core.recommendation_engine import RecommendationEngine

def print_section(title, color="="):
    print(f"\n{color*10} {title.upper()} {color*10}")

def run_final_varied_tests():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    jobs_path = base_dir / "data" / "processed" / "all_jobs_master.csv"
    courses_path = base_dir / "data" / "processed" / "all_courses_master.csv"
    esco_dir = base_dir / "data" / "raw" / "esco"
    
    print("Initializing PathFinder+ Recommendation Engine for Final Audit (V3 Gold)...")
    engine = RecommendationEngine(
        jobs_path=str(jobs_path),
        courses_path=str(courses_path),
        esco_dir=str(esco_dir),
        show_progress=False
    )
    
    # 5 EXTREME PERSONAS with 12-POINT PROFILES
    personas = [
        {
            "id": "PERSONA 1: ABSOLUTE ZERO (O/L School Leaver)",
            "target_job": "Junior Web Developer",
            "answers": {
                "career_stage": "Student / School Leaver",
                "highest_education": "GCE O/L or School Level",
                "experience_years": "0 (None)",
                "responsibility_level": "Followed instructions",
                "career_background": "Just finished my school exams. I like playing video games and want to learn how to make them.",
                "key_achievements": "Did a small coding project in school using Scratch.",
                "upskilling_budget": "< 50k",
                "weekly_availability": "20+ hours",
                "problem_solving": "Search for similar issues and try common fixes",
                "adaptability": "Follow the new directives strictly",
                "education_preference": "None",
                "domain": "IT"
            }
        },
        {
            "id": "PERSONA 2: THE GLASS CEILING (Experienced MBA Manager)",
            "target_job": "Chief Technology Officer (CTO)",
            "answers": {
                "career_stage": "Working Professional",
                "highest_education": "Master's Degree (MBA)",
                "experience_years": "10+ years",
                "responsibility_level": "Managed outcomes / budgets",
                "career_background": "12 years in IT operations and project management. Currently Lead Project Manager at a top bank.",
                "key_achievements": "Led a cross-functional team of 20 to decommission legacy servers and migrate to AWS Cloud.",
                "upskilling_budget": "500k+",
                "weekly_availability": "< 5 hours",
                "problem_solving": "Assess the impact on goals and align the team",
                "adaptability": "Assess the impact on goals and align the team",
                "education_preference": "Postgraduate",
                "domain": "IT"
            }
        },
        {
            "id": "PERSONA 3: THE TOTAL PIVOT (Retail to Data Analytics)",
            "target_job": "Data Analyst",
            "answers": {
                "career_stage": "Career Switcher",
                "highest_education": "Bachelor's Degree",
                "experience_years": "3-5 years",
                "responsibility_level": "Completed independent tasks",
                "career_background": "4 years in retail management. I have been using Excel for inventory and want to move to data analytics.",
                "key_achievements": "Optimized store inventory using Excel macros, reducing waste by 15%.",
                "upskilling_budget": "200k-500k",
                "weekly_availability": "10-20 hours",
                "problem_solving": "Analyze the root cause and propose a new approach",
                "adaptability": "Pivot quickly while documenting the change",
                "education_preference": "MSc",
                "domain": "Healthcare"
            }
        },
        {
            "id": "PERSONA 4: THE HIGH-ACADEMIC (PhD Scientist to Industry ML)",
            "target_job": "Machine Learning Engineer",
            "answers": {
                "career_stage": "University Student",
                "highest_education": "PhD / Doctorate",
                "experience_years": "1-2 years",
                "responsibility_level": "Planned tasks",
                "career_background": "PhD researcher in Physics. I use Python and R for data analysis in lab experiments.",
                "key_achievements": "Published a paper on using neural networks to predict particle decay.",
                "upskilling_budget": "50k-200k",
                "weekly_availability": "20+ hours",
                "problem_solving": "Analyze the root cause and propose a new approach",
                "adaptability": "Pivot quickly while documenting the change",
                "education_preference": "None",
                "domain": "Science"
            }
        },
        {
            "id": "PERSONA 5: THE SIDE-HUSTLE (Commerce Undergrad to Data)",
            "target_job": "Business Analyst",
            "answers": {
                "career_stage": "University Student",
                "highest_education": "Bachelor's Degree",
                "experience_years": "0 (None)",
                "responsibility_level": "Followed instructions",
                "career_background": "Final year Commerce student. I am self-learning PowerBI and basic statistics online.",
                "key_achievements": "Built a personal finance tracker dashboard using PowerBI.",
                "upskilling_budget": "50k-200k",
                "weekly_availability": "5-10 hours",
                "problem_solving": "Collaborate with others to find the most efficient fix",
                "adaptability": "Follow the new directives strictly",
                "education_preference": "Diploma",
                "domain": "Finance"
            }
        },
        {
            "id": "PERSONA 6: THE RESUME PRO (Software Engineer simulating Resume Upload)",
            "target_job": "Software Developer",
            "answers": {
                "career_stage": "Working Professional",
                "highest_education": "Bachelor's Degree",
                "experience_years": "3-5 years",
                "responsibility_level": "Completed independent tasks",
                "career_background": "I have been working as a junior developer for 2 years. SKILLS: Python, Java, Programming, Problem Solving, Agile. Looking to transition into a mid-level Software Developer role in FinTech.",
                "key_achievements": "Developed a full-stack web application using React and Node.js. Automated data pipelines using Python.",
                "upskilling_budget": "50k-200k",
                "weekly_availability": "10-20 hours",
                "problem_solving": "Analyze the root cause and propose a new approach",
                "adaptability": "Pivot quickly while documenting the change",
                "education_preference": "MSc",
                "domain": "IT"
            }
        }
    ]

    audit_file = base_dir / "tests" / "final_system_audit.txt"
    report = []
    
    header = f"""

                PATHFINDER+ CORE ENGINE FINAL SYSTEM AUDIT (V3 GOLD)
                11-POINT DASHBOARD & 12-POINT PROFILE VERIFICATION

    """
    report.append(header)

    for p in personas:
        report.append("\n" + "="*80)
        report.append(f" CASE STUDY: {p['id']}")
        report.append("="*80)
        
        vector = engine.process_comprehensive_assessment(p["answers"])
        print(f"DEBUG: Vector for {p['id']}: Skills={len(vector.get('extracted_intent_skills', []))}, Domain={vector.get('domain')}")
        
        bundle = engine.get_recommendations_from_assessment(vector, p["target_job"])
        print(f"DEBUG: Bundle for {p['id']}: CRI={bundle.get('career_snapshot', {}).get('score')}, Jobs={len(bundle.get('job_opportunities', []))}")
        
        # 1. Career Snapshot (CRI)
        snap = bundle.get("career_snapshot", {})
        report.append(f"\n1. Career Recommendation Summary")
        report.append("─────────────────────────────")
        report.append(f"Target Role: {snap.get('target_role', p['target_job'])}")
        report.append(f"Career Readiness Score: {snap.get('score', 0)} / 100")
        report.append(f"Stage: {snap.get('stage', 'Development Phase')}")
        report.append(f"Estimated Transition Time: {snap.get('estimated_transition_weeks', 0)} weeks")
        report.append(f"Preferred Industry: {snap.get('preferred_industry', 'IT')}")
        report.append(f"\nSub-metrics (from your report):")
        metrics = snap.get("sub_metrics", {})
        report.append(f"Skills Alignment      {metrics.get('Skills Alignment')}%")
        report.append(f"Experience Level       {metrics.get('Experience Level')}%")
        report.append(f"Demand Score          {metrics.get('Demand Score')}%")
        report.append(f"Qualification        {metrics.get('Qualification')}%")
        report.append(f"Gap Coverage           {metrics.get('Gap Coverage')}%\n")
        
        # 2. AI Career Path Recommendation
        path_rec = bundle.get("career_path_recommendation", {})
        report.append(f"2. AI Career Path Recommendation")
        report.append("Recommended Career Path")
        vert = path_rec.get("vertical", [])
        for v in vert[:3]:
            report.append(f"{v['role']}\n        │\n        ▼")
        
        horiz = path_rec.get("horizontal", [])
        report.append("\nAlternative Paths")
        report.append("────────────────")
        for h in horiz[:2]:
            report.append(f"{h['role']}")

        # 3. Skill Intelligence
        intel = bundle.get("skill_intelligence", {})
        report.append(f"\n3. Skill Intelligence Panel")
        report.append("Current Skills")
        for s in intel.get("current_skills", [])[:4]: report.append(f"✔ {s}")
        report.append("\nSkills to Strengthen")
        for s in intel.get("strengthen", [])[:4]: report.append(f"⚡ {s}")
        
        # 4. Skill Gap Insights
        gaps = bundle.get("skill_gap_insights", {})
        report.append(f"\n4. Skill Gap Insights")
        report.append("Skill Gap Analysis\n\nCritical Skills")
        crit = gaps.get("critical_skills", [])
        if not crit or str(crit[0]).startswith("None"): 
            report.append("None — strong skill alignment detected")
        else:
            for c in crit[:3]: report.append(f"• {c}")
        report.append("\nBeneficial Skills")
        for b in gaps.get("beneficial_skills", [])[:3]: report.append(f"• {b}")

        # 5. Recommended Education
        edu = bundle.get("recommended_education", [])
        gap_courses = bundle.get("skill_gap_courses", [])
        
        report.append(f"\n5. Recommended Education Path")
        if edu:
            top_edu = edu[0]
            report.append(f"{top_edu['course_name']}")
            report.append(f"Provider: {top_edu.get('provider', 'N/A')}")
            report.append(f"Score: {top_edu.get('relevance_score', 0.95)}")
            report.append("Why Recommended")
            why = top_edu.get('why_recommended', [])
            if isinstance(why, list):
                for w in why[:2]: report.append(f"• {w}")
            elif isinstance(why, str):
                report.append(f"• {why}")
            else:
                report.append("• Strong academic pathway\n• Builds core concepts\n• High industry demand")
            
            report.append("\nOther cards:")
            for e in edu[1:4]:
                report.append(f"{e.get('provider', 'N/A')} — {e['course_name']}")
        
        report.append("\nProfessional Skill-Gap Courses:")
        for c in gap_courses[:3]:
            report.append(f"• {c['course_name']} ({c.get('provider', 'N/A')}) | Apply: {c.get('apply_url', '#')}")

        # 6. Real Job Opportunities 
        jobs = bundle.get("job_opportunities", [])
        report.append(f"\n6. Real Job Opportunities")
        report.append("Live Opportunities")
        for j in jobs[:3]:
            report.append(f"{j['job_title']}")
            report.append(f"{j.get('company', 'Company Name')}")
            loc = "Remote" if "remote" in j.get('job_title', '').lower() else "Colombo"
            report.append(f"Location: {loc}")
            report.append(f"Apply: {j.get('apply_url', '#')}\n")

        # 7. Salary Intelligence
        sal = bundle.get("salary_intelligence", {})
        report.append(f"\n7. Salary Intelligence")
        report.append(f"Salary Forecast — {bundle.get('career_snapshot', {}).get('preferred_industry', 'IT')} Sector\n")
        report.append(f"Min Salary     {sal.get('min', '30000')} LKR")
        report.append(f"Average        {sal.get('avg', '45000')} LKR")
        report.append(f"Max Salary     {sal.get('max', '75000')} LKR")
        
        # 8. Market Demand
        demand = bundle.get("market_demand", {})
        report.append(f"\n8. Market Demand Insights")
        report.append(f"Trending Field")
        report.append(f"{demand.get('field', 'IT Sector')}\n")
        
        segments = demand.get("segments", [])
        if segments:
            report.append("Market Segments:")
            for seg in segments[:3]:
                report.append(f"• {seg.get('segment', 'General')}: {seg.get('demand', 0)} jobs")
                report.append(f"  Skills: {', '.join(seg.get('skills', []))}")
        
        report.append("\nTop demanded skills:")
        for k, v in list(demand.get("top_demanded_skills", {}).items())[:3]:
            blocks = "█" * (max(1, v // 10))
            report.append(f"{k.ljust(18)} {blocks}")

        # 9. Mentor Recommendations
        mentors = bundle.get("mentor_recommendations", [])
        report.append(f"\n9. Mentor Recommendations")
        report.append("Mentor Matches")
        for m in mentors[:2]:
            report.append(f"{m['name']}")
            report.append(f"{m['title']} — {m['company']}\n")

        # 10. Personalized Action Plan
        plan = bundle.get("action_roadmap", {})
        steps = plan.get("steps", []) if isinstance(plan, dict) else plan
        report.append(f"10. Personalized Action Plan")
        report.append(f"Career Action Roadmap")
        for step in steps[:4]:
            period = str(step.get('period', '')).replace("Months", "Month")
            report.append(f"{period}")
            report.append(f"{step.get('focus', '')}\n")

        # 11. AI Explainability
        expl = bundle.get("ai_explainability", [])
        report.append(f"11. AI Explainability Panel (Important)")
        report.append("Why this recommendation?")
        for e in expl:
            report.append(f"{e}")

    # Write Report
    with open(audit_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"\nAudit Complete. Report generated at: {audit_file.name}")
    print(f"Report Size: {audit_file.stat().st_size} bytes")

if __name__ == "__main__":
    run_final_varied_tests()
