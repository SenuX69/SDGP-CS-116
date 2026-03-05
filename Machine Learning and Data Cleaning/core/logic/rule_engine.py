"""
core/logic/rule_engine.py — Phase 10 Module
Production Rule Engine with domain clustering, validation, and invariants.
All rules here are the ABSOLUTE AUTHORITY over the output.
"""
from typing import Dict, Any, List, Optional
import re


class RuleEngine:
    """
    Phase 7 & 10: Production Rule Engine (Absolute Authority).
    Enforces domain isolation, qualification floors, and output sanity.
    """

    # Priority order matters: Healthcare/Finance before IT to avoid 'analyst'/'engineer' false matches.
    DOMAIN_CLUSTERS: Dict[str, List[str]] = {
        "Healthcare": [
            "nurse", "nursing", "clinical", "medical", "doctor", "pharmacist",
            "ward", "health", "patient", "hospital", "triage", "medicine",
            "caregiver", "surgeon", "physiotherapy", "dental", "pharmacy",
            "radiology", "lab technician", "paramedic"
        ],
        "Finance": [
            "accounting", "accountant", "banking", "finance", "financial",
            "audit", "auditing", "tax", "investment", "insurance", "banker",
            "treasury", "actuary", "cfa", "acca", "risk management", "credit",
            "budgeting", "ifrs", "variance analysis"
        ],
        "Marketing": [
            "marketing", "seo", "brand", "advertising", "social media",
            "content", "copywriter", "media", "pr", "communications",
            "campaign", "growth hacking", "ecommerce"
        ],
        "IT": [
            "software", "developer", "data", "analyst", "machine learning",
            "vision", "engineer", "web", "backend", "frontend", "devops",
            "cloud", "cyber", "computer", "it", "ict", "programming",
            "network", "database", "systems", "tech", "ai", "artificial intelligence",
            "python", "java", "react", "sql", "aws", "security", "node", "javascript"
        ],
    }

    EDU_LEVELS: Dict[str, int] = {
        "no formal education": 0,
        "intermediate": 1,
        "o/l": 1,
        "a/l": 2,
        "diploma": 3,
        "bachelor's degree": 4,
        "bachelor": 4,
        "bsc": 4,
        "degree": 4,
        "master's / phd": 5,
        "master": 5,
        "msc": 5,
        "mba": 5,
        "phd": 6,
    }

    # Hallucination blacklist — terms that must NEVER appear for non-engineering domains
    HALLUCINATION_BLACKLIST: List[str] = [
        "air traffic", "cad software", "aerospace", "cam software",
        "cae software", "avionics", "flight operations"
    ]

    @staticmethod
    def infer_domain(text: str) -> str:
        """Heuristic-based domain inference for roles or skills."""
        if not text:
            return "General"
        text_lower = str(text).lower()
        for domain, keywords in RuleEngine.DOMAIN_CLUSTERS.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        return "General"

    @staticmethod
    def validate_output_full(
        recommendations: Dict[str, Any],
        assessment_vector: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Master Production Sanity Check.
        Enforces absolute Rule Engine invariants before display.
        Checks: domain isolation for jobs/mentors + hallucination guard.
        """
        user_domain = assessment_vector.get("domain", "General")

        # 1. Clean Jobs — suppress cross-domain noise
        safe_jobs = []
        for j in recommendations.get("jobs", []):
            j_domain = RuleEngine.infer_domain(j.get("job_title", ""))
            if user_domain != "General" and j_domain != "General" and j_domain != user_domain:
                continue
            safe_jobs.append(j)
        recommendations["jobs"] = safe_jobs

        # 2. Clean Mentors — strict domain match
        safe_mentors = []
        for m in recommendations.get("mentors", []):
            m_domain = m.get("domain", RuleEngine.infer_domain(m.get("title", "")))
            if user_domain != "General" and m_domain != "General" and m_domain != user_domain:
                continue
            safe_mentors.append(m)
        recommendations["mentors"] = safe_mentors

        # 3. Hallucination Guard — strip blacklisted skills
        if user_domain not in ["IT", "Engineering"]:
            recommendations["skill_gap"] = [
                s for s in recommendations.get("skill_gap", [])
                if not any(b in str(s).lower() for b in RuleEngine.HALLUCINATION_BLACKLIST)
            ]

        return recommendations

    @staticmethod
    def get_edu_level(edu_str: str) -> int:
        """Returns numeric education level for a given string."""
        edu_lower = str(edu_str).lower()
        for key, val in RuleEngine.EDU_LEVELS.items():
            if key in edu_lower:
                return val
        return 0

    @staticmethod
    def is_qualification_floor_violation(course_level_str: str, user_edu_level: int) -> bool:
        """
        Returns True if the recommended course is BELOW the user's qualification.
        Professional certifications / short courses are exempt from this rule.
        """
        course_lower = str(course_level_str).lower()
        # Professional certs are always allowed
        if any(k in course_lower for k in ["professional", "certification", "certificate", "short"]):
            return False

        course_val = 1
        if "diploma" in course_lower:
            course_val = 3
        elif "bachelor" in course_lower or "degree" in course_lower or "bsc" in course_lower:
            course_val = 4
        elif "master" in course_lower or "postgraduate" in course_lower or "msc" in course_lower:
            course_val = 5

        return course_val < user_edu_level
