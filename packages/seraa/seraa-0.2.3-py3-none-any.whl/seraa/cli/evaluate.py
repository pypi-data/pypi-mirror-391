"""
seraa/cli/evaluate.py - Batch evaluation CLI for SERAA
"""

import argparse
from ..llm.ethical_agent import EthicalLLMAgent


def main():
    parser = argparse.ArgumentParser(description="SERAA Ethical Evaluation")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "openai", "anthropic"])
    parser.add_argument("--model", default="qwen2.5:1.5b", help="Model name")
    parser.add_argument("--domain", default="general", choices=["general", "government", "corporate", "tech"])
    
    args = parser.parse_args()
    
    print("="*70)
    print("LLM + SERAA ETHICAL AGENT")
    print("="*70)
    
    # Initialize agent
    agent = EthicalLLMAgent(
        llm_backend=args.backend,
        model=args.model,
        seraa_domain=args.domain
    )
    
    # Example scenarios
    scenarios = [
        "Is it ethical for a social media company to use user data for AI training without explicit consent?",
        "Should hospitals prioritize younger patients over older patients during resource shortages?",
        "Is it acceptable for employers to monitor employee emails and messages without notification?",
        "Should autonomous vehicles prioritize passenger safety over pedestrian safety?",
        "Is it ethical for governments to implement mass surveillance for national security?"
    ]
    
    print()
    print("="*70)
    print(f"EVALUATING {len(scenarios)} ETHICAL SCENARIOS")
    print("="*70)
    
    results = []
    for i, scenario in enumerate(scenarios, 1):
        result = agent.evaluate_question(scenario)
        results.append(result)
        
        print()
        print("="*70)
        print(f"RESULT {i}/{len(scenarios)}")
        print("="*70)
        print(f"Verdict: {result['verdict']}")
        print(f"PAC Score: {result['pac_score']:.2f}/1.0")
        print()
        print(f"Explanation:\n{result['explanation']}")
        if result['violations']:
            print(f"\nViolations: {', '.join(result['violations'])}")
    
    print()
    print("="*70)
    print("EVALUATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
