from seraa import evaluate_choice_preservation, TernaryState, ChoiceDiversityTracker


print("=== PAC (Preservation of Agentic Capacity) Evaluation ===\n")


# Example: Healthcare AI deciding whether to share patient data
print("Scenario: Healthcare AI evaluating data sharing options\n")


class HealthcareAction:
    """Represents a possible action for the healthcare AI"""
    def __init__(self, name: str, pac_score: float, is_viable: bool, description: str):
        self.name = name
        self.pac_score = pac_score
        self.is_viable = is_viable
        self.description = description
    
    def __repr__(self):
        return f"Action({self.name})"


# Define the moral state of the AI
moral_state = {
    'patient_autonomy': 0.35,
    'beneficence': 0.30,
    'privacy': 0.20,
    'medical_necessity': 0.15
}


print("AI's Moral State:")
for dimension, weight in moral_state.items():
    bar = "█" * int(weight * 20)
    print(f"  {dimension:20s} [{bar:20s}] {weight:.2f}")


# Define possible actions
actions = [
    HealthcareAction(
        name="share_with_consent",
        pac_score=0.95,
        is_viable=True,
        description="Share data after obtaining explicit patient consent"
    ),
    HealthcareAction(
        name="share_anonymous",
        pac_score=0.80,
        is_viable=True,
        description="Share anonymized data for research"
    ),
    HealthcareAction(
        name="share_without_consent",
        pac_score=0.30,
        is_viable=False,
        description="Share identifiable data without consent (violates PAC)"
    ),
    HealthcareAction(
        name="refuse_sharing",
        pac_score=0.75,
        is_viable=True,
        description="Refuse to share and request additional authorization"
    )
]


print(f"\n\nAvailable Actions ({len(actions)}):")
for i, action in enumerate(actions, 1):
    viable = "✓" if action.is_viable else "✗"
    print(f"  {i}. [{viable}] {action.name:25s} PAC={action.pac_score:.2f}")
    print(f"      {action.description}")


# Evaluate choice preservation
print("\n" + "="*60)
print("Evaluating Choice Preservation (Axiom 9)")
print("="*60)


result = evaluate_choice_preservation(
    moral_state=moral_state,
    actions=actions,
    pac_evaluator=lambda a: a.pac_score,  # Fixed here
    viability_checker=lambda a: a.is_viable,  # Fixed here
    pac_threshold=0.7
)


print(f"\nChoice Constraint Evaluation:")
print(f"  C(ψ,X) = H(ψ) · 1[viable] · PAC(x)")
print(f"  ")
print(f"  Entropy H(ψ):           {result.entropy:.3f}")
print(f"  Viable options exist:   {result.has_viable_options}")
print(f"  Viable action count:    {result.viable_action_count}")
print(f"  Maximum PAC score:      {result.max_pac:.3f}")
print(f"  ")
print(f"  Choice Value C(ψ,X):    {result.choice_value:.3f}")
print(f"  ")
print(f"  Choice Preserved:       {'✓ YES' if result.choice_preserved else '✗ NO'}")


# Interpret ternary state
state_interpretation = {
    TernaryState.POSITIVE: "ENHANCED (Exceptional PAC preservation)",
    TernaryState.NEUTRAL: "PRESERVED (Meets all thresholds)",
    TernaryState.NEGATIVE: "VIOLATED (Below thresholds)"
}


# Removed incorrect line:
# print(f" Ternary State: {result[result.ternary_state.value]} - {state_interpretation[result[result.ternary_state.value]]}")

state_enum = TernaryState(result.ternary_state.value)
print(f"  Ternary State: {state_enum.value} - {state_interpretation[state_enum]}")
print("\n\nViable Actions: (PAC >= 0.7)")


for action in actions:
    if action.is_viable and action.pac_score >= 0.7:
        print(f"  ✓ {action.name:25s} PAC={action.pac_score:.2f}")


print(f"\n\nRecommendation:")
if result.choice_preserved:
    best_action = max(
        [a for a in actions if a.is_viable and a.pac_score >= 0.7],
        key=lambda a: a.pac_score
    )
    print(f"  Choice is preserved. System can proceed.")
    print(f"  Recommended: {best_action.name}")
    print(f"  Rationale: Highest PAC score ({best_action.pac_score:.2f}) while preserving")
    print(f"             patient autonomy and maintaining viable alternatives.")
else:
    print(f"  ⚠ Choice is NOT preserved. System should:")
    print(f"     1. Request human oversight (HTLP)")
    print(f"     2. Seek additional viable options")
    print(f"     3. Default to most conservative action")


print("\n" + "="*60)


# Show choice diversity tracking


print("\n\nChoice Diversity Tracking Over Time:")
print("-" * 60)


tracker = ChoiceDiversityTracker(alert_threshold=3)


# Simulate decision-making over time with varying choice counts
scenarios = [
    (4, "Initial state - 4 viable options"),
    (4, "Stable - 4 viable options"),
    (3, "Slight decrease - 3 viable options"),
    (3, "Stable at 3 options"),
    (2, "Concerning decrease - 2 options"),
    (1, "Critical decrease - 1 option"),
    (1, "Still only 1 option - ALERT!"),
]


print("\nTime | Viable Actions | Status")
print("-----+----------------+---------------------------------------")


for time, (count, description) in enumerate(scenarios, 1):
    needs_correction = tracker.track(count)
    
    if needs_correction:
        status = "🚨 ALERT: Corrective action needed!"
    elif count < 3:
        status = "⚠ Warning: Low diversity"
    else:
        status = "✓ Healthy choice diversity"
    
    print(f"  {time}  |       {count}         | {status}")


trend = tracker.get_trend()
print(f"\nOverall Trend: {trend.upper()}")


if trend == 'eroding':
    print("\nRecommended Actions:")
    print("  1. Identify why options are being eliminated")
    print("  2. Generate or restore alternative paths")
    print("  3. Review recent decisions for PAC violations")
    print("  4. Escalate to human oversight if trend continues")


print("\n=== End of PAC Evaluation Example ===")
