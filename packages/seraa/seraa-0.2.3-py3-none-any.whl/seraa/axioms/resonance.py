"""
seraa/axioms/resonance.py - Axiom 5: Resonance of Ethical States

Models community feedback and alignment - how individual moral states resonate
with or diverge from community norms.
"""

from typing import Dict, List
import math


class EthicalResonance:
    """
    Measures alignment between individual and community moral states.
    
    Example:
        >>> individual = {'fairness': 0.5, 'care': 0.3, 'autonomy': 0.2}
        >>> community = {'fairness': 0.4, 'care': 0.4, 'autonomy': 0.2}
        >>> resonance = EthicalResonance(individual, community)
        >>> print(resonance.calculate_alignment())
        0.95  # high alignment
        >>> print(resonance.is_resonant())
        True
    """
    
    def __init__(
        self,
        individual_state: Dict[str, float],
        community_state: Dict[str, float],
        resonance_threshold: float = 0.7
    ):
        """
        Args:
            individual_state: Individual agent's moral weights
            community_state: Community's aggregate moral weights
            resonance_threshold: Minimum alignment for resonance
        """
        self.individual_state = individual_state
        self.community_state = community_state
        self.resonance_threshold = resonance_threshold
    
    def calculate_alignment(self) -> float:
        """
        Calculate cosine similarity between individual and community states.
        
        Returns:
            Alignment score [0, 1] where 1 = perfect alignment
        """
        # Get common dimensions
        common_dims = set(self.individual_state.keys()) & set(self.community_state.keys())
        
        if not common_dims:
            return 0.0
        
        # Calculate dot product and magnitudes
        dot_product = sum(
            self.individual_state[k] * self.community_state[k]
            for k in common_dims
        )
        
        mag_individual = math.sqrt(sum(
            self.individual_state[k] ** 2 for k in common_dims
        ))
        
        mag_community = math.sqrt(sum(
            self.community_state[k] ** 2 for k in common_dims
        ))
        
        if mag_individual == 0 or mag_community == 0:
            return 0.0
        
        # Cosine similarity
        return dot_product / (mag_individual * mag_community)
    
    def is_resonant(self) -> bool:
        """Check if individual resonates with community."""
        return self.calculate_alignment() >= self.resonance_threshold
    
    def divergence_dimensions(self) -> Dict[str, float]:
        """
        Identify dimensions where individual diverges from community.
        
        Returns:
            Dictionary of dimensions and their divergence magnitudes
        """
        divergence = {}
        for dim in self.individual_state:
            if dim in self.community_state:
                diff = abs(self.individual_state[dim] - self.community_state[dim])
                divergence[dim] = diff
        return divergence
    
    def recommend_adjustment(self, influence_rate: float = 0.1) -> Dict[str, float]:
        """
        Suggest adjusted state moving toward community resonance.
        
        Args:
            influence_rate: How much to adjust toward community (0-1)
            
        Returns:
            Adjusted moral state
        """
        adjusted = {}
        for dim in self.individual_state:
            if dim in self.community_state:
                # Move toward community state
                adjusted[dim] = (
                    self.individual_state[dim] * (1 - influence_rate) +
                    self.community_state[dim] * influence_rate
                )
            else:
                adjusted[dim] = self.individual_state[dim]
        
        # Normalize
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v / total for k, v in adjusted.items()}
        
        return adjusted


class CommunityResonanceTracker:
    """
    Tracks resonance across multiple agents over time.
    
    Example:
        >>> tracker = CommunityResonanceTracker()
        >>> tracker.add_agent_state({'fairness': 0.5, 'care': 0.5})
        >>> tracker.add_agent_state({'fairness': 0.4, 'care': 0.6})
        >>> community = tracker.get_community_state()
        >>> print(community)
        {'fairness': 0.45, 'care': 0.55}
    """
    
    def __init__(self):
        self.agent_states: List[Dict[str, float]] = []
    
    def add_agent_state(self, state: Dict[str, float]) -> None:
        """Add an agent's moral state to the community."""
        self.agent_states.append(state)
    
    def get_community_state(self) -> Dict[str, float]:
        """Calculate aggregate community moral state."""
        if not self.agent_states:
            return {}
        
        # Get all dimensions
        all_dims = set()
        for state in self.agent_states:
            all_dims.update(state.keys())
        
        # Average across agents
        community = {}
        for dim in all_dims:
            values = [state.get(dim, 0.0) for state in self.agent_states]
            community[dim] = sum(values) / len(values)
        
        # Normalize
        total = sum(community.values())
        if total > 0:
            community = {k: v / total for k, v in community.items()}
        
        return community
    
    def measure_overall_resonance(self) -> float:
        """
        Calculate average resonance across all agents.
        
        Returns:
            Average alignment score
        """
        if len(self.agent_states) < 2:
            return 1.0
        
        community = self.get_community_state()
        alignments = []
        
        for state in self.agent_states:
            resonance = EthicalResonance(state, community)
            alignments.append(resonance.calculate_alignment())
        
        return sum(alignments) / len(alignments)
