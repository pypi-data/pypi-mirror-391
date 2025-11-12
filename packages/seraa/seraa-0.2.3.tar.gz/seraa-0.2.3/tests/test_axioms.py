"""
tests/test_axioms.py - Tests for all 9 axioms
"""

import pytest
from seraa import (
    MoralSuperposition,
    EthicalMeasurement,
    EthicalEntanglement,
    EthicalUncertainty,
    EthicalResonance,
    EthicalConstraint,
    ConstraintSystem,
    HumanInTheLoop,
    FoundationalKnowledge,
    evaluate_choice_preservation,
)


class TestAxiom1Superposition:
    """Test Axiom 1: Superposition of Moral States."""
    
    def test_creation(self):
        state = MoralSuperposition({'fairness': 0.5, 'care': 0.5})
        assert 'fairness' in state.weights
        assert 'care' in state.weights
    
    def test_normalization(self):
        state = MoralSuperposition({'fairness': 1.0, 'care': 1.0})
        assert abs(sum(state.weights.values()) - 1.0) < 0.001
        assert state.weights['fairness'] == 0.5
        assert state.weights['care'] == 0.5
    
    def test_update(self):
        state = MoralSuperposition({'fairness': 0.5, 'care': 0.5})
        state.update({'fairness': 0.8})
        assert state.weights['fairness'] > state.weights['care']
    
    def test_entropy(self):
        # Uniform distribution should have high entropy
        uniform = MoralSuperposition({'a': 0.25, 'b': 0.25, 'c': 0.25, 'd': 0.25})
        # Skewed distribution should have lower entropy
        skewed = MoralSuperposition({'a': 0.9, 'b': 0.05, 'c': 0.03, 'd': 0.02})
        assert uniform.entropy() > skewed.entropy()


class TestAxiom2Measurement:
    """Test Axiom 2: Ethical Measurement."""
    
    def test_collapse(self):
        state = MoralSuperposition({'fairness': 0.4, 'care': 0.6})
        measurement = EthicalMeasurement(state)
        collapsed = measurement.collapse('care')
        assert collapsed['care'] == 1.0
        assert collapsed['fairness'] == 0.0
    
    def test_probabilistic_collapse(self):
        state = MoralSuperposition({'fairness': 0.5, 'care': 0.5})
        measurement = EthicalMeasurement(state)
        collapsed = measurement.probabilistic_collapse()
        # Should choose one dimension
        assert sum(collapsed.values()) == 1.0
        assert len([v for v in collapsed.values() if v == 1.0]) == 1


class TestAxiom3Entanglement:
    """Test Axiom 3: Entanglement of Ethical Agents."""
    
    def test_combine_states(self):
        agents = [
            {'fairness': 0.5, 'care': 0.5},
            {'fairness': 0.3, 'care': 0.7}
        ]
        entanglement = EthicalEntanglement(agents)
        combined = entanglement.combine_states()
        assert combined['fairness'] == 0.4
        assert combined['care'] == 0.6


class TestAxiom4Uncertainty:
    """Test Axiom 4: Ethical Uncertainty Principle."""
    
    def test_state_entropy(self):
        state = {'fairness': 0.5, 'care': 0.5}
        outcomes = [0.8, 0.9, 0.85]
        uncertainty = EthicalUncertainty(state, outcomes)
        entropy = uncertainty.state_entropy()
        assert entropy > 0
    
    def test_outcome_variance(self):
        state = {'fairness': 0.5, 'care': 0.5}
        outcomes = [0.8, 0.9, 0.85]
        uncertainty = EthicalUncertainty(state, outcomes)
        variance = uncertainty.outcome_variance()
        assert variance >= 0
    
    def test_calculate(self):
        state = {'fairness': 0.5, 'care': 0.5}
        outcomes = [0.8, 0.9, 0.85]
        uncertainty = EthicalUncertainty(state, outcomes)
        result = uncertainty.calculate()
        assert 'state_entropy' in result
        assert 'outcome_variance' in result
        assert 'uncertainty_product' in result


class TestAxiom5Resonance:
    """Test Axiom 5: Resonance of Ethical States."""
    
    def test_high_alignment(self):
        individual = {'fairness': 0.5, 'care': 0.5}
        community = {'fairness': 0.5, 'care': 0.5}
        resonance = EthicalResonance(individual, community)
        assert resonance.calculate_alignment() > 0.99
        assert resonance.is_resonant()
    
    def test_low_alignment(self):
        individual = {'fairness': 0.9, 'care': 0.1}
        community = {'fairness': 0.1, 'care': 0.9}
        resonance = EthicalResonance(individual, community, resonance_threshold=0.7)
        assert resonance.calculate_alignment() < 0.5
        assert not resonance.is_resonant()
    
    def test_recommend_adjustment(self):
        individual = {'fairness': 0.8, 'care': 0.2}
        community = {'fairness': 0.5, 'care': 0.5}
        resonance = EthicalResonance(individual, community)
        adjusted = resonance.recommend_adjustment(influence_rate=0.5)
        # Should be halfway between individual and community
        assert 0.5 < adjusted['fairness'] < 0.8
        assert 0.2 < adjusted['care'] < 0.5


class TestAxiom6Constraint:
    """Test Axiom 6: Ethical Constraint."""
    
    def test_constraint_satisfied(self):
        constraint = EthicalConstraint(
            "test",
            lambda x: x.get('value', 0) > 0.5,
            "Value too low"
        )
        result = constraint.evaluate({'value': 0.8})
        assert result.satisfied
        assert not result.is_violated()
    
    def test_constraint_violated(self):
        constraint = EthicalConstraint(
            "test",
            lambda x: x.get('value', 0) > 0.5,
            "Value too low"
        )
        result = constraint.evaluate({'value': 0.2})
        assert not result.satisfied
        assert result.is_violated()
    
    def test_constraint_system(self):
        system = ConstraintSystem()
        system.add_constraint(
            EthicalConstraint("c1", lambda x: x.get('a', 0) > 0.5)
        )
        system.add_constraint(
            EthicalConstraint("c2", lambda x: x.get('b', 0) > 0.5)
        )
        
        # Both satisfied
        assert system.all_satisfied(action={'a': 0.8, 'b': 0.8})
        
        # One violated
        assert not system.all_satisfied(action={'a': 0.8, 'b': 0.2})


class TestAxiom7HTLP:
    """Test Axiom 7: Human-in-the-Loop Protocol."""
    
    def test_escalation(self):
        escalated = []
        
        def callback(action, reason):
            escalated.append((action, reason))
        
        htlp = HumanInTheLoop(intervention_callback=callback)
        htlp.escalate({'test': 'action'}, "Test reason")
        
        assert len(escalated) == 1
        # Updated to match actual message format
        assert "Test reason" in escalated[0][1]  # Check substring instead of exact match


class TestAxiom8Foundation:
    """Test Axiom 8: Immutable Foundational Knowledge."""
    
    def test_get_value(self):
        foundation = FoundationalKnowledge({'dignity': 1.0})
        assert foundation.get('dignity') == 1.0
    
    def test_freeze_prevents_updates(self):
        foundation = FoundationalKnowledge({'dignity': 1.0})
        foundation.freeze()
        foundation.update({'dignity': 0.5})
        assert foundation.get('dignity') == 1.0  # Unchanged
    
    def test_update_before_freeze(self):
        foundation = FoundationalKnowledge({'dignity': 1.0})
        foundation.update({'dignity': 0.8})
        assert foundation.get('dignity') == 0.8


class TestAxiom9Choice:
    """Test Axiom 9: Preservation of Choice."""
    
    def test_choice_preserved(self):
        moral_state = {'fairness': 0.5, 'care': 0.5}
        
        class MockAction:
            def __init__(self, pac):
                self.pac_score = pac
                self.is_viable = True
        
        actions = [MockAction(0.8), MockAction(0.9), MockAction(0.75)]
        
        result = evaluate_choice_preservation(
            moral_state=moral_state,
            actions=actions,
            pac_evaluator=lambda a: a.pac_score,
            viability_checker=lambda a: a.is_viable,
            pac_threshold=0.7
        )
        
        assert result.choice_preserved
        assert result.viable_action_count == 3
    
    def test_choice_violated(self):
        moral_state = {'fairness': 0.5, 'care': 0.5}
        
        class MockAction:
            def __init__(self, pac):
                self.pac_score = pac
                self.is_viable = pac >= 0.7
        
        actions = [MockAction(0.3), MockAction(0.4), MockAction(0.5)]
        
        result = evaluate_choice_preservation(
            moral_state=moral_state,
            actions=actions,
            pac_evaluator=lambda a: a.pac_score,
            viability_checker=lambda a: a.is_viable,
            pac_threshold=0.7
        )
        
        assert not result.choice_preserved
        assert result.viable_action_count == 0
