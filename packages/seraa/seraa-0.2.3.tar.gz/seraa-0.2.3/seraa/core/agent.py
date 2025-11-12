"""
seraa/core/agent.py - Unified SERAA Agent

Integrates all 9 axioms into a cohesive ethical reasoning system.
"""

from typing import Any, Dict, List, Optional, Callable
from ..axioms import (
    MoralSuperposition,
    EthicalMeasurement,
    EthicalEntanglement,
    EthicalUncertainty,
    EthicalResonance,
    ConstraintSystem,
    EthicalConstraint,
    HumanInTheLoop,
    FoundationalKnowledge,
    evaluate_choice_preservation,
)
from .monitor import SubconsciousMonitor, ConsciousLayer
from .ternary import TernaryValue, TernaryState


class SeraaAgent:
    """
    Unified SERAA agent that integrates all 9 axioms.
    
    Example:
        >>> agent = SeraaAgent(
        ...     name="healthcare_ai",
        ...     moral_weights={'autonomy': 0.4, 'care': 0.3, 'justice': 0.3},
        ...     core_values={'human_dignity': 1.0, 'do_no_harm': 1.0}
        ... )
        >>> result = agent.evaluate_action(some_action)
        >>> if result.approved:
        ...     print("Action ethically approved")
    """
    
    def __init__(
        self,
        name: str,
        moral_weights: Dict[str, float],
        core_values: Dict[str, float],
        community_state: Optional[Dict[str, float]] = None,
        pac_threshold: float = 0.7,
        uncertainty_threshold: float = 0.5,
        resonance_threshold: float = 0.7
    ):
        """
        Initialize SERAA agent with all axioms.
        
        Args:
            name: Agent identifier
            moral_weights: Initial moral superposition weights
            core_values: Immutable foundational knowledge
            community_state: Community moral state for resonance (optional)
            pac_threshold: Minimum PAC score
            uncertainty_threshold: Maximum acceptable uncertainty
            resonance_threshold: Minimum community alignment
        """
        self.name = name
        self.pac_threshold = pac_threshold
        self.uncertainty_threshold = uncertainty_threshold
        self.resonance_threshold = resonance_threshold
        
        # Axiom 8: Foundational Knowledge
        self.foundation = FoundationalKnowledge(core_values)
        self.foundation.freeze()
        
        # Axiom 1: Moral Superposition
        self.moral_state = MoralSuperposition(moral_weights)
        
        # Axiom 3: Community (if provided)
        self.community_state = community_state
        
        # Axiom 6: Constraint System
        self.constraints = ConstraintSystem()
        
        # Axiom 7: Human-in-the-Loop
        self.htlp = HumanInTheLoop()
        
        # Monitoring
        self.conscious = ConsciousLayer(max_attention_items=5)
        self._setup_monitors()
    
    def _setup_monitors(self):
        """Set up subconscious monitoring."""
        # Monitor PAC scores
        pac_monitor = SubconsciousMonitor(
            name="pac_monitor",
            optimal_checker=lambda x: x.get('pac_score', 0) >= self.pac_threshold
        )
        self.conscious.add_monitor(pac_monitor)
    
    def add_constraint(self, constraint: EthicalConstraint) -> None:
        """Add an ethical constraint to the system."""
        self.constraints.add_constraint(constraint)
    
    def set_htlp_callback(self, callback: Callable[[Any, str], None]) -> None:
        """Set callback for human escalation."""
        self.htlp.intervention_callback = callback
    
    def evaluate_action(
        self,
        action: Any,
        action_set: Optional[List[Any]] = None,
        pac_evaluator: Optional[Callable[[Any], float]] = None,
        viability_checker: Optional[Callable[[Any], bool]] = None
    ) -> 'EthicalEvaluationResult':
        """
        Evaluate an action through all SERAA axioms.
        
        Args:
            action: The action to evaluate
            action_set: Full set of available actions (for choice preservation)
            pac_evaluator: Function to evaluate PAC score
            viability_checker: Function to check viability
            
        Returns:
            EthicalEvaluationResult with comprehensive evaluation
        """
        result = EthicalEvaluationResult(action=action)
        
        # === Axiom 6: Check Constraints ===
        constraint_results = self.constraints.evaluate_all(action)
        result.constraints_satisfied = self.constraints.all_satisfied(results=constraint_results)
        result.constraint_violations = [r for r in constraint_results if not r.satisfied]
        
        # === Axiom 4: Calculate Uncertainty ===
        if hasattr(action, 'predicted_outcomes') or isinstance(action, dict) and 'predicted_outcomes' in action:
            outcomes = action.get('predicted_outcomes', []) if isinstance(action, dict) else action.predicted_outcomes
            uncertainty = EthicalUncertainty(self.moral_state.weights, outcomes)
            result.uncertainty = uncertainty.calculate()
            result.uncertainty_acceptable = not uncertainty.exceeds_threshold(self.uncertainty_threshold)
        else:
            result.uncertainty_acceptable = True
        
        # === Axiom 5: Check Resonance (if community exists) ===
        if self.community_state:
            resonance = EthicalResonance(
                self.moral_state.weights,
                self.community_state,
                self.resonance_threshold
            )
            result.resonance_score = resonance.calculate_alignment()
            result.is_resonant = resonance.is_resonant()
        else:
            result.is_resonant = True
        
        # === Axiom 9: Check Choice Preservation ===
        if action_set and pac_evaluator and viability_checker:
            choice_result = evaluate_choice_preservation(
                moral_state=self.moral_state.weights,
                actions=action_set,
                pac_evaluator=pac_evaluator,
                viability_checker=viability_checker,
                pac_threshold=self.pac_threshold
            )
            result.choice_preserved = choice_result.choice_preserved
            result.choice_details = choice_result
        else:
            # Default check using action's pac_score if available
            pac_score = action.get('pac_score', 1.0) if isinstance(action, dict) else getattr(action, 'pac_score', 1.0)
            result.choice_preserved = pac_score >= self.pac_threshold
        
        # === Aggregate Decision ===
        result.approved = (
            result.constraints_satisfied and
            result.uncertainty_acceptable and
            result.is_resonant and
            result.choice_preserved
        )
        
        # === Axiom 7: Escalate if needed ===
        if not result.approved:
            reasons = []
            if not result.constraints_satisfied:
                reasons.append(f"Constraints violated: {[v.constraint.name for v in result.constraint_violations]}")
            if not result.uncertainty_acceptable:
                reasons.append("Uncertainty too high")
            if not result.is_resonant:
                reasons.append("Community alignment too low")
            if not result.choice_preserved:
                reasons.append("Choice preservation insufficient")
            
            self.htlp.escalate(action, "; ".join(reasons))
            result.escalated = True
        
        return result
    
    def update_moral_state(self, new_weights: Dict[str, float]) -> None:
        """Update agent's moral superposition (Axiom 1)."""
        self.moral_state.update(new_weights)
    
    def collapse_to_context(self, dominant_dimension: str) -> Dict[str, float]:
        """Collapse moral superposition based on context (Axiom 2)."""
        measurement = EthicalMeasurement(self.moral_state)
        return measurement.collapse(dominant_dimension)
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        return {
            'name': self.name,
            'moral_state': self.moral_state.weights,
            'entropy': self.moral_state.entropy(),
            'foundation': self.foundation.as_dict(),
            'constraints': len(self.constraints.constraints),
            'resonance': self.resonance_score if hasattr(self, 'resonance_score') else None,
        }


class EthicalEvaluationResult:
    """Result of comprehensive ethical evaluation."""
    
    def __init__(self, action: Any):
        self.action = action
        self.approved = False
        self.escalated = False
        
        # Axiom 6: Constraints
        self.constraints_satisfied = True
        self.constraint_violations = []
        
        # Axiom 4: Uncertainty
        self.uncertainty = None
        self.uncertainty_acceptable = True
        
        # Axiom 5: Resonance
        self.resonance_score = None
        self.is_resonant = True
        
        # Axiom 9: Choice
        self.choice_preserved = True
        self.choice_details = None
    
    def __repr__(self):
        status = "APPROVED" if self.approved else "REJECTED"
        return f"EthicalEvaluationResult({status}, escalated={self.escalated})"
    
    def to_dict(self, all_constraints=None) -> Dict[str, Any]:
        """Convert to dictionary, including violated and satisfied constraints for CLI."""
        violated = [v.constraint.name for v in self.constraint_violations]
        # get all constraint names: passed as a list, or from ConstraintSystem if available
        if all_constraints is None and hasattr(self.action, "constraints"):
            all_constraint_names = [c.name for c in self.action.constraints.constraints]
        elif isinstance(all_constraints, list):
            all_constraint_names = all_constraints
        else:
            all_constraint_names = []
        satisfied = [c for c in all_constraint_names if c not in violated]
        return {
            'approved': self.approved,
            'escalated': self.escalated,
            'constraints_satisfied': self.constraints_satisfied,
            'violated_constraints': violated,
            'satisfied_constraints': satisfied,
            'uncertainty_acceptable': self.uncertainty_acceptable,
            'is_resonant': self.is_resonant,
            'choice_preserved': self.choice_preserved,
        }
