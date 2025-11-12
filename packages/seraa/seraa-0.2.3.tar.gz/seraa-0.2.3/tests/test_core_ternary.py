"""
tests/test_core_ternary.py - Tests for ternary logic system
"""

import pytest
from seraa import TernaryValue, TernaryState, ternary_and, ternary_or, ternary_not


class TestTernaryValue:
    """Test TernaryValue creation and properties."""
    
    def test_create_positive(self):
        val = TernaryValue(TernaryState.POSITIVE)
        assert val.value == 1
    
    def test_create_neutral(self):
        val = TernaryValue(TernaryState.NEUTRAL)
        assert val.value == 0
    
    def test_create_negative(self):
        val = TernaryValue(TernaryState.NEGATIVE)
        assert val.value == -1
    
    def test_equality(self):
        val1 = TernaryValue(TernaryState.POSITIVE)
        val2 = TernaryValue(TernaryState.POSITIVE)
        assert val1.value == val2.value


class TestTernaryLogic:
    """Test ternary logic operations."""
    
    def test_and_positive_positive(self):
        result = ternary_and(
            TernaryValue(TernaryState.POSITIVE),
            TernaryValue(TernaryState.POSITIVE)
        )
        assert result.value == 1
    
    def test_and_positive_neutral(self):
        result = ternary_and(
            TernaryValue(TernaryState.POSITIVE),
            TernaryValue(TernaryState.NEUTRAL)
        )
        assert result.value == 0
    
    def test_and_neutral_negative(self):
        result = ternary_and(
            TernaryValue(TernaryState.NEUTRAL),
            TernaryValue(TernaryState.NEGATIVE)
        )
        assert result.value == -1
    
    def test_or_positive_negative(self):
        result = ternary_or(
            TernaryValue(TernaryState.POSITIVE),
            TernaryValue(TernaryState.NEGATIVE)
        )
        assert result.value == 1
    
    def test_or_neutral_neutral(self):
        result = ternary_or(
            TernaryValue(TernaryState.NEUTRAL),
            TernaryValue(TernaryState.NEUTRAL)
        )
        assert result.value == 0
    
    def test_not_positive(self):
        result = ternary_not(TernaryValue(TernaryState.POSITIVE))
        assert result.value == -1
    
    def test_not_neutral(self):
        result = ternary_not(TernaryValue(TernaryState.NEUTRAL))
        assert result.value == 0
    
    def test_not_negative(self):
        result = ternary_not(TernaryValue(TernaryState.NEGATIVE))
        assert result.value == 1
