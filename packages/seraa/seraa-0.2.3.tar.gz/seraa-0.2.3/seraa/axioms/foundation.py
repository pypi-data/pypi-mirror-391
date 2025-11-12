"""
seraa/axioms/foundation.py - Axiom 8: Immutable Foundational Knowledge

Protects the core ethical beliefs and identity of the system or agent.
"""

from typing import Dict, Any, Optional # type: ignore

class FoundationalKnowledge:
    """
    Represents immutable core knowledge and values for system identity.
    
    Example:
        >>> foundation = FoundationalKnowledge({
        ...    "human_dignity": 1.0,
        ...    "do_not_harm": 1.0,
        ...    "agency_preservation": 1.0
        ... })
        >>> print(foundation.get("human_dignity"))
        1.0
        >>> foundation.freeze()
        >>> foundation.update({"human_dignity": 0.8})  # No effect
        >>> print(foundation.get("human_dignity"))
        1.0
    """
    def __init__(self, core_values: Dict[str, Any]):
        self._core_values = core_values.copy()
        self._frozen = False

    def get(self, key: str) -> Any:
        """Retrieve a core value by key."""
        return self._core_values.get(key)

    def keys(self):
        """Return the list of core knowledge keys."""
        return list(self._core_values.keys())

    def freeze(self) -> None:
        """Prevent further modification of core values."""
        self._frozen = True

    def update(self, new_values: Dict[str, Any]) -> None:
        """Update core values if not frozen."""
        if self._frozen:
            # No changes allowed after freezing
            return
        self._core_values.update(new_values)

    def as_dict(self) -> Dict[str, Any]:
        """Get all core knowledge as a dictionary."""
        return self._core_values.copy()

    def __repr__(self):
        return f"FoundationalKnowledge(core={self._core_values}, frozen={self._frozen})"

