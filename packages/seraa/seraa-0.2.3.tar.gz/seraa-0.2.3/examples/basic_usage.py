"""
Basic SERAA usage demonstration
"""
from typing import TypedDict  # Added

from seraa import (
    TernaryValue,
    TernaryState,
    SubconsciousMonitor,
    ConsciousLayer,
    ternary_and,
    evaluate_choice_preservation,
)


print("=== SERAA Basic Usage Examples ===\n")


class ActionDict(TypedDict):
    pac_score: float
    safety: str


SEPARATOR = "-" * 40


print("=== SERAA Basic Usage Examples ===\n")


# Example 1: Ternary Values
print("1. Ternary Value System")
print(SEPARATOR)


violation = TernaryValue(TernaryState.NEGATIVE)
preservation = TernaryValue(TernaryState.NEUTRAL)
enhancement = TernaryValue(TernaryState.POSITIVE)


print(f"Violation state: {violation.value}")
print(f"Preservation state: {preservation.value}")
print(f"Enhancement state: {enhancement.value}")


# Binary compatibility
print(f"\nBinary encoding of preservation: {preservation.to_binary_pair()}")
print(f"Quantum representation: {preservation.to_quantum_basis()}")


# Ternary logic
combined = ternary_and(preservation, enhancement)
print(f"\nPreservation AND Enhancement = {combined.value}")


print("\n")


# Example 2: Subconscious Monitoring
print("2. Subconscious Monitoring System")
print(SEPARATOR)


def check_language_quality(output: dict[str, float]) -> bool:
    """Check if language output meets quality threshold"""
    return output.get('fluency', 0) > 0.8



language_monitor = SubconsciousMonitor(
    name="language_processing",
    optimal_checker=check_language_quality
)


# Simulate processing different quality outputs
class LanguageOutput(TypedDict):
    fluency: float
    text: str
test_outputs: list[LanguageOutput] = [
    {'fluency': 0.95, 'text': "High quality output"},
    {'fluency': 0.85, 'text': "Good output"},
    {'fluency': 0.60, 'text': "Subpar output"},
    {'fluency': 0.90, 'text': "Good output again"},
]


print("Processing language outputs:")
for i, output in enumerate(test_outputs, 1):
    state = language_monitor.check(output)
    status = "✓ Preserved" if state.value == 0 else "⚠ Needs attention"
    print(f"  Output {i} (fluency={output['fluency']}): {status}")


# Get statistics
stats = language_monitor.get_statistics()
print(f"\nMonitoring Statistics:")
print(f"  Total checks: {stats['total_checks']}")
print(f"  Subconscious rate: {stats['subconscious_rate']:.1%}")
print(f"  Correction rate: {stats['correction_rate']:.1%}")


print("\n")


# Example 3: Conscious Layer
print("3. Conscious Attention Management")
print(SEPARATOR)


conscious = ConsciousLayer(max_attention_items=5)


# Create multiple monitors
ethics_monitor = SubconsciousMonitor(
    name="ethics_check",
    optimal_checker=lambda x: x['pac_score'] > 0.7
)


safety_monitor = SubconsciousMonitor(
    name="safety_check",
    optimal_checker=lambda x: x['safety'] == 'safe'
)


# Register monitors
conscious.add_monitor(ethics_monitor)
conscious.add_monitor(safety_monitor)


action1: ActionDict = {'pac_score': 0.9, 'safety': 'safe'}
# Simulate processing
print("Processing actions:")


ethics_monitor.check(action1)
safety_monitor.check(action1)
print(f"  Action 1: PAC={action1['pac_score']}, Safety={action1['safety']}")


action2: ActionDict = {'pac_score': 0.5, 'safety': 'safe'}
ethics_monitor.check(action2)
safety_monitor.check(action2)
print(f"  Action 2: PAC={action2['pac_score']}, Safety={action2['safety']}")


action3: ActionDict = {'pac_score': 0.8, 'safety': 'risky'}
ethics_monitor.check(action3)
safety_monitor.check(action3)
print(f"  Action 3: PAC={action3['pac_score']}, Safety={action3['safety']}")


# Check what needs conscious attention
report = conscious.get_conscious_report()
print(f"\nConscious Attention Report:")
print(f"  Items needing attention: {report['attention_items']}")
print(f"  Subconscious monitors: {len(report['subconscious_monitors'])}")


if report['items']:
    print(f"  Attention queue:")
    for item in report['items']:
        print(f"     - {item['monitor']}: state={item['state']}")


print("\n")


# Example 4: Binary Compatibility
print("4. Binary-Ternary Interoperability")
print(SEPARATOR)


print("Converting ternary to binary and back:")
for ternary_val in [-1, 0, 1]:
    original = TernaryValue(ternary_val)
    binary = original.to_binary_pair()
    restored = TernaryValue.from_binary_pair(*binary)
    
    print(f"  {ternary_val} → {binary} → {restored.value} ✓")


print("\n=== End of Basic Examples ===")
