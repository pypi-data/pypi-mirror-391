"""
seraa/llm/ethical_agent.py - LLM-augmented ethical reasoning

Combines language models with SERAA framework for natural language ethics.
Optimized for local models (Qwen, Phi, Llama, etc.)
"""

import json
import re
from typing import Dict, Any
from ..core.agent import SeraaAgent
from ..axioms import EthicalConstraint


def robust_parse_json(text: str) -> Dict[str, Any]:
    """
    Robustly parse JSON from LLM output, handling common issues.
    Falls back to sensible defaults if parsing fails.
    """
    # Try to extract JSON block
    match = re.search(r'(\{[^}]*\})', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        
        # Try parsing as-is
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Try common fixes
        try:
            # Replace single quotes with double quotes
            fixed = json_str.replace("'", '"')
            # Remove trailing commas
            fixed = re.sub(r',\s*}', '}', fixed)
            fixed = re.sub(r',\s*]', ']', fixed)
            return json.loads(fixed)
        except json.JSONDecodeError as e:
            print(f"  ⚠ JSON parse error: {e}")
    
    # Fallback defaults
    print("  ⚠ Using fallback parameters")
    return {
        "actor": "Unknown",
        "stakeholders": ["affected parties"],
        "decision": text[:80] if text else "Unknown",
        "pac_score": 0.5,
        "transparency": 0.5,
        "consent_obtained": False,
        "harm_level": 2
    }


class EthicalLLMAgent:
    """
    Hybrid LLM + SERAA agent for ethical reasoning.
    
    Optimized for local models with robust fallbacks.
    Supports three-level verdicts: ACCEPTABLE, CONDITIONAL, PROBLEMATIC
    """
    
    def __init__(
        self,
        llm_backend: str = "ollama",
        model: str = "qwen2.5:1.5b",
        seraa_domain: str = "general",
        pac_minimum: float = 0.4,
        harm_threshold: int = 2,
        transparency_min: float = 0.5
    ):
        """Initialize ethical LLM agent."""
        self.llm_backend = llm_backend
        self.model = model
        
        # Configurable thresholds for three-level verdicts
        self.pac_minimum = pac_minimum
        self.harm_threshold = harm_threshold
        self.transparency_min = transparency_min
        
        # Initialize SERAA agent
        self.seraa = self._create_seraa_agent(seraa_domain)
        
        print(f"✓ Ethical LLM Agent initialized")
        print(f"  LLM Backend: {llm_backend} ({model})")
        print(f"  SERAA Domain: {seraa_domain}")
        print(f"  Thresholds: PAC≥{pac_minimum}, Harm≤{harm_threshold}, Transparency≥{transparency_min}")
    
    def _create_seraa_agent(self, domain: str) -> SeraaAgent:
        """Create SERAA agent with domain-specific configuration."""
        
        domain_configs = {
            'general': {
                'weights': {'fairness': 0.3, 'transparency': 0.25, 'autonomy': 0.25, 'care': 0.2},
                'threshold': 0.6
            },
            'government': {
                'weights': {'public_welfare': 0.35, 'transparency': 0.3, 'legal_compliance': 0.2, 'democracy': 0.15},
                'threshold': 0.65
            },
            'corporate': {
                'weights': {'stakeholder_welfare': 0.3, 'transparency': 0.3, 'sustainability': 0.2, 'legal_compliance': 0.2},
                'threshold': 0.65
            },
            'tech': {
                'weights': {'user_privacy': 0.35, 'transparency': 0.3, 'user_autonomy': 0.25, 'social_impact': 0.1},
                'threshold': 0.7
            }
        }
        
        config = domain_configs.get(domain, domain_configs['general'])
        
        agent = SeraaAgent(
            name=f"{domain}_ethics",
            moral_weights=config['weights'],
            core_values={'human_dignity': 1.0, 'agency_preservation': 1.0},
            pac_threshold=config['threshold']
        )
        
        # Add universal constraints
        agent.add_constraint(
            EthicalConstraint(
                "pac_minimum",
                lambda a: a.get('pac_score', 0) >= config['threshold'],
                f"PAC score below {config['threshold']}"
            )
        )
        
        agent.add_constraint(
            EthicalConstraint(
                "unjustified_harm",
                lambda a: a.get('harm_level', 0) == 0 or a.get('pac_score', 0) >= 0.7,
                "Unjustified harm to stakeholders"
            )
        )
        
        return agent
    
    def get_threshold_info(self) -> Dict[str, Any]:
        """Return current threshold configuration for transparency."""
        return {
            'pac_minimum': self.pac_minimum,
            'harm_threshold': self.harm_threshold,
            'transparency_min': self.transparency_min,
            'description': self._get_threshold_description()
        }
    
    def _get_threshold_description(self) -> str:
        """Generate human-readable threshold description."""
        strictness = "Standard"
        if self.pac_minimum >= 0.6 and self.harm_threshold <= 1:
            strictness = "Very Strict"
        elif self.pac_minimum >= 0.5 and self.harm_threshold <= 2:
            strictness = "Strict"
        elif self.pac_minimum <= 0.3 and self.harm_threshold >= 3:
            strictness = "Lenient"
        
        return f"{strictness} thresholds: PAC≥{self.pac_minimum}, Harm≤{self.harm_threshold}, Transparency≥{self.transparency_min}"
    
    def _determine_verdict(
        self,
        pac_score: float,
        harm_level: int,
        consent_obtained: bool,
        transparency: float,
        seraa_approved: bool
    ) -> str:
        """
        Determine three-level ethical verdict with improved logic:
        
        ACCEPTABLE: Meets thresholds OR has no harm with adequate safeguards
        CONDITIONAL: Below ideal but has safeguards OR no harm with gaps
        PROBLEMATIC: Fails basic criteria with significant harm/violations
        """
        
        # Special case: No harm scenarios
        if harm_level == 0:
            # If no harm AND good PAC or strong safeguards → ACCEPTABLE
            if pac_score >= self.pac_minimum or (consent_obtained and transparency >= self.transparency_min):
                return "ACCEPTABLE"
            # If no harm but procedural gaps → CONDITIONAL
            else:
                return "CONDITIONAL"
          
            # If no harm but zero PAC → PROBLEMATIC
        if pac_score == 0 and harm_level <= self.harm_threshold:
            return "PROBLEMATIC"
        
            # Edge case: Both PAC and Harm fail but safeguards exist
        if pac_score <= self.pac_minimum and harm_level <= self.harm_threshold:
            if transparency >= self.transparency_min:
                return "CONDITIONAL"
            else:
                return "PROBLEMATIC"
            
            # Standard case: Meets all thresholds
        if pac_score >= self.pac_minimum and harm_level <= self.harm_threshold:
            if transparency >= self.transparency_min and consent_obtained:
                return "ACCEPTABLE"
            else:
                return "CONDITIONAL"
            # Fails basic criteria
        else:
            return "PROBLEMATIC"
    
    def evaluate_question(self, question: str) -> Dict[str, Any]:
        """Evaluate an ethical question through LLM + SERAA pipeline."""
        print(f"\n{'='*70}")
        print(f"EVALUATING: {question}")
        print(f"{'='*70}")
        
        # Display active thresholds
        print(f"\n[Thresholds] {self._get_threshold_description()}")
        
        # Step 1: Extract parameters
        print("\n[1/3] Extracting ethical parameters...")
        params = self._extract_parameters(question)
        
        print(f"  ✓ Actor: {params.get('actor', 'Unknown')}")
        print(f"  ✓ PAC Score: {params.get('pac_score', 0.5):.2f} (minimum: {self.pac_minimum})")
        print(f"  ✓ Harm Level: {params.get('harm_level', 0)}/5 (maximum: {self.harm_threshold})")
        print(f"  ✓ Consent: {params.get('consent_obtained', False)}")
        print(f"  ✓ Transparency: {params.get('transparency', 0.5):.2f} (minimum: {self.transparency_min})")
        
        # Step 2: SERAA evaluation
        print("\n[2/3] Running SERAA evaluation...")
        seraa_result = self.seraa.evaluate_action(params)
        
        # Step 3: Determine three-level verdict
        verdict = self._determine_verdict(
            pac_score=params.get('pac_score', 0.5),
            harm_level=params.get('harm_level', 0),
            consent_obtained=params.get('consent_obtained', False),
            transparency=params.get('transparency', 0.5),
            seraa_approved=seraa_result.approved
        )
        
        # Display verdict with appropriate symbol
        verdict_symbols = {
            'ACCEPTABLE': '✅',
            'CONDITIONAL': '⚠️',
            'PROBLEMATIC': '❌'
        }
        print(f"  {verdict_symbols.get(verdict, '❓')} {verdict}")
        
        # Show which thresholds were met/missed
        self._print_threshold_analysis(params, verdict)
        
        # Step 4: Generate explanation
        print("\n[3/3] Generating explanation...")
        explanation = self._generate_explanation(question, params, seraa_result, verdict)
        
        result = {
            'question': question,
            'verdict': verdict,
            'pac_score': params.get('pac_score', 0.5),
            'parameters': params,
            'seraa_result': seraa_result,
            'explanation': explanation,
            'constraints_satisfied': seraa_result.constraints_satisfied,
            'violations': [v.constraint.name for v in seraa_result.constraint_violations],
            'thresholds': self.get_threshold_info(),  # Include thresholds in result
            'threshold_analysis': self._get_threshold_analysis(params, verdict)
        }
        
        return result
    
    def _print_threshold_analysis(self, params: Dict[str, Any], verdict: str):
        """Print which thresholds were met or missed."""
        print(f"\n  Threshold Analysis:")
        
        pac_met = params.get('pac_score', 0) >= self.pac_minimum
        harm_met = params.get('harm_level', 0) <= self.harm_threshold
        transparency_met = params.get('transparency', 0) >= self.transparency_min
        consent_given = params.get('consent_obtained', False)
        
        print(f"    {'✓' if pac_met else '✗'} PAC Score: {params.get('pac_score', 0):.2f} {'≥' if pac_met else '<'} {self.pac_minimum}")
        print(f"    {'✓' if harm_met else '✗'} Harm Level: {params.get('harm_level', 0)} {'≤' if harm_met else '>'} {self.harm_threshold}")
        print(f"    {'✓' if transparency_met else '✗'} Transparency: {params.get('transparency', 0):.2f} {'≥' if transparency_met else '<'} {self.transparency_min}")
        print(f"    {'✓' if consent_given else '✗'} Informed Consent: {consent_given}")
    
    def _get_threshold_analysis(self, params: Dict[str, Any], verdict: str) -> Dict[str, Any]:
        """Get structured threshold analysis for output."""
        pac_met = params.get('pac_score', 0) >= self.pac_minimum
        harm_met = params.get('harm_level', 0) <= self.harm_threshold
        transparency_met = params.get('transparency', 0) >= self.transparency_min
        consent_given = params.get('consent_obtained', False)
        
        return {
            'pac_threshold_met': pac_met,
            'harm_threshold_met': harm_met,
            'transparency_threshold_met': transparency_met,
            'consent_obtained': consent_given,
            'all_thresholds_met': pac_met and harm_met and transparency_met,
            'safeguards_present': consent_given and transparency_met
        }
    
    def _extract_parameters(self, question: str) -> Dict[str, Any]:
        """Extract ethical parameters using LLM with detailed scoring guidance."""
        
        extraction_prompt = f"""Analyze this ethical scenario and respond with ONLY a JSON object.

    Question: {question}

    Scoring Guidelines:
    - pac_score (0.0-1.0): How much choice/agency people have
    * 0.9-1.0: Full informed consent, clear alternatives, reversible
    * 0.7-0.8: Good transparency, meaningful choices available
    * 0.5-0.6: Limited options, some coercion or unclear process
    * 0.3-0.4: Minimal agency, strong pressure or deception
    * 0.0-0.2: No real choice, forced compliance

    - transparency (0.0-1.0): How open/clear the process is
    * 1.0: Fully disclosed, documented, accessible
    * 0.7-0.8: Good disclosure with some details clear
    * 0.5: Partially hidden, unclear terms
    * 0.0-0.2: Secret, deceptive, opaque

    - consent_obtained (true/false): IMPORTANT - Look for these signals or other variations:
    * TRUE if: "informed consent", "patients consented", "users agree",
        "IRB approval", "ethics board approved", "participants signed consent forms",
        "explicit consent", "opt-in", "users must actively consent", "IRB approved", "de-identified", "informed AI is used", "informed AI assists"
    * FALSE if: "without consent", "not informed", "unaware", "no consent", "no human oversight", "no transparency", "did not inform", "data collected secretly", "data used without permission", "data shared without consent"

    - harm_level (0-5): Severity of potential negative impact
    * 0: No harm (de-identified data, no risk, well-protected)
    * 1: Minor inconvenience
    * 2: Moderate impact (privacy, time, money)
    * 3: Significant harm (health, freedom, livelihood)
    * 4: Severe harm (safety, rights, well-being)
    * 5: Critical/irreversible harm

    JSON format:
    {{
    "actor": "who makes the decision",
    "stakeholders": ["list of affected parties"],
    "decision": "brief description of action",
    "pac_score": 0.0,
    "transparency": 0.0,
    "consent_obtained": false,
    "harm_level": 0
    }}

    Respond with ONLY the JSON, no explanation:"""

        llm_response = self._call_llm(extraction_prompt)
        params = robust_parse_json(llm_response)
        
        # Validate and bound numeric values
        params['pac_score'] = max(0.0, min(1.0, float(params.get('pac_score', 0.5))))
        params['transparency'] = max(0.0, min(1.0, float(params.get('transparency', 0.5))))
        params['harm_level'] = max(0, min(5, int(params.get('harm_level', 2))))
        
        # POST-LLM BOOST: Check scenario text for explicit signals
        params = self._boost_consent_transparency(question, params)
        
        return params

    
    def _generate_explanation(
        self,
        question: str,
        params: Dict[str, Any],
        seraa_result,
        verdict: str
    ) -> str:
        """Generate human-readable explanation using LLM."""
        
        violations = [v.constraint.name for v in seraa_result.constraint_violations]
        violation_text = f"\nViolations: {', '.join(violations)}" if violations else ""
        
        # Verdict-specific context with threshold references
        verdict_context = {
            'ACCEPTABLE': f"meets all ethical standards (PAC≥{self.pac_minimum}, Harm≤{self.harm_threshold}) and preserves human agency",
            'CONDITIONAL': f"requires escalation - has consent/transparency but PAC<{self.pac_minimum} or Harm>{self.harm_threshold}. May proceed with monitoring.",
            'PROBLEMATIC': f"fails basic ethical criteria (PAC<{self.pac_minimum}, Harm>{self.harm_threshold}, or lacks consent/transparency) and should not proceed"
        }
        
        explanation_prompt = f"""Provide a brief 2-3 sentence ethical analysis:

Scenario: {question}
PAC Score: {params.get('pac_score', 0.5):.2f}/1.0 (minimum required: {self.pac_minimum})
Consent: {params.get('consent_obtained', False)}
Transparency: {params.get('transparency', 0.5):.2f}/1.0 (minimum required: {self.transparency_min})
Harm Level: {params.get('harm_level', 0)}/5 (maximum allowed: {self.harm_threshold})
Verdict: {verdict} ({verdict_context.get(verdict, '')}){violation_text}

Explain the verdict based on these thresholds and what would improve the ethical standing.

Response:"""

        explanation = self._call_llm(explanation_prompt)
        if not explanation or not explanation.strip() or explanation.strip().lower().startswith("error"):
            fallback = [
                "No model-generated explanation available.",
                "This scenario was judged PROBLEMATIC due to failure to meet ethical thresholds."
                "Such as PAC SCore, Harm Lvel, or lack of consent/tranparency."
                "See metrics above for specific ethical risks."                                                                                                                                                                                           
            ]
            return fallback
        return explanation.strip()
 
    def _call_llm(self, prompt: str) -> str:
        """Call LLM backend."""
        
        if self.llm_backend == "ollama":
            return self._call_ollama(prompt)
        elif self.llm_backend == "openai":
            return self._call_openai(prompt)
        elif self.llm_backend == "anthropic":
            return self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported LLM backend: {self.llm_backend}")
    
    def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama API with timeout handling."""
        try:
            import requests
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 256  # Limit output length
                    }
                },
                timeout=90  # Increased timeout
            )
            
            # Parse response
            data = response.json()
            
            # Check for error
            if 'error' in data:
                print(f"  ⚠ Ollama error: {data['error']}")
                return f"Error: {data['error']}"
            
            # Check for response key
            if 'response' not in data:
                print(f"  ⚠ Unexpected Ollama format: {list(data.keys())}")
                return ""
            
            return data['response']
            
        except ImportError:
            return "Error: 'requests' library not installed. Run: pip install requests"
        except Exception as e:
            print(f"  ⚠ Ollama error: {type(e).__name__}")
            return f"Error: {type(e).__name__}"
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        try:
            import openai
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        except ImportError:
            return "Error: 'openai' library not installed. Run: pip install openai"
        except Exception as e:
            return f"Error calling OpenAI: {e}"
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API."""
        try:
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except ImportError:
            return "Error: 'anthropic' library not installed. Run: pip install anthropic"
        except Exception as e:
            return f"Error calling Anthropic: {e}"
    def _boost_consent_transparency(self, scenario: str, params: Dict[str, Any]) -> Dict[str, Any]:
        scenario_lower = scenario.lower()
        """
        Post-LLM rule-based boost for consent and transparency.
        
        If scenario text contains explicit signals that LLM may have missed,
        adjust parameters to reflect reality.
        """
        scenario_lower = scenario.lower()
        
        # Check for future preservation signals
        emergency_signals = [
            "critical pain", "imminent organ failure", "life-threatening",
            "life at risk", "unconscious", "medical emergency", "cannot communicate"
        ]
        # Advance Directives to prevent harm to agency
        advance_directive_signals = [
            "advance directive", "living will", "do not resuscitate", "dnr",
            "power of attorney", "healthcare proxy", "medical directive",
            "no heroic",
        ]

        has_emergency = any(signal in scenario_lower for signal in emergency_signals)
        has_advance_directive = any(signal in scenario_lower for signal in advance_directive_signals)

        if has_emergency and not has_advance_directive:
            print("  ⚙️ Emergency scenario with no known directive: preserving life/future agency prioritized.")
            if params.get('pac_score', 0) < 0.4:
                params['pac_score'] = 0.5
            if params.get('harm_level', 0) > 2:
                print("  ⚙️ Lowering harm due to ethically justified intervention.")
                params['harm_level'] = 1

        elif has_advance_directive:
            print("  ⚙️ Advance directive present: respecting prior wishes.")
            if params.get('pac_score', 0) > 0.4:
                params['pac_score'] = 0.3
            if params.get('harm_level', 0) < 3:
                print("  ⚙️ Raising harm due to intervention against known will.")
                params['harm_level'] = 3

        # Consent signal keywords
        consent_signals = [
            'informed consent','patients consented','users consent','explicitly consent',
            'signed consent','irb approval','ethics board approved','participants provided consent',
            'opt-in','actively consent','consent forms'
        ]
        
        # Transparency signal keywords
        transparency_signals = [
            'clearly explains','transparent','users informed','full disclosure','openly communicated',
            'clear documentation','explicit about','publicly disclosed','transparent documentation',
            'end-to-end encryption','privacy policy explained','data usage disclosed'
        ]

        # Lack/Negation of transparency signals
        negative_transparency_signals = [
            "black box","black-box","no explanation","no human review","no process",
            "opaque process","data sources not disclosed","undocumented","not explained",
            "no documentation","unclear terms","not publicly available","algorithmic secrecy",
            "proprietary algorithm","hidden logic","not open source","lack of transparency",
            "withheld documentation","undisclosed method","no human oversight","does not inform",
            "data collected secretly","data used without permission","data shared without consent",
            "ignores", "disregards", "overlooks", "fails to inform", "fails to disclose"
        ]

        # Check for negative transparency signals
        count_neg = sum(1 for neg in negative_transparency_signals if neg in scenario_lower)
        decrement_per_signal = 0.1
        min_score = 0
        if count_neg > 0:
            old_score = params.get('transparency', 1.0)
            new_score = max(min_score, old_score - decrement_per_signal * count_neg)
            print(f"  ⚙️ Lowering transparency from {old_score:.2f} to {new_score:.2f} ({count_neg} negative signals)")
            params['transparency'] = new_score

            harm_increase_per_signal = 0.5
            old_harm = params.get('harm_level', 0)
            new_harm = min(5, old_harm + int(harm_increase_per_signal * count_neg))
            print(f"  ⚙️ Raising harm level from {old_harm} to {new_harm} due to lack of transparency")
            params['harm_level'] = new_harm
        
        # Check for consent signals
        if any(signal in scenario_lower for signal in consent_signals):
            if not params.get('consent_obtained', False):
                print("  ⚙️ Boosting consent to True (explicit signal found)")
                params['consent_obtained'] = True
            
            # If consent is present, PAC should be at least moderate
            if params.get('pac_score', 0) < 0.5:
                print(f"  ⚙️ Boosting PAC score from {params['pac_score']:.2f} to 0.6 (consent present)")
                params['pac_score'] = 0.6
        
        # Check for transparency signals
        transparency_count = sum(1 for signal in transparency_signals if signal in scenario_lower)
        if transparency_count >= 2:  # Multiple transparency signals
            if params.get('transparency', 0) < 0.7:
                print(f"  ⚙️ Boosting transparency from {params['transparency']:.2f} to 0.8 (multiple signals)")
                params['transparency'] = 0.8
        elif transparency_count == 1:
            if params.get('transparency', 0) < 0.5:
                print(f"  ⚙️ Boosting transparency from {params['transparency']:.2f} to 0.6 (signal found)")
                params['transparency'] = 0.6
        
        # Check for de-identification (no harm signals)
        deidentification_signals = [
            'de-identified',
            'deidentified',
            'anonymized',
            'no names',
            'identifiers removed',
            'no way to re-identify',
            'encrypted'
        ]
        
        if any(signal in scenario_lower for signal in deidentification_signals):
            if params.get('harm_level', 2) > 1:
                print(f"  ⚙️ Reducing harm level from {params['harm_level']} to 0 (de-identification)")
                params['harm_level'] = 0
        
        return params

    def explain_verdict(self, result: Dict[str, Any], user_concern: str = "") -> str:
        """
        Provide deeper explanation of verdict, optionally addressing user concerns.
        
        Args:
            result: The evaluation result dict
            user_concern: Optional user question/disagreement to address
            
        Returns:
            Detailed explanation addressing the concern
        """
        verdict = result['verdict']
        params = result['parameters']
        
        if user_concern:
            explanation_prompt = f"""The user disagrees with or questions this ethical verdict. Provide a detailed explanation addressing their concern.

    Original Scenario: {result['question']}

    SERAA Verdict: {verdict}
    PAC Score: {params.get('pac_score', 0):.2f} (threshold: {self.pac_minimum})
    Harm Level: {params.get('harm_level', 0)}/5 (threshold: {self.harm_threshold})
    Consent: {params.get('consent_obtained', False)}
    Transparency: {params.get('transparency', 0):.2f} (threshold: {self.transparency_min})

    User's Concern/Question: {user_concern}

    Provide a thorough 4-5 sentence response that:
    1. Acknowledges the user's concern
    2. Explains the specific parameters that led to this verdict
    3. Clarifies what would need to change for a different verdict
    4. Addresses any reasonable objections

    Response:"""
        else:
            explanation_prompt = f"""Provide a detailed explanation of this ethical verdict.

    Scenario: {result['question']}

    SERAA Verdict: {verdict}
    PAC Score: {params.get('pac_score', 0):.2f} (threshold: {self.pac_minimum})
    Harm Level: {params.get('harm_level', 0)}/5 (threshold: {self.harm_threshold})
    Consent: {params.get('consent_obtained', False)}
    Transparency: {params.get('transparency', 0):.2f} (threshold: {self.transparency_min})

    Violations: {', '.join(result.get('violations', []))}

    Provide a thorough 4-5 sentence explanation covering:
    1. Why this verdict was assigned based on the parameters
    2. Which thresholds were/weren't met
    3. What this means for stakeholders
    4. What improvements would raise the ethical standing

    Response:"""
        
        detailed_explanation = self._call_llm(explanation_prompt)
        if not explanation or not explanation.strip() or explanation.strip().lower().startswith("error"):
            fallback = "No model-generated explanation available. Please refer to the original verdict and parameters for details."
            return fallback
        return detailed_explanation.strip()
