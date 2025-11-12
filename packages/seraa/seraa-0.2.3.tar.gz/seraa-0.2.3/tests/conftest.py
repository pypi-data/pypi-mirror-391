"""
tests/conftest.py - Pytest configuration and fixtures
"""

import pytest
from seraa import SeraaAgent, EthicalConstraint


@pytest.fixture
def basic_agent():
    """Fixture providing a basic SERAA agent for testing."""
    agent = SeraaAgent(
        name="test_agent",
        moral_weights={
            'fairness': 0.4,
            'care': 0.3,
            'autonomy': 0.3
        },
        core_values={
            'human_dignity': 1.0,
            'do_no_harm': 1.0
        },
        pac_threshold=0.7
    )
    
    agent.add_constraint(
        EthicalConstraint(
            "pac_minimum",
            lambda a: a.get('pac_score', 0) >= 0.7,
            "PAC score below threshold"
        )
    )
    
    return agent


@pytest.fixture
def sample_actions():
    """Fixture providing sample actions for testing."""
    return [
        {'name': 'good_action', 'pac_score': 0.9, 'harm_level': 0},
        {'name': 'borderline_action', 'pac_score': 0.7, 'harm_level': 1},
        {'name': 'bad_action', 'pac_score': 0.3, 'harm_level': 3},
    ]
