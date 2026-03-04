"""
PathFinder+ Automated Multi-Persona Report Generator
Runs 3 distinct user scenarios end-to-end and writes a detailed
startup-level verification report — suitable for SDGP project documentation.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

ml_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ml_root))

from core.recommendation_engine import RecommendationEngine

REPORT_PATH = ml_root / "assessment_verification_report.txt"

# ──────────────────────────────────────────────────────────────
#  Test Personas (12-Point Assessment Inputs)
# ──────────────────────────────────────────────────────────────
PERSONAS = [
    {
        "name": "The Fresh Graduate — IT Track",
        "answers": {
            "career_stage":      "Student",
            "highest_education": "Bachelor's Degree",
            "experience_years":  "0 (None)",
            "target_role":       "Software Developer",
            "responsibility_level": "Followed instructions",
            "career_background": "Just graduated with a BSc in Computer Science. Skilled in Python and Java. Built academic projects.",
            "key_achievements":  "Final year project: Automated traffic management system using computer vision.",
            "problem_solving":   "Search for similar issues and try common fixes",
            "adaptability":      "Follow the new directives strictly",
            "upskilling_budget": "50k-200k",
            "weekly_availability": "20+ hours",
            "preferred_industry": "FinTech"
        }
    },
    {
        "name": "The Career Switcher — Into Data Analytics",
        "answers": {
            "career_stage":      "Career Switcher",
            "highest_education": "Bachelor's Degree",
            "experience_years":  "3-5 years",
            "target_role":       "Data Analyst",
            "responsibility_level": "Planned tasks",
            "career_background": "4 years in retail management. Recently self-taught SQL and Excel. Passionate about statistics.",
            "key_achievements":  "Reduced inventory waste by 15% by building a custom Excel tracking model.",
            "problem_solving":   "Analyze the root cause and propose a new approach",
            "adaptability":      "Pivot quickly while documenting the change",
            "upskilling_budget": "500k+",
            "weekly_availability": "10-20 hours",
            "preferred_industry": "Healthcare"
        }
    },
    {
        "name": "The Experienced Leader — Digital Marketing",
        "answers": {
            "career_stage":      "Experienced Professional",
            "highest_education": "Master's / PhD",
            "experience_years":  "6-10 years",
            "target_role":       "Digital Marketing Specialist",
            "responsibility_level": "Supervised others",
            "career_background": "Senior marketing executive with 7 years in brand management. Moving into digital-first strategy.",
            "key_achievements":  "Led a brand relaunch campaign reaching 2M+ impressions across social platforms.",
            "problem_solving":   "Collaborate with others to find the most efficient fix",
            "adaptability":      "Assess the impact on goals and align the team",
            "upskilling_budget": "200k-500k",
            "weekly_availability": "5-10 hours",
            "preferred_industry": "E-commerce"
        }
    },
    {
        "name": "The Healthcare Transition — Clinical Nurse",
        "answers": {
            "career_stage":      "Entry-level Professional",
            "highest_education": "Diploma",
            "experience_years":  "1-2 years",
            "target_role":       "Registered Nurse",
            "responsibility_level": "Followed instructions",
            "career_background": "Recently completed nursing diploma. Passionate about patient care and triage. Looking for a full-time ward position.",
            "key_achievements":  "Managed a 10-bed ward efficiently during a staff shortage as a trainee.",
            "problem_solving":   "Analyze the root cause and propose a new approach",
            "adaptability":      "Pivot quickly while documenting the change",
            "upskilling_budget": "50k-100k",
            "weekly_availability": "20+ hours",
            "preferred_industry": "Healthcare"
        }
    }
]

#  Report Writer Helpers

def w(f, line=""):    f.write(line + "\n")
def hr(f, ch="─"):   f.write(ch * 72 + "\n")
def section(f, title):
    w(f)
    hr(f, "━")
    w(f, f"  {title}")
    hr(f, "━")


def write_persona_report(f, persona, vector, bundle):
    target = persona["answers"]["target_role"]
    name   = persona["name"]
    w(f)
    hr(f, "█")
    w(f, f"  PERSONA CASE STUDY: {name.upper()}")
    w(f, f"  Target Role: {target}")
    hr(f, "█")

    # ── Input Profile ──
    section(f, "A.  ASSESSMENT INPUTS (12-POINT PROFILE)")
    for k, v in persona["answers"].items():
        w(f, f"    {k.replace('_', ' ').title():<30} {v}")

    # ── CRI ──
    section(f, "B.  CAREER READINESS INDEX (CRI)")
    cri = bundle.get("readiness_score", {})
    w(f, f"    Overall Score  : {cri.get('overall', 0)}/100")
    w(f, f"    Stage          : {cri.get('stage', 'Development Phase')}")
    hr(f)
    w(f, f"    Skills Alignment    : {cri.get('skills_match', 0):.1f}%")
    w(f, f"    Experience Level    : {cri.get('experience', 0):.1f}%")
    w(f, f"    Responsibility Band : {cri.get('responsibility', 0):.1f}%")
    w(f, f"    Role Clarity        : {cri.get('clarity', 0):.1f}%")
    w(f, f"    Market Intent       : {cri.get('communication', 0):.1f}%")

    # ── Extracted Skills ──
    skills = vector.get("extracted_intent_skills", [])
    section(f, "C.  EXTRACTED INTENT SKILLS (from bio)")
    if skills:
        for s in skills: w(f, f"    ✦ {s}")
    else:
        w(f, "    None detected from bio text.")

    # ── Skill Gaps ──
    must  = bundle.get("compulsory_skills", [])
    nice  = bundle.get("optional_skills", [])
    section(f, "D.  SKILL GAP ANALYSIS (ESCO-Mapped)")
    w(f, "  CRITICAL (must close to enter role):")
    if must:
        for s in must[:6]: w(f, f"    [!] {s}")
    else:
        w(f, "    None — strong skills match detected.")
    w(f)
    w(f, "  BENEFICIAL (value-add):")
    for s in nice[:4]: w(f, f"    [ ] {s}")

    # ── Roadmap ──
    section(f, "E.  CAREER ROADMAP")
    vert  = bundle.get("vertical_roadmap", [])
    horiz = bundle.get("horizontal_roadmap", [])
    w(f, "  VERTICAL PROGRESSION:")
    for step in vert[:2]:
        w(f, f"    → {step['role']}  (Est. {step['typical_years']} years)")
        w(f, f"      Advice: {step['advice']}")
    if horiz:
        w(f)
        w(f, "  LATERAL MOVES:")
        for step in horiz[:2]:
            w(f, f"    ↔ {step['role']}")
            if step.get('advice'): w(f, f"      {step['advice']}")

    # ── Courses ──
    section(f, "F.  RECOMMENDED COURSES & PROGRAMS")
    recs = bundle.get("recommendations", [])
    acad = bundle.get("academic_recommendations", [])
    seen, count = set(), 0
    for r in (recs + acad):
        if r["course_name"] in seen or count >= 5: continue
        count += 1
        seen.add(r["course_name"])
        w(f, f"\n  [{count}] {r['course_name']}")
        w(f, f"      Provider  : {r.get('provider', 'Unknown')}")
        w(f, f"      Level     : {r.get('level', 'Professional')} | Score: {r.get('relevance_score', 0):.3f}")
        w(f, f"      Cost      : {r['fee']}")
        w(f, f"      Duration  : {r.get('duration', 'Flexible')}")
        w(f, f"      Why       : {str(r.get('why_recommended', 'Matched your skill gaps'))[:90]}")
        if r.get('url'): w(f, f"      Link      : {r['url']}")

    # ── Jobs ──
    section(f, "G.  LIVE JOB OPPORTUNITIES")
    jobs = bundle.get("job_ideas", [])
    for j in jobs[:3]:
        if "job_title" in j:
            w(f, f"  ◈  {j['job_title']}  @  {j.get('company', 'Confidential')}")
            w(f, f"      Deadline     : {j.get('deadline', 'Apply Soon')}")
            if j.get("skill_gap_pct") is not None:
                w(f, f"      Your Fit     : {max(0, 100-j['skill_gap_pct']):.0f}% skills match")
            # Added: Specific Missing Skills gap
            if j.get("missing_skills"):
                w(f, f"      Missing Skills : {', '.join(j['missing_skills'])}")
            if j.get("url"): w(f, f"      Apply At     : {j['url']}")

    # ── Salary ──
    section(f, "H.  SALARY INTELLIGENCE")
    sal = bundle.get("salary_estimate", {})
    if isinstance(sal, dict) and sal.get("min"):
        w(f, f"    Entry Level  : LKR {sal.get('min', '?')} / month")
        w(f, f"    Senior Level : LKR {sal.get('max', '?')} / month")
    else:
        w(f, "    Salary data not available for this specific role.")

    # ── Market Trends ──
    section(f, "I.  MARKET INTELLIGENCE")
    trends = bundle.get("market_trends", {})
    if isinstance(trends, dict):
        w(f, f"    Trending Field    : {trends.get('field', '—')}")
        w(f, f"    Recommendation    : {trends.get('recommendation', '—')}")
        hot = trends.get("top_demanded_skills", {})
        if hot:
            w(f)
            w(f, "    TOP IN-DEMAND SKILLS:")
            for skill, cnt in list(hot.items())[:6]:
                bar = "█" * min(int(cnt / max(hot.values()) * 24), 24)
                w(f, f"    {skill:<28} {bar} ({cnt})")
        segs = trends.get("segments", [])
        if segs:
            w(f)
            w(f, "    ACTIVE MARKET SEGMENTS:")
            for seg in segs[:3]:
                w(f, f"    ▸  {seg['segment']}  — {seg['demand']} openings")
                w(f, f"         Hot Skills: {', '.join(seg['skills'][:5])}")

    # ── Mentors ──
    section(f, "J.  MENTOR MATCHES")
    mentors = bundle.get("mentors", [])
    if mentors:
        for m in mentors[:2]:
            w(f, f"    ◈ {m.get('name', 'Mentor')}  |  {m.get('title', '—')}  |  {m.get('company', '—')}")
            skills_str = ", ".join(m.get('matched_skills', [])[:4])
            w(f, f"      Matched Skills: {skills_str if skills_str else m.get('specialization', 'General')}")
    else:
        w(f, "    No direct mentor matches.")

    # ── Action Plan ──
    section(f, "K.  12-MONTH ACTION PLAN")
    plan = bundle.get("action_plan", [])
    # If bundle doesn't provide action plan steps, build one from skill gaps + courses
    if not plan or (plan and not plan[0].get('month') and not plan[0].get('timeline')):
        plan = []
        if must:
            plan.append({"month": "Month 1-3",  "action": f"Close ESCO gap: '{must[0]}' via targeted course or self-study"})
            if len(must) > 1:
                plan.append({"month": "Month 2-4",  "action": f"Address skill: '{must[1]}'"})
        if recs:
            plan.append({"month": "Month 3-6",  "action": f"Enroll in: {recs[0]['course_name']} ({recs[0]['provider']})"})
        plan.append({"month": "Month 6-9",  "action": f"Apply for internships / entry positions targeting '{target}'"})
        plan.append({"month": "Month 9-12", "action": f"Full application campaign for '{target}' — build portfolio, network actively"})
    for step in plan[:6]:
        m = step.get("month", step.get("timeline", ""))
        a = step.get("action", step.get("task", ""))
        w(f, f"    {m:<16} → {a}")

    # ── Alternate Paths ──
    alts = bundle.get("alternate_paths", [])
    if alts:
        section(f, "L.  ALTERNATE CAREER PATHS")
        for path in alts[:4]:
            w(f, f"    ↪ {path['title']}  (Similarity: {path['similarity']:.1%})")

    w(f)
    hr(f, "█")


# ──────────────────────────────────────────────────────────────
#  Main
# ──────────────────────────────────────────────────────────────
def run():
    print(f"\n{'='*60}")
    print("  PathFinder+ Multi-Persona Verification Report Generator")
    print(f"{'='*60}")
    print("  Initializing engine (uses cached .pt files if available)...")

    engine = RecommendationEngine(
        jobs_path=ml_root / "data/processed/all_jobs_master.csv",
        courses_path=ml_root / "data/processed/all_courses_master.csv",
        esco_dir=ml_root / "data/raw/esco",
        show_progress=True
    )
    print("  Engine ready.\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        # Header
        hr(f, "█")
        w(f, "  PATHFINDER+  —  ASSESSMENT VERIFICATION REPORT")
        w(f, f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        w(f, f"  Personas  : {len(PERSONAS)}")
        w(f, f"  Engine    : 12-Point Assessment + ESCO Mapping + SBERT Embeddings")
        hr(f, "█")

        for i, persona in enumerate(PERSONAS):
            print(f"  Processing persona {i+1}/{len(PERSONAS)}: {persona['name']}")
            vector = engine.process_comprehensive_assessment(persona["answers"])
            bundle = engine.get_recommendations_from_assessment(vector, persona["answers"]["target_role"])
            write_persona_report(f, persona, vector, bundle)
            print(f"     Done.")

        # Summary Footer
        w(f)
        hr(f, "█")
        w(f, "  REPORT SUMMARY")
        hr(f, "█")
        w(f, f"  Personas processed : {len(PERSONAS)}")
        w(f, f"  Report path        : {REPORT_PATH}")
        w(f, f"  Sections per case  : A-L (12 sections covering all engine features)")
        hr(f, "█")

    print(f"\n  Report saved to: {REPORT_PATH}")
    print(f"  {'='*56}")


if __name__ == "__main__":
    run()
