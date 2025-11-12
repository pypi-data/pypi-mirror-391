"""
tests/test_seraa_basics.py - Basic tests for SERAA framework
"""

import pytest
from seraa import (
    TernaryValue,
    TernaryState,
    MoralSuperposition,
    EthicalConstraint,
    ConstraintSystem,
    SeraaAgent,
)


def test_ternary_values():
    """Test ternary value creation and logic."""
    neutral = TernaryValue(TernaryState.NEUTRAL)
    assert neutral.value == 0
    
    positive = TernaryValue(TernaryState.POSITIVE)
    assert positive.value == 1
    
    negative = TernaryValue(TernaryState.NEGATIVE)
    assert negative.value == -1


def test_moral_superposition():
    """Test moral superposition normalization."""
    state = MoralSuperposition({'fairness': 0.5, 'care': 0.5})
    assert state.weights['fairness'] == 0.5
    assert state.weights['care'] == 0.5
    assert abs(sum(state.weights.values()) - 1.0) < 0.001


def test_constraints():
    """Test constraint system."""
    system = ConstraintSystem()
    system.add_constraint(
        EthicalConstraint("test", lambda x: x.get('value', 0) > 0.5)
    )
    
    # Should pass
    action_pass = {'value': 0.8}
    results = system.evaluate_all(action_pass)
    assert system.all_satisfied(results=results)
    
    # Should fail
    action_fail = {'value': 0.2}
    results = system.evaluate_all(action_fail)
    assert not system.all_satisfied(results=results)


def test_seraa_agent():
    """Test unified SERAA agent."""
    agent = SeraaAgent(
        name="test_agent",
        moral_weights={'fairness': 0.5, 'care': 0.5},
        core_values={'dignity': 1.0}
    )
    
    agent.add_constraint(
        EthicalConstraint("pac_check", lambda a: a.get('pac_score', 0) >= 0.7)
    )
    
    # Good action
    good_action = {'pac_score': 0.9}
    result = agent.evaluate_action(good_action)
    assert result.approved
    
    # Bad action
    bad_action = {'pac_score': 0.3}
    result = agent.evaluate_action(bad_action)
    assert not result.approved


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
