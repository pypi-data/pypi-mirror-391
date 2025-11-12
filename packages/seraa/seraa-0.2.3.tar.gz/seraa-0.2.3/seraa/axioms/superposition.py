from typing import Dict, Optional
import math


class MoralSuperposition:
    """
    Represents the superposition of moral states as weighted ethical dimensions.
    
    Example:
        >>> state = MoralSuperposition({'fairness': 0.3, 'care': 0.5, 'autonomy': 0.2})
        >>> print(state.normalize())
        {'fairness': 0.3, 'care': 0.5, 'autonomy': 0.2}
        >>> state.update({'fairness': 0.4})
        >>> print(state.normalize())
        {'fairness': 0.4, 'care': 0.4, 'autonomy': 0.2}
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None) -> None:
        if weights is None:
            weights = {}
        self.weights = weights
        self.normalize()
    
    def normalize(self) -> Dict[str, float]:
        """Normalize weights so total sums to 1.0"""
        total = sum(self.weights.values())
        if total == 0:
            return self.weights
        for k in self.weights:
            self.weights[k] /= total
        return self.weights
    
    def update(self, new_weights: Dict[str, float]) -> None:
        """Update weights by merging and then normalize"""
        for key, value in new_weights.items():
            self.weights[key] = value
        self.normalize()
    
    def entropy(self) -> float:
        """Calculate Shannon entropy of the moral superposition"""
        total = sum(self.weights.values())
        if total == 0:
            return 0.0
        entropy = 0.0
        for p in (v / total for v in self.weights.values() if v > 0):
            entropy -= p * math.log2(p)
        return entropy
    
    def __repr__(self):
        return f"MoralSuperposition({self.weights})"
