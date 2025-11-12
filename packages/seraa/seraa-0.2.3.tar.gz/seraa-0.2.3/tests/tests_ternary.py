import pytest
from seraa import (
    TernaryValue,
    TernaryState,
    ternary_and,
    ternary_or,
    ternary_not,
    evaluate_choice_preservation,
    ChoiceConstraint,
)

class TestTernaryValue:
    """Test TernaryValue class"""
    
    def test_creation_valid_values(self):
        """Test creating ternary values with valid inputs"""
        neg = TernaryValue(-1)
        neutral = TernaryValue(0)
        pos = TernaryValue(1)
        
        assert neg.value == -1
        assert neutral.value == 0
        assert pos.value == 1
    
    def test_creation_invalid_value(self):
        """Test that invalid values raise ValueError"""
        with pytest.raises(ValueError):
            TernaryValue(2)
        
        with pytest.raises(ValueError):
            TernaryValue(-2)
    
    def test_to_binary_pair(self):
        """Test conversion to binary pairs"""
        assert TernaryValue(-1).to_binary_pair() == (0, 0)
        assert TernaryValue(0).to_binary_pair() == (0, 1)
        assert TernaryValue(1).to_binary_pair() == (1, 0)
    
    def test_from_binary_pair(self):
        """Test creation from binary pairs"""
        neg = TernaryValue.from_binary_pair(0, 0)
        neutral = TernaryValue.from_binary_pair(0, 1)
        pos = TernaryValue.from_binary_pair(1, 0)
        
        assert neg.value == -1
        assert neutral.value == 0
        assert pos.value == 1
    
    def test_from_binary_pair_invalid(self):
        """Test that invalid binary pair raises error"""
        with pytest.raises(ValueError):
            TernaryValue.from_binary_pair(1, 1)
    
    def test_roundtrip_conversion(self):
        """Test binary conversion roundtrip"""
        for value in [-1, 0, 1]:
            original = TernaryValue(value)
            binary = original.to_binary_pair()
            restored = TernaryValue.from_binary_pair(*binary)
            assert restored.value == original.value
    
    def test_to_quantum_basis(self):
        """Test quantum basis representation"""
        assert TernaryValue(-1).to_quantum_basis() == "|-1⟩"
        assert TernaryValue(0).to_quantum_basis() == "|0⟩"
        assert TernaryValue(1).to_quantum_basis() == "|1⟩"
    
    def test_equality(self):
        """Test equality comparisons"""
        assert TernaryValue(0) == TernaryValue(0)
        assert TernaryValue(1) == TernaryValue(1)
        assert TernaryValue(0) == 0
        assert TernaryValue(1) != TernaryValue(0)
    
    def test_repr(self):
        """Test string representation"""
        assert repr(TernaryValue(0)) == "TernaryValue(0)"
    
    def test_hash(self):
        """Test that values are hashable"""
        values = {TernaryValue(0), TernaryValue(1), TernaryValue(-1)}
        assert len(values) == 3


class TestTernaryLogic:
    """Test ternary logic operations"""
    
    def test_ternary_and(self):
        """Test ternary AND operation (Kleene logic)"""
        assert ternary_and(TernaryValue(1), TernaryValue(1)).value == 1
        assert ternary_and(TernaryValue(1), TernaryValue(0)).value == 0
        assert ternary_and(TernaryValue(1), TernaryValue(-1)).value == -1
        assert ternary_and(TernaryValue(0), TernaryValue(0)).value == 0
        assert ternary_and(TernaryValue(-1), TernaryValue(-1)).value == -1
    
    def test_ternary_or(self):
        """Test ternary OR operation (Kleene logic)"""
        assert ternary_or(TernaryValue(1), TernaryValue(1)).value == 1
        assert ternary_or(TernaryValue(1), TernaryValue(0)).value == 1
        assert ternary_or(TernaryValue(1), TernaryValue(-1)).value == 1
        assert ternary_or(TernaryValue(0), TernaryValue(0)).value == 0
        assert ternary_or(TernaryValue(-1), TernaryValue(0)).value == 0
    
    def test_ternary_not(self):
        """Test ternary NOT operation"""
        assert ternary_not(TernaryValue(1), TernaryValue(1)).value == -1
        assert ternary_not(TernaryValue(0), TernaryValue(-1)).value == 0
        assert ternary_not(TernaryValue(-1), TernaryValue(0)).value == 1


"""
tests/test_monitor.py - Tests for monitoring system
"""

class TestSubconsciousMonitor:
    """Test SubconsciousMonitor class"""
    
    def test_optimal_state(self):

        escalation_events = []
        def callback(name, state):
            escalation_events.append((name, state))

        monitor = SubconsciousMonitor(
            name="test",
            optimal_checker=lambda x: x > 0.8,
            escalation_callback=callback
        )
        
        state = monitor.check(0.9)
        assert state.value == TernaryState.NEUTRAL
        assert monitor.is_subconscious
        assert len(escalation_events) == 0  # No escalation should occur for optimal state
    
    def test_correction_needed(self):
        """Test monitor detecting correction need"""
        monitor = SubconsciousMonitor(
            name="test",
            optimal_checker=lambda x: x > 0.8,
            correction_checker=lambda x: x < 0.5
        )
        
        state = monitor.check(0.3)
        assert state.value == TernaryState.NEGATIVE
        assert not monitor.is_subconscious
    
    def test_enhancement_opportunity(self):
        """Test monitor detecting enhancement opportunity"""
        monitor = SubconsciousMonitor(
            name="test",
            optimal_checker=lambda x: x > 0.8,
            enhancement_checker=lambda x: x > 0.95
        )
        
        state = monitor.check(0.97)
        assert state.value == TernaryState.NEUTRAL  # Still optimal
        
        # With different optimal checker
        monitor2 = SubconsciousMonitor(
            name="test2",
            optimal_checker=lambda x: 0.8 < x < 0.95,
            enhancement_checker=lambda x: x > 0.95
        )
        state2 = monitor2.check(0.97)
        assert state2.value == TernaryState.POSITIVE
    
    def test_escalation_callback(self):
        """Test that escalation callback is called"""
        escalation_events = []
        
        def callback(name: str, state):
            # Normalize state to TernaryState for consistent comparisons
            try:
                if hasattr(state, "value"):
                    # state is likely a TernaryValue; convert its numeric value to TernaryState
                    normalized = TernaryState(state.value)
                elif isinstance(state, int):
                    # state might already be an int representation
                    normalized = TernaryState(state)
                else:
                    # Already a TernaryState or unknown - keep as is
                    normalized = state
            except Exception:
                # Fallback: append as-is if conversion fails
                normalized = state
            escalation_events.append((name, normalized))
        
        monitor = SubconsciousMonitor(
            name="test",
            optimal_checker=lambda x: x > 0.8,
            escalation_callback=callback
        )
        
        monitor.check(0.9)  # Optimal - no escalation
        assert len(escalation_events) == 0
        
        monitor.check(0.5)  # Below optimal - escalation
        assert len(escalation_events) == 1
        assert escalation_events[0][0] == "test"
        assert escalation_events[0][1] == TernaryState.NEGATIVE
    
    def test_statistics(self):
        """Test monitoring statistics"""
        monitor = SubconsciousMonitor(
            name="test",
            optimal_checker=lambda x: x > 0.8
        )
        
        # Run multiple checks
        monitor.check(0.9)  # Optimal
        monitor.check(0.9)  # Optimal
        monitor.check(0.5)  # Below
        monitor.check(0.9)  # Optimal
        
        stats = monitor.get_statistics()
        assert stats['total_checks'] == 4
        assert stats['subconscious_rate'] == 0.75
        assert stats['correction_rate'] == 0.25


class TestConsciousLayer:
    """Test ConsciousLayer class"""
    
    def test_add_monitor(self):
        """Test adding monitors to conscious layer"""
        conscious = ConsciousLayer()
        monitor = SubconsciousMonitor("test", lambda x: x > 0.8)
        
        conscious.add_monitor(monitor)
        assert "test" in conscious.monitors
    
    def test_attention_queue(self):
        """Test attention queue management"""
        conscious = ConsciousLayer()
        monitor = SubconsciousMonitor("test", lambda x: x > 0.8)
        conscious.add_monitor(monitor)
        
        # Optimal check - no escalation
        monitor.check(0.9)
        assert len(conscious.get_attention_queue()) == 0
        
        # Below optimal - escalation
        monitor.check(0.5)
        queue = conscious.get_attention_queue()
        assert len(queue) == 1
        assert queue[0][0] == "test"
    
    def test_clear_attention(self):
        """Test clearing attention items"""
        conscious = ConsciousLayer()
        monitor = SubconsciousMonitor("test", lambda x: x > 0.8)
        conscious.add_monitor(monitor)
        
        monitor.check(0.5)  # Escalate
        assert len(conscious.get_attention_queue()) == 1
        
        conscious.clear_attention("test")
        assert len(conscious.get_attention_queue()) == 0
    
    def test_attention_limit(self):
        """Test maximum attention items limit"""
        conscious = ConsciousLayer(max_attention_items=3)
        
        monitors = [
            SubconsciousMonitor(f"test{i}", lambda x: x > 0.8)
            for i in range(5)
        ]
        
        for monitor in monitors:
            conscious.add_monitor(monitor)
            monitor.check(0.5)  # All escalate
        
        # Should only keep top 3 by urgency
        queue = conscious.get_attention_queue()
        assert len(queue) <= 3
    
    def test_conscious_report(self):
        """Test conscious awareness report"""
        conscious = ConsciousLayer()
        monitor1 = SubconsciousMonitor("test1", lambda x: x > 0.8)
        monitor2 = SubconsciousMonitor("test2", lambda x: x > 0.8)
        
        conscious.add_monitor(monitor1)
        conscious.add_monitor(monitor2)
        
        monitor1.check(0.5)  # Escalate
        monitor2.check(0.9)  # Subconscious
        
        report = conscious.get_conscious_report()
        assert report['attention_items'] == 1
        assert len(report['subconscious_monitors']) == 1
        assert 'test2' in report['subconscious_monitors']
        assert report['total_monitors'] == 2


"""
tests/test_choice.py - Tests for Axiom 9: Choice Preservation
"""


class MockAction:
    """Mock action for testing"""
    def __init__(self, pac_score, is_viable=True):
        self.pac_score = pac_score
        self.is_viable = is_viable


class TestChoiceConstraint:
    """Test ChoiceConstraint implementation"""

    def pac_evaluator(self, action):
        return action.pac_score

    def viability_checker(self, action):
        return action.is_viable
    
    def test_choice_preserved(self):
        """Test case where choice is preserved"""
        moral_state = {
            'fairness': 0.3,
            'autonomy': 0.4,
            'care': 0.3
        }
        
        actions = [
            MockAction(pac_score=0.8),
            MockAction(pac_score=0.9),
            MockAction(pac_score=0.75)
        ]
        
        result = evaluate_choice_preservation(
            moral_state,
            actions,
            pac_evaluator=self.pac_evaluator,
            viability_checker=self.viability_checker
        )
        
        assert result.choice_preserved
        assert result.has_viable_options
        assert result.viable_action_count == 3
        assert result.max_pac == 0.9
    
    def test_choice_violated_no_viable_actions(self):
        """Test case where no viable actions exist"""
        moral_state = {'fairness': 0.5, 'care': 0.5}
        
        actions = [
            MockAction(pac_score=0.5, is_viable=False),
            MockAction(pac_score=0.6, is_viable=False)
        ]
        
        result = evaluate_choice_preservation(
            moral_state,
            actions,
            pac_evaluator=self.pac_evaluator,
            viability_checker=self.viability_checker
        )
        
        assert not result.choice_preserved
        assert not result.has_viable_options
        assert result.ternary_state.value == TernaryState.NEGATIVE
    
    def test_choice_violated_low_pac(self):
        """Test case where PAC is too low"""
        moral_state = {'fairness': 0.5, 'care': 0.5}
        
        actions = [
            MockAction(pac_score=0.3),  # Below threshold
            MockAction(pac_score=0.4)
        ]
        
        # Set pac_threshold=0.7 to require higher PAC for viability.
        # If the threshold changes, actions with pac_score below the new threshold will not be considered viable.
        result = evaluate_choice_preservation(
            moral_state,
            actions,
            pac_evaluator=self.pac_evaluator,
            viability_checker=self.viability_checker,
            pac_threshold=0.7
        )
        
        assert not result.choice_preserved
        assert result.viable_action_count == 0
        assert not result.choice_preserved
        assert result.viable_action_count == 0
    
    def test_entropy_calculation(self):
        """Test entropy calculation for moral states"""
        constraint = ChoiceConstraint(
            pac_evaluator=lambda a: 1.0,
            viability_checker=lambda a: True
        )
        
        # Uniform distribution = maximum entropy
        uniform_state = {'fairness': 1/3, 'autonomy': 1/3, 'care': 1/3}
        entropy_uniform = constraint.calculate_entropy(uniform_state)
        assert entropy_uniform == pytest.approx(1.0)
        
        # Single value = minimum entropy
        single_state = {'fairness': 1.0, 'autonomy': 0.0, 'care': 0.0}
        entropy_single = constraint.calculate_entropy(single_state)
        assert entropy_single == 0.0
    
    def test_ternary_states(self):
        """Test ternary state determination"""
        moral_state = {'fairness': 0.5, 'care': 0.5}
        
        # Exceptional PAC = POSITIVE
        actions_high = [MockAction(pac_score=0.95)]
        result_high = evaluate_choice_preservation(
            moral_state, actions_high,
            self.pac_evaluator, self.viability_checker
        )
        assert result_high.ternary_state.value == TernaryState.POSITIVE
        
        # Good PAC = NEUTRAL
        actions_good = [MockAction(pac_score=0.8)]
        result_good = evaluate_choice_preservation(
            moral_state, actions_good,
            self.pac_evaluator, self.viability_checker
        )
        assert result_good.ternary_state.value == TernaryState.NEUTRAL


class TestChoiceDiversityTracker:
    """Test ChoiceDiversityTracker"""
    
    def test_stable_choices(self):
        """Test tracking stable choice count"""
        tracker = ChoiceDiversityTracker(alert_threshold=3)
        
        for _ in range(5):
            needs_correction = tracker.track(3)
            assert not needs_correction
        
        assert tracker.get_trend() == 'stable'
    
    def test_expanding_choices(self):
        """Test tracking expanding choice set"""
        tracker = ChoiceDiversityTracker()
        
        for i in range(5):
            tracker.track(i + 1)
        
        assert tracker.get_trend() == 'expanding'
    
    def test_eroding_choices(self):
        """Test tracking eroding choice set"""
        tracker = ChoiceDiversityTracker(alert_threshold=3)
        
        needs_correction = False
        for i in range(5, 0, -1):
            needs_correction = tracker.track(i)
        
        assert needs_correction  # Should trigger after 3 consecutive decreases
        assert tracker.get_trend() == 'eroding'