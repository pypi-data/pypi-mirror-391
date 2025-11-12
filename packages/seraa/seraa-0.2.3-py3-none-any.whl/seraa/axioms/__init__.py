"""
seraa/axioms/__init__.py

All SERAA axioms for ethical AI reasoning.
"""

from .superposition import MoralSuperposition
from .measurement import EthicalMeasurement
from .entanglement import EthicalEntanglement
from .uncertainty import EthicalUncertainty, calculate_uncertainty_product
from .resonance import EthicalResonance, CommunityResonanceTracker
from .constraint import (
    EthicalConstraint,
    ConstraintResult,
    ConstraintSystem,
    create_threshold_constraint,
)
from .htlp import HumanInTheLoop
from .foundation import FoundationalKnowledge
from .choice import (
    ChoiceConstraint,
    ChoiceEvaluationResult,
    evaluate_choice_preservation,
    ChoiceDiversityTracker,
)

__all__ = [
    # Axiom 1: Superposition
    'MoralSuperposition',
    
    # Axiom 2: Measurement
    'EthicalMeasurement',
    
    # Axiom 3: Entanglement
    'EthicalEntanglement',
    
    # Axiom 4: Uncertainty
    'EthicalUncertainty',
    'calculate_uncertainty_product',
    
    # Axiom 5: Resonance
    'EthicalResonance',
    'CommunityResonanceTracker',
    
    # Axiom 6: Constraint
    'EthicalConstraint',
    'ConstraintResult',
    'ConstraintSystem',
    'create_threshold_constraint',
    
    # Axiom 7: HTLP
    'HumanInTheLoop',
    
    # Axiom 8: Foundation
    'FoundationalKnowledge',
    
    # Axiom 9: Choice
    'ChoiceConstraint',
    'ChoiceEvaluationResult',
    'evaluate_choice_preservation',
    'ChoiceDiversityTracker',
]
