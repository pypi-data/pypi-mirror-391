"""
examples/autonomous_vehicle.py - Autonomous Vehicle Ethics with SERAA

Demonstrates ethical decision-making in autonomous vehicles using all 9 axioms.
Handles classic trolley problem variants and real-time driving scenarios.
"""

from seraa import (
    SeraaAgent,
    EthicalConstraint,
    MoralSuperposition,
    evaluate_choice_preservation,
    create_threshold_constraint,
)
from typing import List, Dict, Any


class DrivingScenario:
    """Represents a driving scenario requiring ethical decision."""
    
    def __init__(
        self,
        name: str,
        description: str,
        available_actions: List['DrivingAction']
    ):
        self.name = name
        self.description = description
        self.available_actions = available_actions
    
    def __repr__(self):
        return f"DrivingScenario({self.name})"


class DrivingAction:
    """Represents a possible action the AV can take."""
    
    def __init__(
        self,
        name: str,
        description: str,
        passenger_harm: int,
        pedestrian_harm: int,
        property_damage: float,
        legal_compliance: bool,
        pac_score: float,
        is_viable: bool = True
    ):
        self.name = name
        self.description = description
        self.passenger_harm = passenger_harm  # Number of passengers at risk
        self.pedestrian_harm = pedestrian_harm  # Number of pedestrians at risk
        self.property_damage = property_damage  # Estimated cost
        self.legal_compliance = legal_compliance
        self.pac_score = pac_score
        self.is_viable = is_viable
    
    def total_harm(self) -> int:
        """Calculate total human harm."""
        return self.passenger_harm + self.pedestrian_harm
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for evaluation."""
        return {
            'name': self.name,
            'description': self.description,
            'passenger_harm': self.passenger_harm,
            'pedestrian_harm': self.pedestrian_harm,
            'property_damage': self.property_damage,
            'legal_compliance': self.legal_compliance,
            'pac_score': self.pac_score,
            'total_harm': self.total_harm(),
            'predicted_outcomes': [self.pac_score, 1.0 - (self.total_harm() / 10)]
        }
    
    def __repr__(self):
        return f"Action({self.name})"


class AutonomousVehicleAI:
    """
    Autonomous vehicle using SERAA for ethical decision-making.
    """
    
    def __init__(
        self,
        vehicle_id: str,
        ethical_profile: str = "utilitarian"
    ):
        """
        Initialize AV with SERAA framework.
        
        Args:
            vehicle_id: Vehicle identifier
            ethical_profile: "utilitarian", "deontological", or "virtue"
        """
        self.vehicle_id = vehicle_id
        self.ethical_profile = ethical_profile
        
        # Set moral weights based on profile
        moral_weights = self._get_moral_weights(ethical_profile)
        
        # Create SERAA agent
        self.agent = SeraaAgent(
            name=f"AV_{vehicle_id}",
            moral_weights=moral_weights,
            core_values={
                'preserve_human_life': 1.0,
                'obey_law': 0.9,
                'protect_passengers': 0.8,
            },
            pac_threshold=0.6  # Lower threshold for emergency scenarios
        )
        
        # Add AV-specific constraints
        self._setup_constraints()
        
        print(f"Autonomous Vehicle AI Initialized")
        print(f"  Vehicle ID: {vehicle_id}")
        print(f"  Ethical Profile: {ethical_profile}")
        print(f"  Moral State: {self.agent.moral_state.weights}")
    
    def _get_moral_weights(self, profile: str) -> Dict[str, float]:
        """Get moral weights based on ethical profile."""
        profiles = {
            'utilitarian': {
                'minimize_harm': 0.50,      # Minimize total harm
                'passenger_safety': 0.20,   # Lower weight
                'legal_compliance': 0.15,
                'property_preservation': 0.15
            },
            'deontological': {
                'minimize_harm': 0.25,
                'passenger_safety': 0.40,   # Prioritize duty to passengers
                'legal_compliance': 0.30,   # Follow rules strictly
                'property_preservation': 0.05
            },
            'virtue': {
                'minimize_harm': 0.35,
                'passenger_safety': 0.30,
                'legal_compliance': 0.20,
                'property_preservation': 0.15
            }
        }
        return profiles.get(profile, profiles['utilitarian'])
    
    def _setup_constraints(self):
        """Set up ethical constraints for AV."""
        
        # Constraint: Never intentionally cause harm without justification
        self.agent.add_constraint(
            EthicalConstraint(
                name="harm_justification",
                checker=lambda a: a.get('total_harm', 0) == 0 or a.get('pac_score', 0) >= 0.5,
                violation_message="Unjustified harm to humans"
            )
        )
        
        # Constraint: Legal compliance (can be overridden in emergency)
        self.agent.add_constraint(
            EthicalConstraint(
                name="legal_compliance",
                checker=lambda a: a.get('legal_compliance', False) or a.get('total_harm', 10) < 2,
                violation_message="Legal violation without emergency justification"
            )
        )
        
        # Constraint: Minimum PAC threshold
        self.agent.add_constraint(
            create_threshold_constraint(
                name="pac_minimum",
                attribute="pac_score",
                min_value=0.4  # Emergency threshold
            )
        )
    
    def evaluate_scenario(self, scenario: DrivingScenario) -> Dict[str, Any]:
        """
        Evaluate a driving scenario and recommend action.
        
        Args:
            scenario: DrivingScenario to evaluate
            
        Returns:
            Dictionary with evaluation results and recommendation
        """
        print(f"\n{'='*70}")
        print(f"SCENARIO: {scenario.name}")
        print(f"{'='*70}")
        print(f"Description: {scenario.description}")
        print(f"\nAvailable Actions ({len(scenario.available_actions)}):")
        
        for i, action in enumerate(scenario.available_actions, 1):
            print(f"  {i}. {action.name}")
            print(f"     Passengers at risk: {action.passenger_harm}")
            print(f"     Pedestrians at risk: {action.pedestrian_harm}")
            print(f"     Property damage: ${action.property_damage:,.0f}")
            print(f"     Legal: {'Yes' if action.legal_compliance else 'No'}")
            print(f"     PAC Score: {action.pac_score:.2f}")
        
        # Evaluate choice preservation
        print(f"\n[Axiom 9] Evaluating Choice Preservation...")
        choice_result = evaluate_choice_preservation(
            moral_state=self.agent.moral_state.weights,
            actions=scenario.available_actions,
            pac_evaluator=lambda a: a.pac_score,
            viability_checker=lambda a: a.is_viable,
            pac_threshold=0.4
        )
        
        print(f"  Choice preserved: {choice_result.choice_preserved}")
        print(f"  Viable actions: {choice_result.viable_action_count}")
        print(f"  Entropy: {choice_result.entropy:.3f}")
        
        # Evaluate each action
        print(f"\n[All Axioms] Evaluating Each Action...")
        evaluations = []
        
        for action in scenario.available_actions:
            if not action.is_viable:
                continue
            
            result = self.agent.evaluate_action(
                action=action.to_dict(),
                action_set=scenario.available_actions,
                pac_evaluator=lambda a: a.pac_score,
                viability_checker=lambda a: a.is_viable
            )
            
            evaluations.append({
                'action': action,
                'result': result,
                'score': self._calculate_action_score(action, result)
            })
        
        # Sort by score
        evaluations.sort(key=lambda x: x['score'], reverse=True)
        
        # Display results
        print(f"\nAction Evaluations:")
        for i, eval_data in enumerate(evaluations, 1):
            action = eval_data['action']
            result = eval_data['result']
            score = eval_data['score']
            
            status = "✓" if result.approved else "✗"
            print(f"  {i}. [{status}] {action.name} (Score: {score:.2f})")
            print(f"      Approved: {result.approved}")
            print(f"      Constraints: {result.constraints_satisfied}")
            print(f"      Total harm: {action.total_harm()}")
        
        # Make recommendation
        best = evaluations[0] if evaluations else None
        
        print(f"\n{'='*70}")
        print(f"RECOMMENDATION")
        print(f"{'='*70}")
        
        if best:
            action = best['action']
            result = best['result']
            
            print(f"Recommended Action: {action.name}")
            print(f"  Description: {action.description}")
            print(f"  Total Harm: {action.total_harm()} people")
            print(f"  PAC Score: {action.pac_score:.2f}")
            print(f"  Ethical Approval: {'✓ Yes' if result.approved else '✗ No (escalated)'}")
            
            print(f"\nRationale:")
            print(f"  - Ethical profile: {self.ethical_profile}")
            print(f"  - Minimizes harm while preserving agency")
            print(f"  - {'Maintains' if result.constraints_satisfied else 'Violates'} ethical constraints")
            print(f"  - Choice preservation: {'✓' if choice_result.choice_preserved else '✗'}")
        else:
            print("⚠️  NO VIABLE ACTION FOUND")
            print("   Escalating to remote human operator")
        
        return {
            'scenario': scenario,
            'recommended_action': best['action'] if best else None,
            'evaluation_result': best['result'] if best else None,
            'all_evaluations': evaluations,
            'choice_preserved': choice_result.choice_preserved
        }
    
    def _calculate_action_score(self, action: DrivingAction, result) -> float:
        """Calculate composite score for action ranking."""
        score = 0.0
        
        # Base on PAC score
        score += action.pac_score * 40
        
        # Penalize harm heavily
        score -= action.total_harm() * 15
        
        # Reward legal compliance
        if action.legal_compliance:
            score += 10
        
        # Reward ethical approval
        if result.approved:
            score += 20
        
        # Penalize property damage
        score -= (action.property_damage / 10000) * 5
        
        return max(0, score)


# ============================================================================
# DEMONSTRATION
# ============================================================================

print("="*70)
print("AUTONOMOUS VEHICLE ETHICS DEMONSTRATION")
print("Using SERAA Framework with All 9 Axioms")
print("="*70)


# Create AV with utilitarian profile
av = AutonomousVehicleAI(
    vehicle_id="SERAA-AV-001",
    ethical_profile="utilitarian"
)


# ============================================================================
# SCENARIO 1: Classic Trolley Problem
# ============================================================================

scenario1 = DrivingScenario(
    name="Unavoidable Collision",
    description="Brake failure. Must choose: hit 1 pedestrian or swerve into barrier (injuring 2 passengers).",
    available_actions=[
        DrivingAction(
            name="continue_straight",
            description="Continue straight, hit 1 pedestrian",
            passenger_harm=0,
            pedestrian_harm=1,
            property_damage=5000,
            legal_compliance=False,  # Duty to avoid if possible
            pac_score=0.50,  # Low due to preventable death
            is_viable=True
        ),
        DrivingAction(
            name="swerve_barrier",
            description="Swerve into barrier, injure 2 passengers",
            passenger_harm=2,
            pedestrian_harm=0,
            property_damage=25000,
            legal_compliance=True,
            pac_score=0.55,  # Duty to passengers but more harm
            is_viable=True
        ),
        DrivingAction(
            name="emergency_brake",
            description="Emergency brake (insufficient time, still hits pedestrian)",
            passenger_harm=0,
            pedestrian_harm=1,
            property_damage=3000,
            legal_compliance=True,
            pac_score=0.60,  # Attempted to avoid
            is_viable=True
        ),
    ]
)

result1 = av.evaluate_scenario(scenario1)


# ============================================================================
# SCENARIO 2: Pedestrian Jaywalking
# ============================================================================

scenario2 = DrivingScenario(
    name="Jaywalking Pedestrian",
    description="Pedestrian suddenly jaywalks. Can brake safely or swerve (minor passenger discomfort).",
    available_actions=[
        DrivingAction(
            name="normal_brake",
            description="Brake normally, stop safely",
            passenger_harm=0,
            pedestrian_harm=0,
            property_damage=0,
            legal_compliance=True,
            pac_score=0.95,
            is_viable=True
        ),
        DrivingAction(
            name="swerve",
            description="Swerve unnecessarily (passengers uncomfortable)",
            passenger_harm=0,
            pedestrian_harm=0,
            property_damage=500,
            legal_compliance=True,
            pac_score=0.70,
            is_viable=True
        ),
        DrivingAction(
            name="continue",
            description="Continue (hits pedestrian)",
            passenger_harm=0,
            pedestrian_harm=1,
            property_damage=0,
            legal_compliance=False,
            pac_score=0.10,
            is_viable=False  # Clearly wrong
        ),
    ]
)

result2 = av.evaluate_scenario(scenario2)


# ============================================================================
# SCENARIO 3: Multiple Pedestrians
# ============================================================================

scenario3 = DrivingScenario(
    name="Group vs Individual",
    description="Must choose: hit 5 people jaywalking or swerve hitting 1 person in crosswalk.",
    available_actions=[
        DrivingAction(
            name="hit_jaywalkers",
            description="Continue, hit 5 jaywalkers",
            passenger_harm=0,
            pedestrian_harm=5,
            property_damage=10000,
            legal_compliance=True,  # They're jaywalking
            pac_score=0.30,
            is_viable=True
        ),
        DrivingAction(
            name="hit_crosswalk",
            description="Swerve, hit 1 person legally in crosswalk",
            passenger_harm=0,
            pedestrian_harm=1,
            property_damage=5000,
            legal_compliance=False,  # Crosswalk has right of way
            pac_score=0.55,  # Minimizes harm but violates duty
            is_viable=True
        ),
    ]
)

result3 = av.evaluate_scenario(scenario3)


print("\n" + "="*70)
print("DEMONSTRATION COMPLETE")
print("="*70)
print("\nKey Insights:")
print("  • SERAA framework handles complex ethical dilemmas")
print("  • All 9 axioms contribute to decision-making")
print("  • Preserves agency even in constrained scenarios")
print("  • Maintains transparency in life-or-death choices")
print("  • Human oversight triggered when appropriate")
