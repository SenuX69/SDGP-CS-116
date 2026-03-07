from typing import Dict, Any, List, Optional
import math

class ActionPlanGenerator:
    """
    Phase 3 & 10: Dynamic Action Plan Generator.
    Adapts duration and milestones based on user experience, gap count, and pace.
    """

    @staticmethod
    def generate_action_plan(gap_skills: List[str], target_role: str = "your target role",
                              assessment_vector: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates a DYNAMIC, high-precision action plan using the V2 Formula:
        Transition Time = (Sum of Skill Times) / (Availability / Baseline) * Exp Factor * Stage Multiplier
        """
        if not gap_skills:
            return {
                "steps": [{
                    "period":    "Ongoing",
                    "focus":    f"You are already well-positioned for {target_role}. Focus on networking, portfolio building, and staying current with industry trends.",
                    "milestone": "Maintain and grow your lead"
                }],
                "estimated_months": 0,
                "estimated_weeks": 0,
                "estimated_completion": "Ready now"
            }

        # 1. Base Skill Weights (Weeks)
        # Advanced (16), Intermediate (8), Basic (5)
        ADVANCED_KWS = ["machine learning", "distributed system", "blockchain", "cybersecurity", "architecture", "deep learning", "nlp", "devops", "cloud", "aws", "azure", "docker", "kubernetes"]
        INTER_KWS = ["api", "database", "visualization", "react", "node", "statistics", "analytics", "backend", "frontend", "sql", "git", "rest", "graphql"]

        sum_skill_weeks = 0
        for s in gap_skills:
            s_lower = str(s).lower()
            if any(kw in s_lower for kw in ADVANCED_KWS):
                sum_skill_weeks += 16
            elif any(kw in s_lower for kw in INTER_KWS):
                sum_skill_weeks += 8
            else:
                sum_skill_weeks += 5

        # 2. Availability Adjustment (Baseline 10 hours)
        time_str = str(assessment_vector.get("time_commitment", "10-20 hours")).lower() if assessment_vector else "10-20 hours"
        availability_hours = 10
        if "20+" in time_str or "full" in time_str: availability_hours = 25
        elif "10-20" in time_str: availability_hours = 15
        elif "5-10" in time_str: availability_hours = 8
        else: availability_hours = 5
        
        pace_factor = availability_hours / 10.0 # Speed multiplier (e.g. 1.5x)

        # 3. Experience Factor (Transferable Skills)
        exp_years = float(assessment_vector.get("experience_years", 0)) if assessment_vector else 0
        exp_factor = 1.0
        if exp_years >= 10: exp_factor = 0.7
        elif exp_years >= 6: exp_factor = 0.8
        elif exp_years >= 3: exp_factor = 0.9

        # 4. Career Stage Multiplier
        status = int(assessment_vector.get("status_level", 1)) if assessment_vector else 1
        # Multipliers: Student (1.2), Switcher (1.0), Professional (0.8)
        stage_multiplier = 1.0
        if status <= 1: stage_multiplier = 1.2
        elif status == 2: stage_multiplier = 0.8
        elif status == 3: stage_multiplier = 1.0

        # FINAL FORMULA
        total_weeks = (sum_skill_weeks / pace_factor) * exp_factor * stage_multiplier
        total_months = max(2, round(total_weeks / 4.33))
        
        # 5. Milestone Generation
        def phase_label(month_start: int, month_end: int) -> str:
            if month_end <= 1: return f"Month 1"
            elif month_end - month_start <= 1: return f"Month {month_start}"
            else: return f"Months {month_start}-{month_end}"

        plan = []
        seg1 = max(1, round(total_months * 0.30))
        seg2 = max(seg1 + 1, round(total_months * 0.55))
        seg3 = max(seg2 + 1, round(total_months * 0.80))
        seg4 = total_months

        plan.append({
            "period": phase_label(1, seg1),
            "focus": f"Foundations: Develop core skills like {', '.join(gap_skills[:2])}",
            "milestone": "Completed foundational upskilling"
        })
        plan.append({
            "period": phase_label(seg1 + 1, seg2),
            "focus": f"Portfolio building for {target_role}: Apply skills to 3+ practical projects",
            "milestone": "Portfolio ready for review"
        })
        plan.append({
            "period": phase_label(seg2 + 1, seg3),
            "focus": f"Transition Support: Connect with mentors and update industry visibility",
            "milestone": "LinkedIn updated and 5+ informational interviews"
        })
        plan.append({
            "period": phase_label(seg3 + 1, seg4),
            "focus": f"Placement: Active application and interview prep for {target_role} roles",
            "milestone": "Role secured or transition completed"
        })

        est_label = f"~{total_months} months at your current pace ({availability_hours}h/week)"
        
        return {
            "steps": plan,
            "estimated_months": total_months,
            "estimated_weeks": int(total_weeks),
            "estimated_completion": est_label
        }
