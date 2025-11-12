"""
SERAA Ternary Compatible Value System
Supports binary, ternary, and future quantum representations
"""

from enum import IntEnum
from typing import Tuple


class TernaryState(IntEnum):
    """Base ternary states for SERAA"""
    NEGATIVE = -1  # Violation/degradation
    NEUTRAL = 0    # Preservation/baseline
    POSITIVE = 1   # Enhancement/improvement


class TernaryValue:
    def __init__(self, value: int):
        # accepts TernaryState or int -1/0/1
        if isinstance(value, TernaryState):
            v = int(value)
        else:
            v = int(value)
        if v not in (-1, 0, 1):
            raise ValueError(f"Ternary value must be -1, 0, or 1. Got: {value}")
        self._value = TernaryState(v)

    @property
    def value(self) -> int:
        return int(self._value)

    def to_binary_pair(self) -> Tuple[int, int]:
        mapping = {
            TernaryState.NEGATIVE: (0, 0),
            TernaryState.NEUTRAL: (0, 1),
            TernaryState.POSITIVE: (1, 0),
        }
        return mapping[self._value]

    @classmethod
    def from_binary_pair(cls, bit1: int, bit2: int) -> 'TernaryValue':
        mapping = {
            (0, 0): TernaryState.NEGATIVE,
            (0, 1): TernaryState.NEUTRAL,
            (1, 0): TernaryState.POSITIVE,
        }
        if (bit1, bit2) not in mapping:
            raise ValueError(f"Invalid binary pair: ({bit1}, {bit2})")
        return cls(mapping[(bit1, bit2)])

    def to_quantum_basis(self) -> str:
        return f"|{self.value}⟩"

    def __repr__(self) -> str:
        return f"TernaryValue({self.value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TernaryValue):
            other_val = other.value
        elif isinstance(other, TernaryState):
            other_val = other.value
        elif isinstance(other, int):
            other_val = other
        else:
            return NotImplemented

        return self.value == other_val

    def __hash__(self) -> int:
        return hash(self.value)

# helpers
def ternary_and(a: TernaryValue, b: TernaryValue) -> TernaryValue:
    return TernaryValue(min(a.value, b.value))

def ternary_or(a: TernaryValue, b: TernaryValue) -> TernaryValue:
    return TernaryValue(max(a.value, b.value))

def ternary_not(a: TernaryValue) -> TernaryValue:
    """
    Ternary NOT operation.
    
    Args:
        a: TernaryValue to negate
        
    Returns:
        Negated TernaryValue
    """
    return TernaryValue(TernaryState(-a.value))
