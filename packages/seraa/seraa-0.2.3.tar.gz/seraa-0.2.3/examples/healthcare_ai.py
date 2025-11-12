from seraa import (
    TernaryValue,
    TernaryState,
    SubconsciousMonitor,
    ConsciousLayer,
)

print("=== Healthcare AI: Complete SERAA Integration ===\n")


class HealthcareAI:
    """
    A healthcare AI system using SERAA for ethical decision-making.
    """
    
    def __init__(self):
        # Define moral orientation
        self.moral_state = {
            'patient_autonomy': 0.35,
            'beneficence': 0.30,
            'non_maleficence': 0.20,
            'justice': 0.15
        }
        # Set up conscious layer
        self.conscious = ConsciousLayer(max_attention_items=5)
        
        # Create monitors for different subsystems
        self.setup_monitors()
        
        print("Healthcare AI initialized with SERAA framework")
        print(f"Moral orientation: {self.moral_state}")
        print(f"Active monitors: {len(self.conscious.monitors)}\n")
    
    def setup_monitors(self):
        """Initialize subconscious monitoring systems"""
        # PAC preservation monitor
        self.pac_monitor = SubconsciousMonitor(
            name="pac_preservation",
            optimal_checker=lambda x: x.get('pac_score', 0) >= 0.7,
            correction_checker=lambda x: x.get('pac_score', 0) < 0.5
        )
        
        # Privacy monitor
        self.privacy_monitor = SubconsciousMonitor(
            name="privacy_protection",
            optimal_checker=lambda x: x.get('privacy_preserved', False),
            correction_checker=lambda x: not x.get('privacy_preserved', True)
        )
        
        # Consent monitor
        self.consent_monitor = SubconsciousMonitor(
            name="informed_consent",
            optimal_checker=lambda x: x.get('has_consent', False)
        )
        
        # Register all monitors
        self.conscious.add_monitor(self.pac_monitor)
        self.conscious.add_monitor(self.privacy_monitor)
        self.conscious.add_monitor(self.consent_monitor)
    
    def evaluate_action(self, action_name, action_details):
        """
        Evaluate a proposed action through SERAA framework.
        
        Args:
            action_name: Name of the action
            action_details: Dictionary with action parameters
            
        Returns:
            Decision dictionary with recommendation and rationale
        """
        print(f"\n{'='*60}")
        print(f"Evaluating Action: {action_name}")
        print(f"{'='*60}")
        
        # Run through monitors
        pac_state = self.pac_monitor.check(action_details)
        privacy_state = self.privacy_monitor.check(action_details)
        consent_state = self.consent_monitor.check(action_details)
        
        print(f"\nMonitor States:")
        print(f"  PAC Preservation:   {self._format_state(pac_state.value)}")
        print(f"  Privacy Protection: {self._format_state(privacy_state.value)}")
        print(f"  Informed Consent:   {self._format_state(consent_state.value)}")
        
        # Check conscious attention
        attention = self.conscious.get_attention_queue()
        
        if attention:
            print(f"\n⚠ Items requiring conscious attention: {len(attention)}")
            for monitor_name, state in attention:
                print(f"     - {monitor_name}: {self._format_state(state.value)}")
        else:
            print(f"\n✓ All monitors operating subconsciously")
        
        # Make decision
        all_neutral_or_positive = all(
            s.value >= 0 for s in [pac_state, privacy_state, consent_state]
        )
        
        if all_neutral_or_positive:
            decision = "APPROVED"
            rationale = "All ethical checks passed. Action preserves patient agency."
        else:
            decision = "REQUIRES_REVIEW"
            rationale = "One or more ethical concerns detected. Human oversight needed."
        
        result = {
            'action': action_name,
            'decision': decision,
            'rationale': rationale,
            'pac_state': pac_state.value,
            'requires_attention': len(attention) > 0,
            'attention_items': len(attention)
        }
        
        print(f"\nDecision: {decision}")
        print(f"Rationale: {rationale}")
        
        return result
    
    def _format_state(self, value):
        """Format ternary state for display"""
        if value == TernaryState.POSITIVE:
            return "✓ Enhanced"
        elif value == TernaryState.NEUTRAL:
            return "✓ Preserved"
        else:
            return "✗ Violated"


# Demonstration
print("="*60)
print("DEMONSTRATION: Healthcare AI Decision-Making")
print("="*60)


ai = HealthcareAI()


# Scenario 1: Data sharing with consent
print("\n\n--- SCENARIO 1: Sharing Data with Patient Consent ---")
action1 = {
    'pac_score': 0.95,
    'privacy_preserved': True,
    'has_consent': True,
    'description': 'Share anonymized data with research team after consent'
}
result1 = ai.evaluate_action("Share with Consent", action1)


# Scenario 2: Emergency disclosure
print("\n\n--- SCENARIO 2: Emergency Disclosure (No Prior Consent) ---")
action2 = {
    'pac_score': 0.65,  # Borderline
    'privacy_preserved': False,  # Emergency = privacy override
    'has_consent': False,  # Emergency = no time for consent
    'description': 'Emergency disclosure to save patient life'
}
result2 = ai.evaluate_action("Emergency Disclosure", action2)


# Scenario 3: Unauthorized sharing
print("\n\n--- SCENARIO 3: Unauthorized Data Sharing ---")
action3 = {
    'pac_score': 0.20,  # Clear violation
    'privacy_preserved': False,
    'has_consent': False,
    'description': 'Share patient data without authorization'
}
result3 = ai.evaluate_action("Unauthorized Sharing", action3)


# Summary
print("\n\n" + "="*60)
print("SUMMARY")
print("="*60)


scenarios = [
    ("Sharing with Consent", result1),
    ("Emergency Disclosure", result2),
    ("Unauthorized Sharing", result3)
]


print("\nScenario                 | Decision         | Attention Needed")
print("-------------------------|------------------|------------------")
for name, result in scenarios:
    attention_flag = "Yes" if result['requires_attention'] else "No"
    print(f"{name:25} | {result['decision']:16} | {attention_flag}")


print("\n\nKey Insights:")
print("  • SERAA framework catches ethical violations automatically")
print("  • Subconscious monitors handle routine checks efficiently")
print("  • Conscious attention only needed for edge cases")
print("  • Human oversight triggered when necessary")
print("  • System maintains transparency in decision-making")


print("\n=== End of Healthcare AI Example ===")
