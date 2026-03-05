"""
core/logic/recommenders.py — Phase 10 Module
Modular Course, Job and Mentor recommendation logic.
Operates on data from the main engine context.
"""
from typing import Dict, Any, List, Optional
from .rule_engine import RuleEngine
from .analytics import Analytics
from .action_plan import ActionPlanGenerator


class Recommender:
    """
    Phase 7 & 10: Core Recommendation Logic.
    Separates Course, Job, and Mentor matching into testable, auditable modules.
    """

    def __init__(self, engine_context: Any):
        self.ctx = engine_context  # RecommendationEngine instance (data only)
        self.rule_engine = RuleEngine()
        self.analytics = Analytics()
        self.action_plan_gen = ActionPlanGenerator()

    #  Mentor Matching 

    def match_mentors_full(
        self,
        user_skills: List[str],
        target_job: str,
        mentors_data: List[Dict],
        top_n: int = 3,
        assessment_vector: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Production Mentor Matcher.
        Invariant: mentor domain must match user domain (domain isolation).
        Scoring: skill overlap (2pts each) + role match bonus (10pts) + company bonus (5pts).
        """
        if not mentors_data:
            return []

        user_domain = (
            assessment_vector.get("domain", RuleEngine.infer_domain(target_job))
            if assessment_vector
            else RuleEngine.infer_domain(target_job)
        )
        target_role_lower = str(target_job).lower()
        user_skill_set = set(s.lower() for s in user_skills)
        scored_mentors = []

        for mentor in mentors_data:
            current_role = str(mentor.get("current_role", mentor.get("title", ""))).lower()
            mentor_domain = mentor.get("domain", RuleEngine.infer_domain(current_role))

            # Absolute Invariant: Domain Isolation
            if user_domain != "General" and mentor_domain != "General" and mentor_domain != user_domain:
                continue

            mentor_skills = [str(s).lower() for s in mentor.get("skills", [])]
            overlap = list(user_skill_set & set(mentor_skills))

            score = len(overlap) * 2

            # Role relevance boost
            if target_role_lower in current_role or current_role in target_role_lower:
                score += 10

            # Company credibility boost
            if mentor.get("company") and str(mentor.get("company")).strip() not in ("", "N/A", "nan"):
                score += 5

            # Always show matched_skills — use role label as fallback
            matched_skills_display = (
                [s.title() for s in overlap[:3]]
                if overlap
                else [f"Role match: {mentor.get('current_role', 'Professional')}"]
            )

            scored_mentors.append({
                "name":           mentor.get("name"),
                "title":          mentor.get("current_role", mentor.get("title")) or "Professional Mentor",
                "company":        mentor.get("company", "Independent"),
                "score":          score,
                "domain":         mentor_domain,
                "matched_skills": matched_skills_display,
            })

        scored_mentors.sort(key=lambda x: x["score"], reverse=True)
        return scored_mentors[:top_n]

    # ── Job Recommendations 

    def recommend_jobs_domain_filtered(
        self,
        user_skills: List[str],
        target_job: str,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Domain-first job recommendations backed by the local jobs database.
        """
        import pandas as pd
        user_domain = RuleEngine.infer_domain(target_job)
        jobs_df = self.ctx.jobs_df

        if jobs_df is None or jobs_df.empty:
            return []

        domain_keywords = RuleEngine.DOMAIN_CLUSTERS.get(user_domain, [])
        if not domain_keywords:
            return []

        import re
        pattern = "|".join(re.escape(kw) for kw in domain_keywords)
        domain_jobs = jobs_df[jobs_df["title"].str.lower().str.contains(pattern, na=False, regex=True)]

        results = []
        for _, row in domain_jobs.head(top_n).iterrows():
            results.append({
                "job_title":  row.get("title", "Unknown Role"),
                "company":    row.get("company", "Sri Lanka Market"),
                "location":   row.get("location", "Remote/Colombo"),
                "url":        row.get("url", row.get("job_url", "#")),
                "deadline":   row.get("deadline", "Apply Soon"),
            })
        return results
