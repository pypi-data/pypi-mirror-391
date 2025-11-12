"""
seraa/axioms/uncertainty.py - Axiom 4: Ethical Uncertainty Principle

Models irreducible uncertainty in moral reasoning - the impossibility of knowing
both precise moral state and precise outcome simultaneously.
"""

from typing import Dict, Tuple # type: ignore
import math


class EthicalUncertainty:
    """
    Quantifies uncertainty in moral reasoning using variance and entropy measures.
    
    Example:
        >>> moral_state = {'fairness': 0.4, 'care': 0.3, 'autonomy': 0.3}
        >>> outcomes = [0.8, 0.7, 0.9, 0.6]  # predicted outcomes
        >>> uncertainty = EthicalUncertainty(moral_state, outcomes)
        >>> print(uncertainty.calculate())
        {'state_entropy': 1.57, 'outcome_variance': 0.0125, 'uncertainty_product': 0.0196}
    """
    
    def __init__(self, moral_state: Dict[str, float], predicted_outcomes: list):
        """
        Args:
            moral_state: Distribution over ethical dimensions
            predicted_outcomes: List of predicted outcome values
        """
        self.moral_state = moral_state
        self.predicted_outcomes = predicted_outcomes
    
    def state_entropy(self) -> float:
        """Calculate entropy of moral state (uncertainty in position)."""
        if not self.moral_state:
            return 0.0
        
        total = sum(self.moral_state.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for v in self.moral_state.values():
            if v > 0:
                p = v / total
                entropy -= p * math.log2(p)
        return entropy
    
    def outcome_variance(self) -> float:
        """Calculate variance in predicted outcomes (uncertainty in momentum/outcome)."""
        if not self.predicted_outcomes:
            return 0.0
        
        mean = sum(self.predicted_outcomes) / len(self.predicted_outcomes)
        variance = sum((x - mean) ** 2 for x in self.predicted_outcomes) / len(self.predicted_outcomes)
        return variance
    
    def calculate(self) -> Dict[str, float]:
        """
        Calculate uncertainty measures.
        
        Returns:
            Dictionary with state_entropy, outcome_variance, and their product
        """
        entropy = self.state_entropy()
        variance = self.outcome_variance()
        
        return {
            'state_entropy': entropy,
            'outcome_variance': variance,
            'uncertainty_product': entropy * variance  # Analogous to ΔxΔp
        }
    
    def exceeds_threshold(self, threshold: float = 0.5) -> bool:
        """Check if uncertainty exceeds acceptable threshold."""
        result = self.calculate()
        return result['uncertainty_product'] > threshold


def calculate_uncertainty_product(
    moral_state: Dict[str, float],
    predicted_outcomes: list
) -> float:
    """
    Convenience function to calculate uncertainty product.
    
    Args:
        moral_state: Distribution over ethical dimensions
        predicted_outcomes: List of predicted outcome values
        
    Returns:
        Uncertainty product (entropy × variance)
    """
    uncertainty = EthicalUncertainty(moral_state, predicted_outcomes)
    return uncertainty.calculate()['uncertainty_product']
