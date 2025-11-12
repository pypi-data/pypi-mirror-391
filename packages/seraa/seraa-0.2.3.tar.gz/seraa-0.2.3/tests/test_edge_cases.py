"""
tests/test_edge_cases.py - Edge cases and error handling
"""

import pytest
from seraa import (
    MoralSuperposition,
    EthicalConstraint,
    ConstraintSystem,
    SeraaAgent,
)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_moral_state(self):
        state = MoralSuperposition({})
        assert state.entropy() == 0.0
    
    def test_single_dimension_state(self):
        state = MoralSuperposition({'fairness': 1.0})
        assert state.weights['fairness'] == 1.0
        assert state.entropy() == 0.0
    
    def test_zero_sum_weights(self):
        state = MoralSuperposition({'a': 0.0, 'b': 0.0})
        # Should handle gracefully
        assert sum(state.weights.values()) >= 0
    
    def test_constraint_with_missing_key(self):
        constraint = EthicalConstraint(
            "test",
            lambda x: x.get('nonexistent', 0) > 0.5
        )
        result = constraint.evaluate({})
        assert not result.satisfied
    
    def test_agent_with_no_constraints(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 1.0},
            core_values={'dignity': 1.0}
        )
        
        # Should still evaluate
        result = agent.evaluate_action({'pac_score': 0.9})
        # With no constraints added, base constraints should still apply
        assert result is not None
    
    def test_very_high_pac_score(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 1.0},
            core_values={'dignity': 1.0}
        )
        
        result = agent.evaluate_action({'pac_score': 1.0})
        assert result.approved
    
    def test_very_low_pac_score(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 1.0},
            core_values={'dignity': 1.0}
        )
        
        result = agent.evaluate_action({'pac_score': 0.0})
        assert not result.approved
