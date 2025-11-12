"""
seraa/axioms/constraint.py - Axiom 6: Ethical Constraint (Exclusion Principle)

Supports both critical ("hard") and soft constraints with priorities and weights.
Resolves conflicts using thresholded scoring after checking critical violations.
Like the Pauli exclusion principle, certain ethical states cannot coexist.
"""

from typing import Dict, List, Callable, Any, Optional
from ..core.ternary import TernaryValue, TernaryState

CRITICAL_THRESHOLD = 90     # Priority above this is "critical"/hard
ACCEPTANCE_THRESHOLD = 1.0  # Soft score required for passing (customizable)

class EthicalConstraint:
    """
    Represents an ethical constraint, either critical (hard) or soft.
    Supports priorities and weights for pluralistic, nuanced evaluation.
    """
    def __init__(
        self,
        name: str,
        checker: Callable[[Any], bool],
        violation_message: str = "Constraint violated",
        priority: int = 50,   # 0-100, >CRITICAL_THRESHOLD = critical
        weight: float = 1.0,  # Used in scoring if soft
        penalty: float = 1.0  # Penalty on violation if soft
    ):
        self.name = name
        self.checker = checker
        self.violation_message = violation_message
        self.priority = priority
        self.weight = weight
        self.penalty = penalty

    def evaluate(self, action: Any) -> 'ConstraintResult':
        """
        Evaluate if action satisfies constraint.
        Returns a ConstraintResult with satisfaction and ternary state.
        """
        satisfied = self.checker(action)
        state = TernaryValue(TernaryState.NEUTRAL if satisfied else TernaryState.NEGATIVE)
        return ConstraintResult(
            constraint=self,
            satisfied=satisfied,
            state=state,
            message=self.violation_message if not satisfied else "Constraint satisfied"
        )

class ConstraintResult:
    """Result of constraint evaluation for a specific action."""
    def __init__(
        self,
        constraint: EthicalConstraint,
        satisfied: bool,
        state: TernaryValue,
        message: str
    ):
        self.constraint = constraint
        self.satisfied = satisfied
        self.state = state
        self.message = message

    def is_violated(self) -> bool:
        """Returns True if constraint was violated."""
        return not self.satisfied

    def __repr__(self):
        status = "✓ Satisfied" if self.satisfied else "✗ Violated"
        return f"ConstraintResult({self.constraint.name}: {status})"

class ConstraintSystem:
    """
    Manages and evaluates multiple ethical constraints.
    Supports conflict resolution with weighted scoring and critical checks.
    """
    def __init__(self):
        self.constraints: List[EthicalConstraint] = []

    def add_constraint(self, constraint: EthicalConstraint) -> None:
        self.constraints.append(constraint)

    def evaluate_all(self, action: Any) -> List[ConstraintResult]:
        """Evaluate action against all constraints."""
        return [constraint.evaluate(action) for constraint in self.constraints]

    def all_satisfied(self, results: Optional[List[ConstraintResult]] = None, action: Any = None) -> bool:
        """Check if all constraints are satisfied."""
        if results is None:
            if action is None:
                raise ValueError("Must provide either results or action")
            results = self.evaluate_all(action)
        return all(result.satisfied for result in results)

    def get_violations(self, action: Any) -> List[ConstraintResult]:
        """Return list of violations for a given action."""
        return [r for r in self.evaluate_all(action) if r.is_violated()]

    def resolve_conflicts(self, action: Any) -> (bool, str):
        """
        Resolve constraint conflicts:
        - Block immediately on critical constraint violation
        - Otherwise, sum weights/penalties for soft constraints 
        - Pass only if weighted score reaches threshold.
        Returns: (bool pass/fail, explanation string)
        """
        results = self.evaluate_all(action)
        critical = [r for r in results if r.constraint.priority > CRITICAL_THRESHOLD and r.is_violated()]
        if critical:
            return False, f"Critical constraint(s) violated: {', '.join([r.constraint.name for r in critical])}"
        # Weighted scoring for soft constraints
        soft_score = sum(
            r.constraint.weight if not r.is_violated() else -r.constraint.penalty
            for r in results if r.constraint.priority <= CRITICAL_THRESHOLD
        )
        if soft_score >= ACCEPTANCE_THRESHOLD:
            return True, f"Action accepted (score: {soft_score})"
        else:
            violated_names = [r.constraint.name for r in results if r.constraint.priority <= CRITICAL_THRESHOLD and r.is_violated()]
            return False, f"Soft constraint justification insufficient (score: {soft_score}). Violated: {violated_names}"

def create_threshold_constraint(
    name: str,
    attribute: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    priority: int = 50,
    weight: float = 1.0,
    penalty: float = 1.0
) -> EthicalConstraint:
    """
    Template for attribute-based constraints.
    Checks if the attribute in an action is within specified bounds.
    """
    def checker(action):
        value = action.get(attribute, 0)
        if min_value is not None and value < min_value:
            return False
        if max_value is not None and value > max_value:
            return False
        return True

    return EthicalConstraint(
        name=name,
        checker=checker,
        violation_message=f"{attribute} outside acceptable range",
        priority=priority,
        weight=weight,
        penalty=penalty
    )
