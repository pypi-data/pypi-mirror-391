"""
tests/test_agent.py - Tests for unified SERAA agent
"""

import pytest
from seraa import SeraaAgent, EthicalConstraint


class TestSeraaAgent:
    """Test the unified SERAA agent."""
    
    def test_agent_creation(self):
        agent = SeraaAgent(
            name="test_agent",
            moral_weights={'fairness': 0.5, 'care': 0.5},
            core_values={'dignity': 1.0}
        )
        assert agent.name == "test_agent"
        assert agent.moral_state.weights['fairness'] == 0.5
    
    def test_add_constraint(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 0.5, 'care': 0.5},
            core_values={'dignity': 1.0}
        )
        
        agent.add_constraint(
            EthicalConstraint("test", lambda a: a.get('value', 0) > 0.5)
        )
        
        assert len(agent.constraints.constraints) >= 1
    
    def test_approve_good_action(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 0.5, 'care': 0.5},
            core_values={'dignity': 1.0},
            pac_threshold=0.7
        )
        
        agent.add_constraint(
            EthicalConstraint("pac", lambda a: a.get('pac_score', 0) >= 0.7)
        )
        
        result = agent.evaluate_action({'pac_score': 0.9, 'harm_level': 0})
        assert result.approved
        assert result.constraints_satisfied
    
    def test_reject_bad_action(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 0.5, 'care': 0.5},
            core_values={'dignity': 1.0},
            pac_threshold=0.7
        )
        
        agent.add_constraint(
            EthicalConstraint("pac", lambda a: a.get('pac_score', 0) >= 0.7)
        )
        
        result = agent.evaluate_action({'pac_score': 0.3, 'harm_level': 3})
        assert not result.approved
    
    def test_update_moral_state(self):
        agent = SeraaAgent(
            name="test",
            moral_weights={'fairness': 0.5, 'care': 0.5},
            core_values={'dignity': 1.0}
        )
        
        agent.update_moral_state({'fairness': 0.8})
        assert agent.moral_state.weights['fairness'] > 0.5
