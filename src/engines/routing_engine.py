"""
Routing Engine.
Routes feedback to appropriate departments based on aspects and severity.
"""

from typing import Any, Dict, List


class RoutingEngine:
    """Route feedback to appropriate departments."""
    
    # Routing rules based on aspects
    ASPECT_ROUTING = {
        "wait_time": "OPD Operations",
        "politeness": "Front Desk",
        "doctor_explanation": "Medical Services",
        "billing": "Billing Department",
        "cleanliness": "Housekeeping",
        "nursing_care": "Nursing Supervisor",
        "diagnostics": "Diagnostics Department",
        "discharge_process": "Medical Services",
        "lab_services": "Diagnostics Department"
    }
    
    # Escalation rules based on severity
    ESCALATION_SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM"]
    ESCALATION_DEPARTMENT = "Management"
    
    def __init__(self):
        """Initialize the RoutingEngine."""
        pass
    
    def route(
        self,
        aspects: List[str],
        severity: str,
        service_line: str = None,
        staff_category: str = None,
        overall_sentiment: str = None,
        clause_analysis: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Route feedback to appropriate department.
        """

        # ===== Escalation Rules =====
        requires_escalation = severity in self.ESCALATION_SEVERITY_LEVELS

        if severity == "CRITICAL":
            return {
                "routing_department": "Patient Safety Office",
                "requires_escalation": True,
                "escalation_reason": "Critical patient safety issue",
                "primary_aspect": aspects[0] if aspects else None,
                "all_aspects": aspects
            }

        if severity == "HIGH":
            return {
                "routing_department": "Patient Safety Office",
                "requires_escalation": True,
                "escalation_reason": "High severity patient safety concern",
                "primary_aspect": aspects[0] if aspects else None,
                "all_aspects": aspects
            }

        # ===== Clause-Based Routing (Preferred) =====
        if clause_analysis:

            negative_clauses = [
                c for c in clause_analysis
                if c.get("overall_sentiment") == "negative"
            ]

            negative_aspects = []

            for clause in negative_clauses:
                negative_aspects.extend(
                    clause.get("aspects", [])
                )

            negative_aspects = list(dict.fromkeys(negative_aspects))

            if negative_aspects:
                primary_aspect = negative_aspects[0]
            elif aspects:
                primary_aspect = aspects[0]
            else:
                primary_aspect = None

        else:
            primary_aspect = aspects[0] if aspects else None

        # ===== Aspect Routing =====
        if primary_aspect:
            department = self.ASPECT_ROUTING.get(
                primary_aspect,
                "Patient Relations"
            )
        else:
            department = "Patient Relations"

        # ===== Staff Overrides =====
        if staff_category in ["nurse", "nursing_staff"]:
            department = "Nursing Supervisor"

        elif staff_category == "doctor":
            department = "Medical Services"

        elif staff_category in ["lab_technician", "diagnostics_staff"]:
            department = "Diagnostics Department"

        elif staff_category in ["receptionist", "reception_staff"]:
            department = "Front Desk"

        elif staff_category == "billing_staff":
            department = "Billing Department"

        if department == "Patient Relations" and service_line:
            department = f"{service_line} Operations"

        # Final return (outside the if/elif chain)
        return {
            "routing_department": department,
            "requires_escalation": requires_escalation,
            "escalation_reason": (
                "Medium severity operational issue"
                if severity == "MEDIUM"
                else None
            ),
            "primary_aspect": primary_aspect,
            "all_aspects": aspects
        }
