"""
core/logic/analytics.py — Phase 10 Module
Career Readiness Index (CRI) + Local Demand Scoring.
All logic delegated here from the main orchestrator.
"""
import json
import pandas as pd
import numpy as np
import re  # needed for pattern in calculate_local_demand_score
from typing import Dict, Any, List, Optional
from .rule_engine import RuleEngine


class Analytics:
    """
    Phase 7 & 10: Scoring and Market Analytics.
    Handles CRI, Local Demand, and Skill Alignment.
    """

    @staticmethod
    def calculate_local_demand_score(
        domain: str,
        jobs_df: pd.DataFrame,
        salary_mapping: Dict[str, Any],
        rule_engine: "RuleEngine"
    ) -> float:
        """
        Computes demand score (0.0 – 1.0) using ONLY Sri Lanka datasets.
        Score = 0.6 * normalised_job_count + 0.4 * normalised_avg_salary.
        """
        # Accept either a domain key or a free-text role → infer
        actual_domain = (
            domain
            if domain in RuleEngine.DOMAIN_CLUSTERS
            else RuleEngine.infer_domain(domain)
        )

        if actual_domain == "General" or jobs_df is None or jobs_df.empty:
            return 0.35  # Conservative baseline

        # 1. Job Count Score
        domain_keywords = RuleEngine.DOMAIN_CLUSTERS.get(actual_domain, [])
        pattern = "|".join(re.escape(kw) for kw in domain_keywords)
        domain_jobs = jobs_df[jobs_df["title"].str.lower().str.contains(pattern, na=False, regex=True)]
        job_count_norm = min(len(domain_jobs) / 500, 1.0)

        # 2. Salary Score
        salary_sum = 0
        salary_count = 0
        for role, data in salary_mapping.get("roles", {}).items():
            if RuleEngine.infer_domain(role) == actual_domain:
                avg_val = data.get("avg", (data.get("min", 0) + data.get("max", 0)) / 2)
                salary_sum += avg_val
                salary_count += 1

        avg_salary = salary_sum / salary_count if salary_count > 0 else 100_000
        salary_norm = min(max(avg_salary - 50_000, 0) / 450_000, 1.0)

        demand_score = (0.6 * job_count_norm) + (0.4 * salary_norm)
        return round(float(demand_score), 2)

    @staticmethod
    def calculate_readiness_score(
        user_skills: List[str],
        assessment_vector: Dict[str, Any],
        target_role: str,
        jobs_df: pd.DataFrame,
        salary_mapping: Dict[str, Any],
        rule_engine: "RuleEngine",
        show_progress: bool = False
    ) -> Dict[str, Any]:
        """
        Phase 7 Production CRI (Lock-in).
        Weights:
          - Skills Alignment:  35%  (domain-filtered, floor 15–25%)
          - Experience Level:  25%  (tiered interpolation)
          - Local Demand:      20%  (Sri Lanka only)
          - Qualification:     10%  (level match)
          - Skill Gap Cover:   10%  (band proxy)
        """
        import re as _re

        domain = assessment_vector.get("domain", RuleEngine.infer_domain(target_role))

        # ── 1. Skills Match (35%) ─────────────────────────────────────
        user_skills_set = set(str(s).lower() for s in user_skills)
        # We pull required skills from domain keywords as a proxy
        domain_kws = set(RuleEngine.DOMAIN_CLUSTERS.get(domain, []))
        overlap = user_skills_set & domain_kws
        raw_skill_pct = len(overlap) / len(domain_kws) if domain_kws else 0.5
        skill_alignment = max(raw_skill_pct, 0.15)  # Production floor
        status_level = assessment_vector.get("status_level", 1)
        if status_level <= 1:
            skill_alignment = max(skill_alignment, 0.25)  # Graduate boost

        # ── 2. Experience (25%) ───────────────────────────────────────
        exp_years = float(assessment_vector.get("experience_years", 0))
        _bp = [(0, 0.0), (1.5, 0.30), (4.0, 0.60), (8.0, 0.85), (12.0, 1.0)]
        exp_pct = 1.0
        for i in range(len(_bp) - 1):
            lo_x, lo_y = _bp[i]; hi_x, hi_y = _bp[i + 1]
            if lo_x <= exp_years <= hi_x:
                t = (exp_years - lo_x) / (hi_x - lo_x) if (hi_x - lo_x) > 0 else 0
                exp_pct = lo_y + t * (hi_y - lo_y)
                break

        # ── 3. Local Demand (20%)
        demand_score = Analytics.calculate_local_demand_score(domain, jobs_df, salary_mapping, rule_engine)

        # ── 4. Qualification Match (10%) 
        user_edu_lvl = assessment_vector.get("education_level", 1)
        target_edu_lvl = 4 if domain in ["IT", "Finance"] else 3
        qual_pct = min(user_edu_lvl / target_edu_lvl, 1.0)

        # ── 5. Skill Gap Coverage (10%) 
        gap_cov_pct = assessment_vector.get("responsibility_band", 0) / 4.0

        score = (skill_alignment * 35) + (exp_pct * 25) + (demand_score * 20) + (qual_pct * 10) + (gap_cov_pct * 10)

        logs = {
            "domain_detected": domain,
            "demand_score": demand_score,
            "skill_alignment_before_floor": round(raw_skill_pct * 100, 1),
            "skill_alignment_after_floor": round(skill_alignment * 100, 1),
            "rule_overrides_triggered": ["AlignmentFloor"] if skill_alignment > raw_skill_pct else [],
        }
        if show_progress:
            print(f"DEBUG RuleEngine: {json.dumps(logs)}")

        stage = "Market Ready" if score > 70 else "Development Phase"
        return {
            "overall":       round(score, 1),
            "skills_match":  round(skill_alignment * 100, 1),
            "experience":    round(exp_pct * 100, 1),
            "demand_score":  round(demand_score * 100, 1),
            "qualification": round(qual_pct * 100, 1),
            "gap_coverage":  round(gap_cov_pct * 100, 1),
            "stage":         stage,
            "logs":          logs,
        }
