"""
seraa/axioms/choice.py - Axiom 9: Preservation of Choice

An ethical system must preserve and expand the meaningful choices available to agents.
"""

from typing import Any, Callable, List, Dict
import math
from ..core.ternary import TernaryValue, TernaryState  # Fixed import


class ChoiceConstraint:
    """
    Implements Axiom 9: Preservation of Choice
    
    C(ψ,X) = H(ψ) · 1[viable options exist] · PAC(x)
    
    Where:
    - H(ψ): Entropy of moral states (diversity of possibilities)
    - 1[viable options exist]: Boolean indicator of viable choice set
    - PAC(x): Preservation of Agentic Capacity
    
    Usage:
        >>> actions = [action1, action2, action3]
        >>> constraint = ChoiceConstraint(
        ...     pac_evaluator=lambda a: a.preserves_agency,
        ...     viability_checker=lambda a: a.is_meaningful
        ... )
        >>> result = constraint.evaluate(moral_state, actions)
        >>> print(result.choice_preserved)  # True/False
    """
    
    def __init__(
        self,
        pac_evaluator: Callable[[Any], float],
        viability_checker: Callable[[Any], bool],
        pac_threshold: float = 0.7,
        viability_threshold: float = 0.5,
        diversity_threshold: float = 0.5
    ):
        """
        Initialize choice constraint evaluator.
        
        Args:
            pac_evaluator: Function that returns PAC score [0,1] for an action
            viability_checker: Function that returns True if action is viable
            pac_threshold: Minimum PAC score (δ in formulation)
            viability_threshold: Minimum viability score (ε in formulation)
            diversity_threshold: Minimum entropy/diversity (θ in formulation)
        """
        self.pac_evaluator = pac_evaluator
        self.viability_checker = viability_checker
        self.pac_threshold = pac_threshold
        self.viability_threshold = viability_threshold
        self.diversity_threshold = diversity_threshold
    
    def evaluate(
        self,
        moral_state: Dict[str, float],
        action_set: List[Any]
    ) -> 'ChoiceEvaluationResult':
        """
        Evaluate if choice is preserved for a given moral state and action set.
        
        Args:
            moral_state: Dictionary of moral dimensions and their weights
            action_set: List of possible actions
            
        Returns:
            ChoiceEvaluationResult with detailed evaluation
        """
        # Calculate entropy H(ψ)
        entropy = self._calculate_entropy(moral_state)
        
        # Filter viable options
        viable_actions = self._filter_viable_actions(action_set)
        
        # Check viability indicator
        has_viable_options = len(viable_actions) > 0
        
        # Calculate PAC scores
        pac_scores = {
            action: self.pac_evaluator(action) 
            for action in viable_actions
        }
        
        # Overall PAC (use max to be permissive)
        max_pac = max(pac_scores.values()) if pac_scores else 0.0
        
        # Calculate C(ψ,X)
        choice_value = entropy * (1.0 if has_viable_options else 0.0) * max_pac
        
        # Determine if choice is preserved
        choice_preserved = (
            entropy >= self.diversity_threshold and
            has_viable_options and
            max_pac >= self.pac_threshold
        )
        
        return ChoiceEvaluationResult(
            choice_value=choice_value,
            entropy=entropy,
            has_viable_options=has_viable_options,
            viable_action_count=len(viable_actions),
            pac_scores=pac_scores,
            max_pac=max_pac,
            choice_preserved=choice_preserved,
            ternary_state=self._determine_ternary_state(choice_preserved, max_pac)
        )
    
    def _calculate_entropy(self, moral_state: Dict[str, float]) -> float:
        """
        Calculate Shannon entropy of moral state.
        
        H(ψ) = -Σ p_i * log(p_i)
        """
        if not moral_state:
            return 0.0
        
        # Normalize to probabilities
        total = sum(moral_state.values())
        if total == 0:
            return 0.0
        
        probabilities = [v / total for v in moral_state.values()]
        
        # Calculate entropy
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        
        # Normalize to [0, 1] based on max possible entropy
        max_entropy = math.log2(len(moral_state)) if len(moral_state) > 0 else 1.0
        return entropy / max_entropy if max_entropy > 0 else 0.0
    
    def _filter_viable_actions(self, action_set: List[Any]) -> List[Any]:
        """Filter actions by viability and PAC thresholds"""
        viable: List[Any] = []
        for action in action_set:
            if (self.viability_checker(action) and 
                self.pac_evaluator(action) >= self.pac_threshold):
                viable.append(action)
        return viable
    
    def _determine_ternary_state(
        self,
        choice_preserved: bool,
        max_pac: float
    ) -> TernaryValue:
        """
        Determine ternary state based on evaluation.
        
        Returns:
            POSITIVE: Choice enhanced (high PAC, high diversity)
            NEUTRAL: Choice preserved (meets thresholds)
            NEGATIVE: Choice violated (below thresholds)
        """
        if not choice_preserved:
            return TernaryValue(TernaryState.NEGATIVE)
        elif max_pac > 0.9:  # Exceptional PAC preservation
            return TernaryValue(TernaryState.POSITIVE)
        else:
            return TernaryValue(TernaryState.NEUTRAL)


class ChoiceEvaluationResult:
    """Results of a choice preservation evaluation"""
    
    def __init__(
        self,
        choice_value: float,
        entropy: float,
        has_viable_options: bool,
        viable_action_count: int,
        pac_scores: Dict[Any, float],
        max_pac: float,
        choice_preserved: bool,
        ternary_state: TernaryValue
    ):
        self.choice_value = choice_value
        self.entropy = entropy
        self.has_viable_options = has_viable_options
        self.viable_action_count = viable_action_count
        self.pac_scores = pac_scores
        self.max_pac = max_pac
        self.choice_preserved = choice_preserved
        self.ternary_state = ternary_state
    
    def __repr__(self) -> str:
        return (
            f"ChoiceEvaluationResult("
            f"preserved={self.choice_preserved}, "
            f"state={self.ternary_state.value}, "
            f"viable_actions={self.viable_action_count})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "choice_value": self.choice_value,
            "entropy": self.entropy,
            "has_viable_options": self.has_viable_options,
            "viable_action_count": self.viable_action_count,
            "max_pac": self.max_pac,
            "choice_preserved": self.choice_preserved,
            "ternary_state": self.ternary_state.value
        }


def evaluate_choice_preservation(
    moral_state: Dict[str, float],
    actions: List[Any],
    pac_evaluator: Callable[[Any], float],
    viability_checker: Callable[[Any], bool],
    pac_threshold: float = 0.7
) -> ChoiceEvaluationResult:
    """
    Convenience function for evaluating choice preservation.
    
    Args:
        moral_state: Dictionary of moral dimension weights
        actions: List of possible actions
        pac_evaluator: Function to evaluate PAC for each action
        viability_checker: Function to check if action is viable
        pac_threshold: Minimum PAC threshold (default 0.7)
        
    Returns:
        ChoiceEvaluationResult
        
    Example:
        >>> moral_state = {'fairness': 0.3, 'autonomy': 0.4, 'care': 0.3}
        >>> actions = [action1, action2, action3]
        >>> result = evaluate_choice_preservation(
        ...     moral_state,
        ...     actions,
        ...     lambda a: a.pac_score,
        ...     lambda a: a.is_viable
        ... )
        >>> if result.choice_preserved:
        ...     print("Choice is preserved!")
    """
    constraint = ChoiceConstraint(
        pac_evaluator=pac_evaluator,
        viability_checker=viability_checker,
        pac_threshold=pac_threshold
    )
    return constraint.evaluate(moral_state, actions)


class ChoiceDiversityTracker:
    """
    Tracks choice diversity over time to detect erosion.
    
    Implements: ΔX̃ₜ = |X̃ₜ₊₁| - |X̃ₜ|
    If ΔX̃ₜ < 0 persistently, trigger corrective expansion
    """
    
    def __init__(self, alert_threshold: int = 3):
        """
        Args:
            alert_threshold: Number of consecutive decreases before alert
        """
        self.history: List[int] = []
        self.alert_threshold = alert_threshold
        self.consecutive_decreases = 0
    
    def track(self, viable_action_count: int) -> bool:
        """
        Track viable action count and detect erosion.
        
        Args:
            viable_action_count: Current number of viable actions
            
        Returns:
            True if corrective action needed (persistent decrease)
        """
        if self.history:
            delta = viable_action_count - self.history[-1]
            if delta < 0:
                self.consecutive_decreases += 1
            else:
                self.consecutive_decreases = 0
        
        self.history.append(viable_action_count)
        
        return self.consecutive_decreases >= self.alert_threshold
    
    def get_trend(self) -> str:
        """Get overall trend: 'expanding', 'stable', 'eroding'"""
        if len(self.history) < 2:
            return 'stable'
        
        recent = self.history[-5:] if len(self.history) >= 5 else self.history
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return 'expanding'
        elif all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return 'eroding'
        else:
            return 'stable'
