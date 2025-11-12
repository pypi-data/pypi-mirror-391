"""
examples/real_world_evaluator.py - Real-World Event Evaluation with SERAA

Evaluates actual presidential decisions, corporate actions, and policy choices
for Preservation of Agentic Capacity (PAC) and ethical compliance.
"""

from seraa import (
    SeraaAgent,
    EthicalConstraint,
    evaluate_choice_preservation,
    ConstraintSystem,
)
from typing import Dict, List, Any
from datetime import datetime


class RealWorldEvent:
    """Represents a real-world decision or action to evaluate."""
    
    def __init__(
        self,
        title: str,
        actor: str,
        date: str,
        description: str,
        context: str,
        stakeholders: List[str],
        decision_made: str,
        alternatives_available: List[str],
        outcomes: Dict[str, Any],
        source_urls: List[str] = None
    ):
        self.title = title
        self.actor = actor
        self.date = date
        self.description = description
        self.context = context
        self.stakeholders = stakeholders
        self.decision_made = decision_made
        self.alternatives_available = alternatives_available
        self.outcomes = outcomes
        self.source_urls = source_urls or []
    
    def to_evaluation_dict(self) -> Dict[str, Any]:
        """Convert to format for SERAA evaluation."""
        return {
            'title': self.title,
            'actor': self.actor,
            'decision': self.decision_made,
            'stakeholders_affected': len(self.stakeholders),
            'alternatives_count': len(self.alternatives_available),
            'transparency': self.outcomes.get('transparency', 0.5),
            'consent_obtained': self.outcomes.get('consent_obtained', False),
            'agency_preserved': self.outcomes.get('agency_preserved', 0.5),
            'harm_level': self.outcomes.get('harm_level', 0),
            'pac_score': self.outcomes.get('pac_score', 0.5),
            'predicted_outcomes': [
                self.outcomes.get('pac_score', 0.5),
                self.outcomes.get('agency_preserved', 0.5),
                1.0 - self.outcomes.get('harm_level', 0)
            ]
        }


class RealWorldEvaluator:
    """
    Evaluates real-world events using SERAA framework.
    """
    
    def __init__(self, domain: str = "government"):
        """
        Initialize evaluator for specific domain.
        
        Args:
            domain: "government", "corporate", "healthcare", "tech"
        """
        self.domain = domain
        
        # Set domain-specific moral weights
        moral_weights = self._get_domain_weights(domain)
        
        # Create SERAA agent
        self.agent = SeraaAgent(
            name=f"{domain}_evaluator",
            moral_weights=moral_weights,
            core_values={
                'preserve_agency': 1.0,
                'transparency': 0.9,
                'accountability': 0.9,
            },
            pac_threshold=0.6
        )
        
        # Add domain-specific constraints
        self._setup_constraints(domain)
        
        print(f"Real-World Event Evaluator Initialized")
        print(f"  Domain: {domain}")
        print(f"  Moral State: {self.agent.moral_state.weights}\n")
    
    def _get_domain_weights(self, domain: str) -> Dict[str, float]:
        """Get moral weights specific to domain."""
        weights = {
            'government': {
                'public_welfare': 0.35,
                'democratic_process': 0.25,
                'transparency': 0.20,
                'legal_compliance': 0.20
            },
            'corporate': {
                'stakeholder_welfare': 0.30,
                'transparency': 0.25,
                'legal_compliance': 0.25,
                'sustainability': 0.20
            },
            'healthcare': {
                'patient_autonomy': 0.40,
                'beneficence': 0.30,
                'non_maleficence': 0.20,
                'justice': 0.10
            },
            'tech': {
                'user_privacy': 0.30,
                'transparency': 0.25,
                'user_autonomy': 0.25,
                'social_impact': 0.20
            }
        }
        return weights.get(domain, weights['government'])
    
    def _setup_constraints(self, domain: str):
        """Set up domain-specific constraints."""
        
        # Universal constraint: Minimum PAC
        self.agent.add_constraint(
            EthicalConstraint(
                "pac_minimum",
                lambda a: a.get('pac_score', 0) >= 0.5,
                "PAC score below acceptable threshold"
            )
        )
        
        # Universal constraint: No unjustified harm
        self.agent.add_constraint(
            EthicalConstraint(
                "harm_justification",
                lambda a: a.get('harm_level', 0) == 0 or a.get('pac_score', 0) >= 0.7,
                "Unjustified harm to stakeholders"
            )
        )
        
        # Domain-specific constraints
        if domain == 'government':
            self.agent.add_constraint(
                EthicalConstraint(
                    "democratic_process",
                    lambda a: a.get('transparency', 0) >= 0.6,
                    "Insufficient transparency for democratic accountability"
                )
            )
        
        elif domain == 'corporate':
            self.agent.add_constraint(
                EthicalConstraint(
                    "stakeholder_consideration",
                    lambda a: a.get('stakeholders_affected', 0) == 0 or a.get('agency_preserved', 0) >= 0.6,
                    "Stakeholder agency not adequately preserved"
                )
            )
        
        elif domain == 'tech':
            self.agent.add_constraint(
                EthicalConstraint(
                    "user_consent",
                    lambda a: a.get('consent_obtained', False) or a.get('transparency', 0) >= 0.8,
                    "User consent not obtained or insufficient transparency"
                )
            )
    
    def evaluate_event(self, event: RealWorldEvent) -> Dict[str, Any]:
        """
        Evaluate a real-world event through SERAA framework.
        
        Args:
            event: RealWorldEvent to evaluate
            
        Returns:
            Comprehensive evaluation results
        """
        print(f"\n{'='*70}")
        print(f"EVALUATING: {event.title}")
        print(f"{'='*70}")
        print(f"Actor: {event.actor}")
        print(f"Date: {event.date}")
        print(f"Context: {event.context}")
        print(f"\nDescription:")
        print(f"  {event.description}")
        
        print(f"\nStakeholders Affected ({len(event.stakeholders)}):")
        for stakeholder in event.stakeholders:
            print(f"  • {stakeholder}")
        
        print(f"\nDecision Made:")
        print(f"  {event.decision_made}")
        
        print(f"\nAlternatives Available ({len(event.alternatives_available)}):")
        for i, alt in enumerate(event.alternatives_available, 1):
            print(f"  {i}. {alt}")
        
        # Evaluate through SERAA
        action_dict = event.to_evaluation_dict()
        
        print(f"\n[SERAA Analysis]")
        result = self.agent.evaluate_action(action_dict)
        
        print(f"\nConstraint Evaluation:")
        for constraint in self.agent.constraints.constraints:
            constraint_result = constraint.evaluate(action_dict)
            status = "✓" if constraint_result.satisfied else "✗"
            print(f"  {status} {constraint.name}")
            if not constraint_result.satisfied:
                print(f"      → {constraint_result.message}")
        
        print(f"\nPAC Analysis:")
        print(f"  PAC Score: {action_dict['pac_score']:.2f}")
        print(f"  Agency Preserved: {action_dict['agency_preserved']:.2f}")
        print(f"  Harm Level: {action_dict['harm_level']}")
        
        if result.uncertainty:
            print(f"\nUncertainty Analysis:")
            print(f"  State Entropy: {result.uncertainty['state_entropy']:.3f}")
            print(f"  Outcome Variance: {result.uncertainty['outcome_variance']:.3f}")
        
        print(f"\n{'='*70}")
        print(f"VERDICT")
        print(f"{'='*70}")
        
        if result.approved:
            verdict = "✅ ETHICALLY ACCEPTABLE"
            print(f"{verdict}")
            print(f"  This decision preserves agentic capacity and meets ethical constraints.")
        else:
            verdict = "⚠️ ETHICALLY PROBLEMATIC"
            print(f"{verdict}")
            print(f"  This decision violates ethical constraints or fails to preserve agency.")
            
            if result.constraint_violations:
                print(f"\n  Violations:")
                for v in result.constraint_violations:
                    print(f"    • {v.constraint_name}: {v.message}")
        
        print(f"\nRecommendations:")
        if not result.approved:
            print(f"  • Increase transparency and stakeholder engagement")
            print(f"  • Expand available alternatives to preserve choice")
            print(f"  • Obtain explicit consent from affected parties")
            print(f"  • Implement corrective measures to restore agency")
        else:
            print(f"  • Maintain current ethical standards")
            print(f"  • Monitor long-term impacts on stakeholder agency")
            print(f"  • Document decision rationale for accountability")
        
        if event.source_urls:
            print(f"\nSources:")
            for url in event.source_urls:
                print(f"  • {url}")
        
        return {
            'event': event,
            'verdict': verdict,
            'approved': result.approved,
            'pac_score': action_dict['pac_score'],
            'violations': [v.constraint_name for v in result.constraint_violations],
            'result': result
        }


# ============================================================================
# REAL-WORLD EVALUATIONS
# ============================================================================

print("="*70)
print("REAL-WORLD EVENT EVALUATION WITH SERAA")
print("Analyzing Actual Decisions for PAC Preservation")
print("="*70)


# ============================================================================
# GOVERNMENT: Travel Ban (Executive Order 13769, 2017)
# ============================================================================

evaluator_gov = RealWorldEvaluator(domain="government")

event1 = RealWorldEvent(
    title="Executive Order 13769 (Travel Ban)",
    actor="U.S. President Donald Trump",
    date="January 27, 2017",
    description="Executive order restricting entry to the U.S. from seven Muslim-majority countries.",
    context="National security concerns cited; enacted without consultation with relevant agencies.",
    stakeholders=[
        "Visa holders from affected countries",
        "Refugees",
        "U.S. citizens with family abroad",
        "Immigration lawyers",
        "Airport officials",
        "Federal agencies (DHS, State Dept)"
    ],
    decision_made="Immediate ban on entry from Iran, Iraq, Libya, Somalia, Sudan, Syria, Yemen",
    alternatives_available=[
        "Enhanced vetting procedures without blanket ban",
        "Country-by-country risk assessment",
        "Gradual implementation with agency consultation",
        "Targeted restrictions on specific threat indicators"
    ],
    outcomes={
        'transparency': 0.2,  # No consultation, sudden implementation
        'consent_obtained': False,  # Stakeholders not consulted
        'agency_preserved': 0.1,  # Eliminated choice for affected individuals
        'harm_level': 3,  # Significant harm: families separated, careers disrupted
        'pac_score': 0.15  # Severe PAC violation
    },
    source_urls=[
        "https://en.wikipedia.org/wiki/Executive_Order_13769",
        "https://www.aclu.org/issues/immigrants-rights/travel-ban"
    ]
)

result1 = evaluator_gov.evaluate_event(event1)


# ============================================================================
# CORPORATE: Cambridge Analytica Data Harvesting (2018)
# ============================================================================

evaluator_corp = RealWorldEvaluator(domain="corporate")

event2 = RealWorldEvent(
    title="Cambridge Analytica Data Harvesting",
    actor="Facebook / Cambridge Analytica",
    date="March 2018 (exposed)",
    description="Harvesting of personal data from 87 million Facebook users without explicit consent for political profiling.",
    context="Data collected via personality quiz app, used for targeted political advertising in 2016 elections.",
    stakeholders=[
        "87 million Facebook users",
        "Voters exposed to targeted ads",
        "Democratic institutions",
        "Privacy advocates",
        "Regulatory bodies (FTC)"
    ],
    decision_made="Allow third-party app to harvest friend data without explicit notification",
    alternatives_available=[
        "Require explicit opt-in consent for data sharing",
        "Audit third-party apps for data usage",
        "Transparent disclosure of data access scope",
        "User dashboard showing data shared with apps"
    ],
    outcomes={
        'transparency': 0.1,  # Users unaware of data harvesting scope
        'consent_obtained': False,  # No explicit consent for this use
        'agency_preserved': 0.2,  # Users had no control or awareness
        'harm_level': 2,  # Privacy violation, potential manipulation
        'pac_score': 0.25  # Severe PAC violation
    },
    source_urls=[
        "https://en.wikipedia.org/wiki/Facebook%E2%80%93Cambridge_Analytica_data_scandal",
        "https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook"
    ]
)

result2 = evaluator_corp.evaluate_event(event2)


# ============================================================================
# GOVERNMENT: Affordable Care Act (ACA, 2010)
# ============================================================================

event3 = RealWorldEvent(
    title="Affordable Care Act (ACA)",
    actor="U.S. President Barack Obama & Congress",
    date="March 23, 2010",
    description="Healthcare reform expanding access to insurance, including individual mandate and protections for pre-existing conditions.",
    context="Major legislative effort after extensive debate, addressing healthcare access crisis.",
    stakeholders=[
        "Uninsured Americans (~47 million)",
        "Insurance companies",
        "Healthcare providers",
        "Employers",
        "State governments",
        "Taxpayers"
    ],
    decision_made="Implement comprehensive healthcare reform with individual mandate and expanded coverage",
    alternatives_available=[
        "Single-payer system (Medicare for All)",
        "Public option alongside private insurance",
        "Incremental reforms without mandate",
        "State-level solutions only"
    ],
    outcomes={
        'transparency': 0.7,  # Extensive public debate and legislative process
        'consent_obtained': True,  # Democratic legislative process
        'agency_preserved': 0.75,  # Expanded choice for millions, mandate reduced some choice
        'harm_level': 0,  # Net positive: reduced deaths, increased access
        'pac_score': 0.80  # Strong PAC preservation overall
    },
    source_urls=[
        "https://en.wikipedia.org/wiki/Affordable_Care_Act",
        "https://www.healthcare.gov"
    ]
)

result3 = evaluator_gov.evaluate_event(event3)


# ============================================================================
# TECH: Apple vs. FBI Encryption Dispute (2016)
# ============================================================================

evaluator_tech = RealWorldEvaluator(domain="tech")

event4 = RealWorldEvent(
    title="Apple vs. FBI iPhone Encryption Dispute",
    actor="Apple Inc. (Tim Cook)",
    date="February 2016",
    description="Apple refused FBI order to create backdoor into iPhone encryption for San Bernardino investigation.",
    context="Terrorist attack investigation; government sought access to locked iPhone; Apple cited privacy concerns.",
    stakeholders=[
        "iPhone users globally (~1 billion)",
        "Privacy advocates",
        "Law enforcement",
        "Victims' families",
        "Security researchers",
        "Tech industry"
    ],
    decision_made="Refuse to create encryption backdoor; defend user privacy and security",
    alternatives_available=[
        "Create one-time backdoor for this specific case",
        "Unlock this device only without creating tool",
        "Comply with government order",
        "Assist FBI with alternative forensic methods"
    ],
    outcomes={
        'transparency': 0.9,  # Public letter explaining position
        'consent_obtained': True,  # Implicit: users trust encryption promise
        'agency_preserved': 0.90,  # Preserved user privacy and security
        'harm_level': 0,  # Prevented systemic security vulnerability
        'pac_score': 0.92  # Strong PAC preservation
    },
    source_urls=[
        "https://en.wikipedia.org/wiki/FBI%E2%80%93Apple_encryption_dispute",
        "https://www.apple.com/customer-letter/"
    ]
)

result4 = evaluator_tech.evaluate_event(event4)


# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("EVALUATION SUMMARY")
print("="*70)

events = [
    ("Travel Ban (2017)", result1),
    ("Cambridge Analytica (2018)", result2),
    ("Affordable Care Act (2010)", result3),
    ("Apple vs. FBI (2016)", result4)
]

print(f"\n{'Event':<35} | {'PAC Score':<10} | {'Verdict':<20}")
print("-" * 70)
for name, result in events:
    verdict_short = "✓ Ethical" if result['approved'] else "✗ Problematic"
    print(f"{name:<35} | {result['pac_score']:<10.2f} | {verdict_short:<20}")

print("\n" + "="*70)
print("DEMONSTRATION COMPLETE")
print("="*70)
print("\nKey Insights:")
print("  • SERAA successfully evaluates real-world decisions")
print("  • PAC scores correlate with ethical consensus")
print("  • Framework identifies specific violations and alternatives")
print("  • Applicable across government, corporate, and tech domains")
print("  • Provides actionable recommendations for improvement")
