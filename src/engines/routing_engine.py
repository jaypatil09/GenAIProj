"""
Routing Engine.
Routes feedback to appropriate departments based on aspects and severity.
"""

from typing import List, Dict


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
    ESCALATION_SEVERITY_LEVELS = ["CRITICAL", "HIGH"]
    ESCALATION_DEPARTMENT = "Management"
    
    def __init__(self):
        """Initialize the RoutingEngine."""
        pass
    
    def route(
        self,
        aspects: List[str],
        severity: str,
        service_line: str = None
    ) -> Dict[str, any]:
        """
        Route feedback to appropriate department.
        
        Args:
            aspects: List of detected aspects
            severity: Severity level
            service_line: Service line (optional)
            
        Returns:
            Dictionary with routing information
        """
        # Check if escalation needed
        requires_escalation = severity in self.ESCALATION_SEVERITY_LEVELS
        
        if requires_escalation:
            department = self.ESCALATION_DEPARTMENT
            escalation_reason = f"{severity} severity complaint"
        else:
            # Route based on primary aspect
            if aspects:
                primary_aspect = aspects[0]
                department = self.ASPECT_ROUTING.get(primary_aspect, "OPD Operations")
            else:
                department = "OPD Operations"
            escalation_reason = None
        
        return {
            "routing_department": department,
            "requires_escalation": requires_escalation,
            "escalation_reason": escalation_reason,
            "primary_aspect": aspects[0] if aspects else None,
            "all_aspects": aspects
        }
    
    def route_batch(
        self,
        aspects_list: List[List[str]],
        severities: List[str],
        service_lines: List[str] = None
    ) -> List[Dict]:
        """
        Route multiple feedbacks.
        
        Args:
            aspects_list: List of aspect lists
            severities: List of severity levels
            service_lines: List of service lines (optional)
            
        Returns:
            List of routing dictionaries
        """
        if service_lines is None:
            service_lines = [None] * len(aspects_list)
        
        return [
            self.route(aspects, severity, service_line)
            for aspects, severity, service_line in zip(aspects_list, severities, service_lines)
        ]
    
    def get_routing_rules(self) -> Dict[str, str]:
        """Get all routing rules."""
        return self.ASPECT_ROUTING.copy()
    
    def get_department_for_aspect(self, aspect: str) -> str:
        """
        Get department for a specific aspect.
        
        Args:
            aspect: Aspect name
            
        Returns:
            Department name
        """
        return self.ASPECT_ROUTING.get(aspect, "OPD Operations")
    
    def get_all_departments(self) -> List[str]:
        """Get list of all departments."""
        departments = set(self.ASPECT_ROUTING.values())
        departments.add(self.ESCALATION_DEPARTMENT)
        return sorted(list(departments))
