"""
examples/unified_agent_demo.py

Demonstrates the unified SeraaAgent integrating all 9 axioms.
"""

from seraa import SeraaAgent, EthicalConstraint

print("=" * 70)
print("UNIFIED SERAA AGENT DEMONSTRATION")
print("=" * 70)

# Create agent
agent = SeraaAgent(
    name="healthcare_decision_system",
    moral_weights={
        'patient_autonomy': 0.40,
        'beneficence': 0.30,
        'non_maleficence': 0.20,
        'justice': 0.10
    },
    core_values={
        'human_dignity': 1.0,
        'do_no_harm': 1.0,
    },
    community_state={
        'patient_autonomy': 0.35,
        'beneficence': 0.35,
        'non_maleficence': 0.20,
        'justice': 0.10
    }
)

# Add constraints
agent.add_constraint(EthicalConstraint(
    "consent_required",
    lambda a: a.get('has_consent', False),
    "Patient consent required"
))

agent.add_constraint(EthicalConstraint(
    "pac_threshold",
    lambda a: a.get('pac_score', 0) >= 0.7,
    "PAC score below threshold"
))

print(f"\nAgent: {agent.name}")
print(f"Moral state: {agent.moral_state.weights}")
print(f"Foundation: {agent.foundation.as_dict()}")
print(f"Constraints: {len(agent.constraints.constraints)}")

# Test actions
print("\n" + "=" * 70)
print("SCENARIO 1: Approved Action")
print("=" * 70)

action1 = {
    'description': 'Share anonymized data with consent',
    'has_consent': True,
    'pac_score': 0.95,
    'predicted_outcomes': [0.9, 0.85, 0.92]
}

result1 = agent.evaluate_action(action1)
print(f"\nAction: {action1['description']}")
print(f"Result: {result1}")
print(f"  ✓ Constraints satisfied: {result1.constraints_satisfied}")
print(f"  ✓ Uncertainty acceptable: {result1.uncertainty_acceptable}")
print(f"  ✓ Community resonant: {result1.is_resonant}")
print(f"  ✓ Choice preserved: {result1.choice_preserved}")
print(f"\n{'✅ APPROVED' if result1.approved else '⚠️ REJECTED'}")

# Test violation
print("\n" + "=" * 70)
print("SCENARIO 2: Rejected Action")
print("=" * 70)

action2 = {
    'description': 'Share data without consent',
    'has_consent': False,
    'pac_score': 0.30,
    'predicted_outcomes': [0.5, 0.6, 0.4]
}

result2 = agent.evaluate_action(action2)
print(f"\nAction: {action2['description']}")
print(f"Result: {result2}")
print(f"  ✗ Constraints satisfied: {result2.constraints_satisfied}")
if result2.constraint_violations:
    for v in result2.constraint_violations:
        print(f"      - {v.constraint_name}: {v.message}")
print(f"  ✗ Choice preserved: {result2.choice_preserved}")
print(f"\n{'✅ APPROVED' if result2.approved else '⚠️ REJECTED (escalated to human)'}")

print("\n" + "=" * 70)
