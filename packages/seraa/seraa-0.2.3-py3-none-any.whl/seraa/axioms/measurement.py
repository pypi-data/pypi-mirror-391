"""
seraa/axioms/measurement.py - Axiom 2: Ethical Measurement (Collapse)

Models the act of decision-making as the 'collapse' of a superposed moral state into a specific ethical orientation.
"""

from typing import Dict, Any # type: ignore
from .superposition import MoralSuperposition

class EthicalMeasurement:
    """
    Collapses a superposed moral state into a chosen orientation given context/criteria.

    Example:
        >>> superposition = MoralSuperposition({'fairness': 0.4, 'autonomy': 0.3, 'care': 0.3})
        >>> measurer = EthicalMeasurement(superposition)
        >>> result = measurer.collapse('autonomy')  # context: autonomy is prioritized
        >>> print(result)
        {'fairness': 0.0, 'autonomy': 1.0, 'care': 0.0}
    """

    def __init__(self, superposed_state: MoralSuperposition):
        self.state = superposed_state

    def collapse(self, dominant_dimension: str) -> Dict[str, float]:
        """
        Collapse the moral state toward one dominant ethical orientation.

        Args:
            dominant_dimension: The ethical dimension selected by context

        Returns:
            Dictionary with only the dominant dimension set to 1.0, others to 0.0
        """
        collapsed = {k: 0.0 for k in self.state.weights}
        if dominant_dimension in collapsed:
            collapsed[dominant_dimension] = 1.0
        return collapsed

    def probabilistic_collapse(self) -> Dict[str, float]:
        """
        Collapse probabilistically, choosing orientation by weights.

        Returns:
            Dict with the chosen dimension set to 1.0, others 0.0
        """
        import random
        keys = list(self.state.weights.keys())
        weights = list(self.state.weights.values())
        if not keys:
            return {}
        chosen = random.choices(keys, weights=weights, k=1)[0]
        return {k: (1.0 if k == chosen else 0.0) for k in keys}
