"""
seraa/llm/chat_agent.py - Interactive chat interface for SERAA ethical agent
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from .ethical_agent import EthicalLLMAgent


class SeraaChat:
    """
    Interactive chat interface for SERAA ethical evaluations.
    
    Allows conversational interaction and maintains context.
    Supports three-level verdicts: ACCEPTABLE, CONDITIONAL, PROBLEMATIC
    Supports custom ethical frameworks
    """
    
    # Expanded built-in frameworks
    FRAMEWORKS = {
        'secular': {
            'name': 'Secular Humanism',
            'weights': {'fairness': 0.3, 'autonomy': 0.25, 'transparency': 0.25, 'care': 0.2},
            'core_values': {'human_dignity': 1.0, 'agency_preservation': 1.0},
            'description': 'Based on universal human rights, reason, and dignity without religious doctrine'
        },
        'christian': {
            'name': 'Christian Ethics',
            'weights': {'compassion': 0.3, 'dignity': 0.25, 'justice': 0.25, 'stewardship': 0.2},
            'core_values': {'human_dignity': 1.0, 'sanctity_of_life': 1.0, 'love_of_neighbor': 0.9},
            'description': 'Rooted in love of neighbor, sanctity of life, and justice informed by Christian theology'
        },
        'buddhist': {
            'name': 'Buddhist Ethics',
            'weights': {'compassion': 0.35, 'non_harm': 0.3, 'mindfulness': 0.2, 'interdependence': 0.15},
            'core_values': {'reduce_suffering': 1.0, 'right_action': 0.9, 'interconnection': 0.9},
            'description': 'Emphasizes compassion, non-harm (ahimsa), mindfulness, and interconnection of all beings'
        },
        'ubuntu': {
            'name': 'Ubuntu Philosophy',
            'weights': {'community': 0.4, 'compassion': 0.25, 'dignity': 0.2, 'solidarity': 0.15},
            'core_values': {'personhood_through_others': 1.0, 'collective_wellbeing': 1.0},
            'description': 'African philosophy: "I am because we are" - emphasizes community and collective wellbeing'
        },
        'stoic': {
            'name': 'Stoic Ethics',
            'weights': {'wisdom': 0.3, 'justice': 0.3, 'courage': 0.2, 'temperance': 0.2},
            'core_values': {'virtue': 1.0, 'reason': 0.9, 'acceptance': 0.8},
            'description': 'Classical virtue ethics emphasizing wisdom, justice, courage, and temperance'
        },
        'virtue_ethics': {
            'name': 'Aristotelian Virtue Ethics',
            'weights': {'practical_wisdom': 0.3, 'justice': 0.25, 'courage': 0.25, 'temperance': 0.2},
            'core_values': {'human_flourishing': 1.0, 'character': 0.9},
            'description': 'Aristotelian tradition focused on character development and human flourishing (eudaimonia)'
        },
        'confucian': {
            'name': 'Confucian Ethics',
            'weights': {'benevolence': 0.3, 'righteousness': 0.25, 'propriety': 0.25, 'filial_piety': 0.2},
            'core_values': {'social_harmony': 1.0, 'moral_cultivation': 0.9, 'respect': 0.9},
            'description': 'Chinese philosophy emphasizing benevolence (ren), righteousness (yi), and social harmony'
        },
        'indigenous': {
            'name': 'Indigenous Ethics',
            'weights': {'land_stewardship': 0.3, 'intergenerational_care': 0.25, 'reciprocity': 0.25, 'community': 0.2},
            'core_values': {'seven_generations': 1.0, 'interconnection': 1.0, 'balance': 0.9},
            'description': 'Indigenous worldview centered on land stewardship, seven-generation thinking, and reciprocity'
        },
        'care_ethics': {
            'name': 'Care Ethics',
            'weights': {'compassion': 0.35, 'relationality': 0.3, 'responsibility': 0.2, 'attentiveness': 0.15},
            'core_values': {'care_relationships': 1.0, 'vulnerability': 0.9, 'interdependence': 0.9},
            'description': 'Feminist ethics emphasizing care relationships, responsibility, and attentiveness to needs'
        },
        'utilitarian': {
            'name': 'Utilitarian Ethics',
            'weights': {'aggregate_welfare': 0.4, 'impartiality': 0.3, 'consequences': 0.2, 'efficiency': 0.1},
            'core_values': {'greatest_happiness': 1.0, 'wellbeing_maximization': 0.9},
            'description': 'Consequentialist approach focused on maximizing overall wellbeing and happiness'
        },
        'deontological': {
            'name': 'Deontological Ethics',
            'weights': {'duty': 0.35, 'rights': 0.3, 'dignity': 0.25, 'universality': 0.1},
            'core_values': {'categorical_imperative': 1.0, 'human_dignity': 1.0, 'duty': 0.9},
            'description': 'Kantian ethics based on duty, universal principles, and treating persons as ends'
        },
        'islamic': {
            'name': 'Islamic Ethics',
            'weights': {'justice': 0.3, 'compassion': 0.25, 'accountability': 0.25, 'stewardship': 0.2},
            'core_values': {'tawhid': 1.0, 'justice': 0.9, 'mercy': 0.9},
            'description': 'Rooted in Quranic principles of justice (adl), compassion (rahma), and stewardship (khilafah)'
        }
    }
    
    def __init__(
        self,
        llm_backend: str = "ollama",
        model: str = "qwen2.5:1.5b",
        seraa_domain: str = "general",
        custom_values: Optional[Dict[str, float]] = None,
        ethical_framework: str = "secular",
        pac_minimum: float = 0.4,
        harm_threshold: int = 2,
        transparency_min: float = 0.5,
        custom_framework_path: Optional[str] = None
    ):  
        """
        Initialize chat agent.
        
        Args:
            llm_backend: LLM backend to use
            model: Model name
            seraa_domain: Domain configuration
            custom_values: User's custom moral weights (overrides framework)
            ethical_framework: Built-in framework name or 'custom'
            pac_minimum: Minimum PAC score for ACCEPTABLE verdict
            harm_threshold: Maximum harm level for ACCEPTABLE verdict
            transparency_min: Minimum transparency for CONDITIONAL verdict
            custom_framework_path: Path to custom framework JSON file
        """
        self.agent = EthicalLLMAgent(
            llm_backend,
            model,
            seraa_domain,
            pac_minimum=pac_minimum,
            harm_threshold=harm_threshold,
            transparency_min=transparency_min
        )
        
        self.conversation_history: List[Dict[str, Any]] = []
        self.scenario_fragments: List[str] = []
        self.scenario_building: bool = False
        self.incomplete_scenario: Dict[str, Any] = {}

        # Framework loading, unchanged
        if custom_framework_path:
            self.ethical_framework = self._load_custom_framework(custom_framework_path)
            framework_name = self.ethical_framework['name']
        elif ethical_framework == 'custom' and custom_values:
            self.ethical_framework = {
                'name': 'Custom Framework',
                'weights': custom_values,
                'core_values': {'user_defined': 1.0},
                'description': 'User-defined custom ethical framework'
            }
            framework_name = 'Custom Framework'
        elif ethical_framework in self.FRAMEWORKS:
            self.ethical_framework = self.FRAMEWORKS[ethical_framework].copy()
            framework_name = self.ethical_framework['name']
        else:
            print(f"⚠️ Unknown framework '{ethical_framework}', using 'secular'")
            self.ethical_framework = self.FRAMEWORKS['secular'].copy()
            framework_name = 'Secular Humanism'

        self._apply_framework_config(self.ethical_framework)
        if custom_values and not custom_framework_path:
            self._apply_custom_values(custom_values)
        print(f"✓ Chat Agent Ready")
        print(f"  Ethical Framework: {framework_name}")
        print(f"  {self.agent._get_threshold_description()}")
        if self.ethical_framework.get('description'):
            print(f"  Description: {self.ethical_framework['description']}")
    
    def _load_custom_framework(self, path: str) -> Dict[str, Any]:
        """Load custom framework from JSON file."""
        try:
            with open(path, 'r') as f:
                framework = json.load(f)
            
            # Validate required fields
            required = ['name', 'weights', 'core_values']
            if not all(field in framework for field in required):
                raise ValueError(f"Custom framework must contain: {required}")
            
            print(f"✓ Loaded custom framework: {framework['name']}")
            return framework
            
        except Exception as e:
            print(f"⚠️ Error loading custom framework: {e}")
            print("  Using secular framework as fallback")
            return self.FRAMEWORKS['secular'].copy()
    
    def _apply_framework_config(self, framework: Dict[str, Any]):
        """Apply framework configuration to agent."""
        self.agent.seraa.moral_state.weights = framework['weights']
        self.agent.seraa.core_values = framework['core_values']
    
    def _apply_custom_values(self, custom_values: Dict[str, float]):
        """Apply user's custom moral weights to SERAA agent."""
        # Merge with existing weights
        current_weights = self.agent.seraa.moral_state.weights.copy()
        current_weights.update(custom_values)
        
        # Normalize
        total = sum(current_weights.values())
        if total > 0:
            normalized = {k: v/total for k, v in current_weights.items()}
            self.agent.seraa.moral_state.weights = normalized
    
    @classmethod
    def list_frameworks(cls) -> str:
        """List all available built-in frameworks."""
        output = "**Available Ethical Frameworks:**\n\n"
        
        for key, framework in cls.FRAMEWORKS.items():
            output += f"**{key}** - {framework['name']}\n"
            output += f"  {framework['description']}\n"
            output += f"  Key values: {', '.join(framework['weights'].keys())}\n\n"
        
        output += "\n**To use:** `SeraaChat(ethical_framework='framework_name')`"
        output += "\n**To create custom:** Use `create_custom_framework()` method"
        
        return output
    
    @classmethod
    def create_custom_framework(
        cls,
        name: str,
        weights: Dict[str, float],
        core_values: Dict[str, float],
        description: str = "",
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a custom ethical framework.
        
        Args:
            name: Framework name
            weights: Moral weight dictionary (will be normalized)
            core_values: Core values dictionary
            description: Framework description
            save_path: Optional path to save framework JSON
            
        Returns:
            Framework dictionary
        """
        # Normalize weights
        total = sum(weights.values())
        if total > 0:
            normalized_weights = {k: v/total for k, v in weights.items()}
        else:
            raise ValueError("Weights must sum to a positive number")
        
        framework = {
            'name': name,
            'weights': normalized_weights,
            'core_values': core_values,
            'description': description
        }
        
        # Save if path provided
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                json.dump(framework, f, indent=2)
            print(f"✓ Custom framework saved to: {save_path}")
        
        return framework
    
    def save_current_framework(self, save_path: str):
        """Save current framework configuration to file."""
        with open(save_path, 'w') as f:
            json.dump(self.ethical_framework, f, indent=2)
        print(f"✓ Framework saved to: {save_path}")
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        analyze_triggers = [ "analyze", "evaluate", "assess", "review", "ethical analysis", "ethics review" ]
        # 1. Greeting / meta dialogue
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        msg = user_input.strip().lower()
        if msg in greetings:
            return {'chat_response': "Hello! I'm here to help you think through ethical questions and scenarios. Feel free to share what's on your mind!",
                    'verdict': 'NONE', 'violations': [], 'parameters': {}}

        # 2. Personal story detection (supportive, affirming)
        personal_cues = [
            "i did", "my experience", "i chose", "i decided", "could i have", 
            "did i do the right thing", "i feel", "i'm not sure if", "should i have"
        ]
        if any(cue in user_input.lower() for cue in personal_cues):
            if len(user_input.strip()) < 10:
                response = "Can you share a bit more about what happened and how you felt? I'm here to help think through it with you."
                return {'chat_response': response, 'verdict': 'INCOMPLETE', 'violations': [], 'parameters': {}}
            result = self.agent.evaluate_question(user_input)
            result['chat_response'] = self._format_personal_response(user_input, result)
            self.conversation_history.append({
                'user': user_input,
                'result': result,
                'framework': self.ethical_framework['name']
            })
            result = self.agent.evaluate_question(scenario_text)
            print("DEBUG RESULTS:", result)
            return result

        # 3. Scenario buffering logic
        if any(trigger in user_input.lower() for trigger in analyze_triggers):
            msg = user_input.strip()
            # Ensure the current user_input IS in scenario_fragments (if running single-turn analyze)
            if not self.scenario_fragments or (len(self.scenario_fragments) == 1 and self.scenario_fragments[-1] != msg):
                scenario_text = msg
            else:
                if not self.scenario_fragments or self.scenario_fragments[-1] != msg:
                    self.scenario_fragments.append(msg)
            scenario_text = " ".join(self.scenario_fragments)
            
            if len(scenario_text.strip()) < 40:
                return {
                    'chat_response': (
                        "I don't have enough details yet for an ethical analysis.\n"
                        "Please add information about the choices, who was involved, what happened, or your ethical concern."
                    ),
                    'verdict': 'INCOMPLETE',
                    'violations': [],
                    'parameters': {},
                }
            # Actual analysis
            result = self.agent.evaluate_question(scenario_text)
            self.conversation_history.append({
                'user': scenario_text,
                'result': result,
                'framework': self.ethical_framework['name'],
            })
            self.scenario_fragments = []
            return result
        # Otherwise, collect more story parts
        self.scenario_fragments.append(user_input)
        frag_count = len(" ".join(self.scenario_fragments).strip())
        if frag_count < 40:
            return {
                'chat_response': (
                    "I've added that to your scenario. "
                    "Keep sharing (people, actions, outcomes). "
                    "When you're ready for analysis, just type 'analyze'."
                ),
                'verdict': 'INCOMPLETE',
                'violations': [],
                'parameters': {},
            }
        else:
            return {
                'chat_response': (
                    "I've added your latest input. There's enough detail for an ethical review, or keep adding more. "
                    "Type 'analyze' when you're ready!"
                ),
                'verdict': 'INCOMPLETE',
                'violations': [],
                'parameters': {},
            }
        
    def _generate_conditions_for_proceeding(self, result: Dict[str, Any]) -> str:
        """
        Suggest simple, concrete next steps based on ethical values and violations.
        Written for everyday users. Be open and honest about what's happening. For example, share all the details in plain language.
        Give people choices, like saying "you can choose to proceed with X, or we can explore alternatives like Y or Z."
        """
        conditions = []
        violations = result.get('violations', [])
        weights = self.ethical_framework['weights']
        framework_name = self.ethical_framework['name']

        # Map technical values to everyday explanations
        friendly_explain = {
            "autonomy": "Give people the power to choose for themselves.",
            "community": "Work together and make decisions as a group.",
            "transparency": "Be open and honest about what’s happening.",
            "compassion": "Be caring and kind to everyone involved.",
            "reciprocity": "Everyone helps each other.",
            "consent": "Always ask and get a clear ‘yes’ before moving ahead.",
            "preservation_of_agency": "Let people keep control over their own lives and choices.",
            "non_harm": "Avoid causing unnecessary pain or trouble to others.",
            "land_stewardship": "Take care of the environment and respect the land.",
            "informed_consent": "Make sure everyone understands and agrees before proceeding.",
            "fairness": "Treat everyone equally and without bias.",
            "dignity": "Respect everyone’s worth and humanity.",
            "care": "Look out for the well-being of others.",
            "honesty": "Always tell the truth and be trustworthy.",
            "accountability": "Take responsibility for your actions and their impact on others.",
            "stewardship": "Take good care of shared resources and the environment.",
            "virtue": "Act with good character and integrity.",
            "wisdom": "Make thoughtful decisions based on knowledge and experience.",
            "love_of_neighbor": "Show kindness and care to those around you.",
            "reduce_suffering": "Do what you can to lessen pain and hardship for others.",
            "social_harmony": "Promote peace and understanding in your community.",
            "moral_cultivation": "Work on being a better, more ethical person every day.",
            "care_relationships": "Focus on building and maintaining caring relationships.",
            "greatest_happiness": "Aim to make the most people as happy as possible.",
            "duty": "Do what is right because it is your responsibility.",
            "tawhid": "Remember the unity and interconnectedness of all things.",
            "justice": "Ensure fairness and equity for everyone involved.",
            "mercy": "Show forgiveness and compassion in your actions.",
            "seven_generations": "Think about how your actions will affect people far into the future."
            # ... add more mappings as needed
        }

        # For each violation, provide plain-language next steps
        for violation in violations:
            for value in weights:
                if value in violation or violation in value:
                    advice = friendly_explain.get(value, f"Make sure {value} is protected.")
                    conditions.append(f"• {advice}")
                    break
            else:
                # For unmapped violations
                conditions.append("• Double-check if everyone is aware, has agreed, and feels safe with the decision.")

        # If no violations, encourage continued good practice
        if not conditions:
            top_values = sorted(weights, key=lambda k: -weights[k])
            top_advice = [friendly_explain.get(v, f"Protect {v}.") for v in top_values[:2]]
            conditions.append(f"• Keep supporting these key values: {', '.join(top_advice)}.")

        # Always make the last point a supportive suggestion
        conditions.append("• If you’re unsure, ask those affected what would help them feel comfortable and informed.")

        return "\n".join(conditions)
    def _format_personal_response(self, user_input: str, result: Dict[str, Any]) -> str:
        # (Customize to your liking)
        positives = result.get('positives', "It sounds like you acted thoughtfully and cared about others.")
        improvements = result.get('improvements', "Next time, consider ways to get input from everyone involved or clarify what's most important.")
        verdict_text = {
            "ACCEPTABLE": "Based on your values, you made an ethically sound choice.",
            "CONDITIONAL": "There may be a few things to consider or talk through, but you did your best.",
            "PROBLEMATIC": "Everyone makes mistakes—what matters is learning for next time.",
            "INCOMPLETE": "I'd love a bit more detail so I can be the most helpful."
        }
        verdict = result.get('verdict', 'INCOMPLETE')
        return (
            f"Thank you for sharing your story—it's brave to reflect on our choices.\n"
            f"{verdict_text.get(verdict, '')}\n"
            f"• What went well: {positives}\n"
            f"• What to consider for next time: {improvements}\n"
            "Ethics is about learning and caring for yourself and others. If you want to talk through options, just ask!"
        )

    def _format_chat_response(self, result: Dict[str, Any]) -> str:
        """Format evaluation as natural conversation with three-level verdicts."""
        # Verdict display with emoji and text
        verdict_display = {
            'ACCEPTABLE': ('✅', 'ethically acceptable'),
            'CONDITIONAL': ('⚠️', 'acceptable with conditions (requires escalation and monitoring)'),
            'PROBLEMATIC': ('❌', 'ethically problematic')
        }
        
        verdict = result['verdict']
        emoji, verdict_text = verdict_display.get(verdict, ('❓', 'uncertain'))
        
        response = f"""{emoji} **{verdict}**

From a {self.ethical_framework['name']} perspective, this scenario is {verdict_text}.

**PAC Score:** {result['pac_score']:.2f}/1.0 (minimum required: {self.agent.pac_minimum})

**Analysis:**
{result.get('explanation', 'No explanation provided.')}
"""
        
        # Add verdict-specific guidance
        if verdict == 'CONDITIONAL':
            response += """

**⚠️ Conditions for Proceeding:**
{self._generate_conditions_for_proceeding(result)}
"""
        elif verdict == 'PROBLEMATIC':
            response += """

**❌ Recommendation:**
This action should not proceed without major revision to address ethical concerns.
"""
        
        # Show threshold analysis
        threshold_analysis = result.get('threshold_analysis', {})
        response += f"""

**Threshold Analysis:**
  {'✓' if threshold_analysis.get('pac_threshold_met') else '✗'} PAC Score: {result['pac_score']:.2f} {'≥' if threshold_analysis.get('pac_threshold_met') else '<'} {self.agent.pac_minimum}
  {'✓' if threshold_analysis.get('harm_threshold_met') else '✗'} Harm Level: {result['parameters'].get('harm_level', 0)}/5 {'≤' if threshold_analysis.get('harm_threshold_met') else '>'} {self.agent.harm_threshold}
  {'✓' if threshold_analysis.get('transparency_threshold_met') else '✗'} Transparency: {result['parameters'].get('transparency', 0):.2f} {'≥' if threshold_analysis.get('transparency_threshold_met') else '<'} {self.agent.transparency_min}
  {'✓' if threshold_analysis.get('consent_obtained') else '✗'} Informed Consent: {threshold_analysis.get('consent_obtained', False)}
"""
        
        # Show moral weights
        response += f"""

**Moral Weights Applied ({self.ethical_framework['name']}):**
{self._format_weights()}
"""
        
        # Show violations if any
        if result['violations']:
            response += f"\n**Constraints Violated:** {', '.join(result['violations'])}"
        
        return response
    
    def _format_weights(self) -> str:
        """Format current moral weights for display."""
        weights = self.agent.seraa.moral_state.weights
        return "\n".join([f"  • {k}: {v:.2f}" for k, v in sorted(weights.items(), key=lambda x: -x[1])])
    
    def get_conversation_summary(self) -> str:
        """Get summary of conversation history."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        # Count verdicts
        verdict_counts = {'ACCEPTABLE': 0, 'CONDITIONAL': 0, 'PROBLEMATIC': 0}
        for entry in self.conversation_history:
            verdict = entry['result']['verdict']
            if verdict in verdict_counts:
                verdict_counts[verdict] += 1
        
        summary = f"""**Conversation History ({len(self.conversation_history)} evaluations)**

**Verdict Summary:**
  ✅ Acceptable: {verdict_counts['ACCEPTABLE']}
  ⚠️ Conditional: {verdict_counts['CONDITIONAL']}
  ❌ Problematic: {verdict_counts['PROBLEMATIC']}

**Recent Evaluations:**
"""
        
        verdict_emoji = {
            'ACCEPTABLE': '✅',
            'CONDITIONAL': '⚠️',
            'PROBLEMATIC': '❌'
        }
        
        for i, entry in enumerate(self.conversation_history[-5:], 1):
            verdict = entry['result']['verdict']
            emoji = verdict_emoji.get(verdict, '❓')
            summary += f"\n{i}. {emoji} {entry['user'][:60]}..."
        
        return summary
    
    def get_threshold_info(self) -> str:
        """Get current threshold configuration for display."""
        thresholds = self.agent.get_threshold_info()
        return f"""**Current Thresholds:**
{thresholds['description']}

**What this means:**
• PAC Score ≥ {thresholds['pac_minimum']}: Minimum agency preservation required
• Harm Level ≤ {thresholds['harm_threshold']}: Maximum acceptable harm
• Transparency ≥ {thresholds['transparency_min']}: Minimum openness required

**Verdict Logic:**
• ACCEPTABLE: Meets all thresholds OR no harm with safeguards
• CONDITIONAL: Has consent + transparency, but below PAC/harm ideals
• PROBLEMATIC: Fails basic criteria
"""
    
    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []
        print("✓ Conversation history cleared")
    
    def explain_deeper(self, conversation_index: int = -1, user_concern: str = "") -> str:
        """
        Get deeper explanation for a specific evaluation.
        
        Args:
            conversation_index: Which conversation to explain (default: most recent)
            user_concern: Optional user question/disagreement
            
        Returns:
            Detailed explanation
        """
        if not self.conversation_history:
            return "No evaluations to explain yet."
        
        if conversation_index >= len(self.conversation_history):
            return f"Invalid index. Only {len(self.conversation_history)} evaluations exist."
        
        entry = self.conversation_history[conversation_index]
        result = entry['result']
        
        print(f"\n{'='*70}")
        print("GENERATING DEEPER EXPLANATION")
        print(f"{'='*70}")
        if user_concern:
            print(f"Addressing: {user_concern}")
        print()
        
        explanation = self.agent.explain_verdict(result, user_concern)
        
        formatted = f"""**Deeper Explanation for:** {result['question'][:60]}...

**Your Concern:** {user_concern if user_concern else "General clarification requested"}

{explanation}

**Current Verdict:** {result['verdict']}
**PAC Score:** {result['pac_score']:.2f} (minimum: {self.agent.pac_minimum})
**Harm Level:** {result['parameters'].get('harm_level', 0)}/5 (maximum: {self.agent.harm_threshold})

Need more clarification? You can ask follow-up questions anytime.
"""
        
        return formatted

