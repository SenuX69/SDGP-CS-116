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
        """Generates a DYNAMIC, person-specific action plan."""
        if not gap_skills:
            return {
                "steps": [{
                    "period":    "Ongoing",
                    "action":    f"You are already well-positioned for {target_role}. Focus on networking, portfolio building, and staying current with industry trends.",
                    "milestone": "Maintain and grow your lead"
                }],
                "estimated_months": 0,
                "estimated_weeks": 0,
                "estimated_completion": "Ready now"
            }

        # 1. Read user context
        exp_years = float(assessment_vector.get("experience_years", 0)) if assessment_vector else 0
        status = int(assessment_vector.get("status_level", 1)) if assessment_vector else 1
        time_str = str(assessment_vector.get("time_commitment", "10-20 hours")).lower() if assessment_vector else "10-20 hours"

        # Hours per week learning pace
        if "20+" in time_str or "full" in time_str: pace = 1.0
        elif "10-20" in time_str: pace = 1.5
        elif "5-10" in time_str: pace = 2.0
        else: pace = 2.5

        weeks_per_gap = 3.0 * pace
        total_weeks = int(len(gap_skills) * weeks_per_gap) + int(8 * pace)
        total_months = max(2, round(total_weeks / 4.33))

        # Career stage helpers
        is_entry = status <= 1 or exp_years == 0
        is_switcher = status == 3
        is_senior = exp_years >= 5

        def phase_label(month_start: int, month_end: int) -> str:
            if month_end <= 1: return f"Weeks 1-{int(month_end * 4)}"
            elif month_end - month_start <= 1: return f"Month {month_start}"
            else: return f"Months {month_start}-{month_end}"

        plan = []
        seg1 = max(1, round(total_months * 0.30))
        seg2 = max(seg1 + 1, round(total_months * 0.55))
        seg3 = max(seg2 + 1, round(total_months * 0.80))
        seg4 = total_months

        # Phase 1: Foundation
        plan.append({
            "period": phase_label(1, seg1),
            "action": f"Develop core skills: {', '.join(gap_skills[:2])}",
            "milestone": "Complete foundational upskilling" if is_entry else "Identify and close strategic gaps"
        })

        # Phase 2: Build
        plan.append({
            "period": phase_label(seg1 + 1, seg2),
            "action": f"Apply skills to practical projects for {target_role}",
            "milestone": "3+ portfolio projects completed" if not is_senior else "Lead a pilot project in your current role"
        })

        # Phase 3: Transition
        plan.append({
            "period": phase_label(seg2 + 1, seg3),
            "action": f"Seek mentorship and build network in {target_role} domain",
            "milestone": "LinkedIn updated and 5+ informational interviews"
        })

        # Phase 4: Placement
        plan.append({
            "period": phase_label(seg3 + 1, seg4),
            "action": f"Resume overhaul and active application for {target_role} roles",
            "milestone": "Role secured or transition completed"
        })

        est_label = f"~{total_months} months at your current pace"
        
        return {
            "steps": plan,
            "estimated_months": total_months,
            "estimated_weeks": total_weeks,
            "estimated_completion": est_label
        }
