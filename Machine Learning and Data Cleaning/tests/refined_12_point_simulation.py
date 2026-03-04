"""
PathFinder+ Interactive Simulation - Startup-Level Output
Shows ALL available features: CRI, Skill Gaps, Roadmap, Courses, Jobs, Mentors, Market Trends, Action Plan
"""
import sys
from pathlib import Path
from datetime import datetime

ml_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ml_root))

from core.recommendation_engine import RecommendationEngine

# ─────────────────────────────────────────────────
#  Print Helpers
# ─────────────────────────────────────────────────
def section(title):
    print(f"\n{'━'*70}")
    print(f"  {title}")
    print(f"{'━'*70}")

def sub(label, value=""):
    if value: print(f"  {'':2}{label:<30} {value}")
    else:      print(f"  {label}")

def star(text):       print(f"  ✦ {text}")
def warn(text):       print(f"  ⚠ {text}")
def check(text):      print(f"  ✓ {text}")
def bullet(text):     print(f"  • {text}")
def divider():        print(f"  {'—'*66}")


def run_simulation():
    print("\n" + "█"*70)
    print("  PATHFINDER+  ―  Intelligent Career Recommendation Engine")
    print("  Startup-Level Interactive Simulation | 12-Point Assessment")
    print("█"*70)
    print(f"  Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ── Engine Init ──
    print("\n  Initializing AI Engine...")
    engine = RecommendationEngine(
        jobs_path=ml_root / "data/processed/all_jobs_master.csv",
        courses_path=ml_root / "data/processed/all_courses_master.csv",
        esco_dir=ml_root / "data/raw/esco",
        show_progress=False
    )
    print("  Engine Ready.\n")

    # ── Section 1: Profile Collection ──
    section("PROFILE BUILDER  (Press Enter to use smart defaults)")
    career_stage  = input("  Career Stage [Student/Entry-level Professional/Experienced Professional/Career Switcher]: ") or "Entry-level Professional"
    edu           = input("  Highest Education [GCE O/L / GCE A/L / Bachelor's Degree / Master's / PhD]: ") or "Bachelor's Degree"
    exp           = input("  Years of Experience [0 (None) / 1-2 years / 3-5 years / 6-10 years / 10+ years]: ") or "1-2 years"
    target_role   = input("  Target Role / Dream Job: ") or "Data Scientist"
    resp          = input("  Highest Responsibility [Followed instructions / Planned tasks / Supervised others / Managed outcomes / budgets]: ") or "Planned tasks"
    background    = input("  Career Background (bio): ") or "CS graduate with Python and ML experience. Published a paper on NLP."
    achievements  = input("  Key Achievement or Project: ") or "Built a sentiment analysis API used by 200+ users."

    print("\n  ── Behavioral Scenarios ──")
    print("  A=Wait/Frustrated  B=Search/Follow  C=Analyze/Pivot  D=Collaborate/Align")
    prob_solv     = input("  Problem Solving scenario answer: ") or "Analyze the root cause and propose a fix"
    adapt         = input("  Adaptability scenario answer: ") or "Pivot quickly while documenting the change"

    print("\n  ── Constraints ──")
    budget        = input("  Upskilling Budget [< 50k / 50k-200k / 200k-500k / 500k+]: ") or "50k-200k"
    availability  = input("  Weekly Hours Available [< 5 hours / 5-10 hours / 10-20 hours / 20+ hours]: ") or "10-20 hours"
    industry      = input("  Preferred Industry [FinTech / Healthcare / E-commerce / Sustainability / No preference]: ") or "No preference"

    answers = {
        "career_stage": career_stage, "highest_education": edu,
        "experience_years": exp, "target_role": target_role,
        "responsibility_level": resp, "career_background": background,
        "key_achievements": achievements, "problem_solving": prob_solv,
        "adaptability": adapt, "upskilling_budget": budget,
        "weekly_availability": availability, "preferred_industry": industry
    }

    print("\n  Processing your profile...", end="", flush=True)
    vector = engine.process_comprehensive_assessment(answers)
    bundle = engine.get_recommendations_from_assessment(vector, target_role)
    print(" Done!\n")

    # ══════════════════════════════════════
    #  RESULTS OUTPUT — STARTUP LEVEL
    # ══════════════════════════════════════
    print("\n" + "█"*70)
    print("  PATHFINDER+  ―  YOUR CAREER INTELLIGENCE DASHBOARD")
    print("█"*70)

    # ── CRI Score ──
    cri = bundle.get('readiness_score', {})
    score = cri.get('overall', 0)
    stage = cri.get('stage', 'Development Phase')

    section("1.  CAREER READINESS INDEX  (CRI)")
    print(f"  Overall Score: {score}/100  ─  Stage: {stage}")
    divider()
    sub("Skills Alignment:",    f"{cri.get('skills_match', 0):.1f}%")
    sub("Experience Level:",    f"{cri.get('experience', 0):.1f}%")
    sub("Responsibility Band:", f"{cri.get('responsibility', 0):.1f}%")
    sub("Role Clarity:",        f"{cri.get('clarity', 0):.1f}%")
    sub("Market Intent:",       f"{cri.get('communication', 0):.1f}%")

    # ── Skill Gap ──
    section("2.  SKILL GAP ANALYSIS  (ESCO-Mapped)")
    must_have = bundle.get('compulsory_skills', [])
    good_have = bundle.get('optional_skills', [])
    if must_have:
        print("  CRITICAL (Essential for the role):")
        for s in must_have[:6]: star(s)
    if good_have:
        print("\n  BENEFICIAL (Value-add skills):")
        for s in good_have[:4]: bullet(s)
    if not must_have and not good_have:
        check("No critical skill gaps detected!")

    # ── Career Roadmap ──
    section("3.  CAREER ROADMAP")
    vert = bundle.get('vertical_roadmap', [])
    horiz = bundle.get('horizontal_roadmap', [])

    if vert:
        print("  VERTICAL (Climb the ladder):")
        for step in vert[:2]:
            star(f"{step['role']}  ({step['typical_years']} yrs)")
            print(f"       💡 {step['advice']}")
    if horiz:
        print("\n  HORIZONTAL PIVOTS (Parallel moves):")
        for step in horiz[:2]:
            bullet(f"{step['role']}  (Similarity: {step.get('similarity_score', '—')})")
            print(f"       {step.get('advice', '')}")

    # ── Courses ──
    section("4.  RECOMMENDED LEARNING PATHS")
    recs = bundle.get('recommendations', [])
    acad = bundle.get('academic_recommendations', [])
    seen = set()
    all_recs = recs + acad
    count = 0
    for r in all_recs:
        if r['course_name'] not in seen and count < 5:
            level = r.get('level', 'Professional')
            score_r = r.get('relevance_score', 0)
            print(f"\n  [{count+1}] {r['course_name']}")
            sub("Provider:",     r.get('provider', 'Unknown'))
            sub("Type:",         f"{level} │ Match Score: {score_r:.2f}")
            sub("Cost:",          r.get('fee', 'N/A'))
            sub("Duration:",      r.get('duration', 'Flexible'))
            sub("Why this?",      str(r.get('why_recommended', 'Matched your skill gap'))[:80])
            if r.get('url'): sub("Enroll:", r['url'])
            seen.add(r['course_name'])
            count += 1

    # ── Jobs ──
    section("5.  LIVE JOB MARKET  (Sri Lanka)")
    jobs = bundle.get('job_ideas', [])
    for j in jobs[:3]:
        if 'job_title' not in j: continue
        print(f"\n  ◈  {j['job_title']}")
        sub("Company:",   j.get('company', 'Confidential'))
        sub("Deadline:",  j.get('deadline', 'Apply Soon'))
        skill_gap = j.get('skill_gap_pct', None)
        if skill_gap is not None:
            sub("Your Readiness:",   f"{100-skill_gap:.0f}% match")
        est_sal = j.get('estimated_salary', None)
        if est_sal and isinstance(est_sal, dict):
            sub("Est. Salary:",  f"{est_sal.get('min','?')} – {est_sal.get('max','?')} LKR")
        if j.get('url'): sub("Apply:", j['url'])

    # ── Salary ──
    section("6.  SALARY INTELLIGENCE")
    sal = bundle.get('salary_estimate', {})
    if isinstance(sal, dict) and sal.get('min'):
        sub("Entry Level:",   f"LKR {sal.get('min', '?')} / month")
        sub("Senior Level:",  f"LKR {sal.get('max', '?')} / month")
    else:
        warn("Salary data not available for this specific role — see job listings above.")

    # ── Market Trends ──
    section("7.  MARKET INTELLIGENCE")
    trends = bundle.get('market_trends', {})
    if isinstance(trends, dict):
        field = trends.get('field', 'General')
        hot = trends.get('top_demanded_skills', {})
        segs = trends.get('segments', [])
        rec = trends.get('recommendation', '')

        sub("Trending Field:", field)
        if rec: print(f"\n  Strategic Insight: {rec}")

        if hot:
            print("\n  TOP IN-DEMAND SKILLS:")
            for skill, count in list(hot.items())[:5]:
                bar = "█" * min(int(count / max(hot.values()) * 20), 20)
                print(f"  {skill:<30} {bar} ({count})")

        if segs:
            print("\n  ACTIVE MARKET SEGMENTS:")
            for seg in segs[:3]:
                print(f"\n  ▸ {seg['segment']}  (Demand: {seg['demand']} openings)")
                print(f"    Skills needed: {', '.join(seg['skills'][:5])}")

    # ── Mentors ──
    section("8.  MENTOR RECOMMENDATIONS")
    mentors = bundle.get('mentors', [])
    if mentors:
        for m in mentors[:2]:
            print(f"\n  ◈  {m.get('name', 'Mentor')}")
            sub("Title:",    m.get('title', '—'))
            sub("Company:",  m.get('company', '—'))
            skills_str = ', '.join(m.get('matched_skills', [])[:4])
            sub("Skills:",   skills_str if skills_str else m.get('specialization', 'General'))
    else:
        warn("No exact mentor matches — try broadening your role.")

    # ── Action Plan ──
    section("9.  PERSONALISED ACTION PLAN  (Next 12 Months)")
    action_plan = bundle.get('action_plan', [])
    if not action_plan:
        # Build a minimal default from skill gaps + top course
        if must_have:
            action_plan = [
                {"month": "Month 1-3",  "action": f"Close critical gap: {must_have[0]}"},
                {"month": "Month 3-6",  "action": f"Enroll in: {recs[0]['course_name'] if recs else 'top recommended course'}"},
                {"month": "Month 6-9",  "action": "Apply for relevant internships or entry positions"},
                {"month": "Month 9-12", "action": f"Target role: {target_role} — apply & network"},
            ]
    for step in action_plan[:6]:
        m = step.get('month', step.get('timeline', ''))
        a = step.get('action', step.get('task', ''))
        print(f"  {m:<16} → {a}")

    # ── Alternate Paths ──
    alternate = bundle.get('alternate_paths', [])
    if alternate:
        section("10. ALTERNATIVE CAREER PATHS")
        for path in alternate[:4]:
            bullet(f"{path['title']}  (Similarity: {path['similarity']:.0%})")

    # ── Footer ──
    print("\n" + "█"*70)
    print(f"  PathFinder+  |  AI-powered Career Guidance for Sri Lanka")
    print(f"  Assessment complete — {datetime.now().strftime('%H:%M')}")
    print("█"*70 + "\n")


if __name__ == "__main__":
    run_simulation()
