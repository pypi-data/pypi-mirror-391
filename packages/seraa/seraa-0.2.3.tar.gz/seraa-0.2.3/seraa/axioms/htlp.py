"""
seraa/axioms/htlp.py - Axiom 7: Human-in-the-Loop Protocol (HTLP)

Ensures human governance, oversight, and intervention at critical junctures.
"""

from typing import Any, Callable, Optional

class HumanInTheLoop:
    """
    Represents a process or decision point requiring human review or approval.
    
    Example:
        >>> def notify_user(action, reason):
        ...     print(f"User notified for: {action} Reason: {reason}")
        ...
        >>> htlp = HumanInTheLoop(
        ...     intervention_callback=notify_user,
        ...     review_message="Flagged for human oversight"
        ... )
        >>> htlp.escalate({'action': 'data_sharing'}, "Unusual consent status")
    """
    def __init__(
        self,
        intervention_callback: Optional[Callable[[Any, str], None]] = None,
        review_message: str = "Action requires human review"
    ):
        """
        Args:
            intervention_callback: Called when human intervention is triggered
            review_message: Explanation for review
        """
        self.intervention_callback = intervention_callback
        self.review_message = review_message

    def escalate(self, action: Any, reason: str = "") -> None:
        """
        Escalate to human review.
        
        Args:
            action: The action or event being escalated
            reason: Specific reason for escalation
        """
        message = f"{self.review_message}"
        if reason:
            message += f": {reason}"
        if self.intervention_callback:
            self.intervention_callback(action, message)
        else:
            # Default: print to console (can be replaced)
            print(f"[HTLP] Escalation - Action: {action} | Reason: {message}")

    def is_review_required(self, flagged: bool) -> bool:
        """Check if an action requires human review."""
        return flagged

