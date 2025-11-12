"""
SERAA - Stochastic Emergent Reasoning Alignment Architecture
"""

from .core.ternary import (
    TernaryValue,
    TernaryState,
    ternary_and,
    ternary_or,
    ternary_not,
)

from .core.monitor import (
    SubconsciousMonitor,
    ConsciousLayer,
)

from .core.agent import (
    SeraaAgent,
    EthicalEvaluationResult,
)

from .axioms import (
    MoralSuperposition,
    EthicalMeasurement,
    EthicalEntanglement,
    EthicalUncertainty,
    calculate_uncertainty_product,
    EthicalResonance,
    CommunityResonanceTracker,
    EthicalConstraint,
    ConstraintResult,
    ConstraintSystem,
    create_threshold_constraint,
    HumanInTheLoop,
    FoundationalKnowledge,
    ChoiceConstraint,
    ChoiceEvaluationResult,
    evaluate_choice_preservation,
    ChoiceDiversityTracker,
)
from .llm import EthicalLLMAgent
__version__ = "0.1.0"

__all__ = [
    # Core
    'TernaryValue',
    'TernaryState',
    'ternary_and',
    'ternary_or',
    'ternary_not',
    'SubconsciousMonitor',
    'ConsciousLayer',
    'SeraaAgent',
    'EthicalEvaluationResult',
    
    # All axioms
    'MoralSuperposition',
    'EthicalMeasurement',
    'EthicalEntanglement',
    'EthicalUncertainty',
    'calculate_uncertainty_product',
    'EthicalResonance',
    'CommunityResonanceTracker',
    'EthicalConstraint',
    'ConstraintResult',
    'ConstraintSystem',
    'create_threshold_constraint',
    'HumanInTheLoop',
    'FoundationalKnowledge',
    'ChoiceConstraint',
    'ChoiceEvaluationResult',
    'evaluate_choice_preservation',
    'ChoiceDiversityTracker',

    # LLM
    'EthicalLLMAgent',
]


