"""
examples/llm_cli.py - Command-line interface for LLM + SERAA ethics

Usage:
    python examples/llm_cli.py
    python examples/llm_cli.py --backend openai --model gpt-4
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from seraa.llm.ethical_agent import EthicalLLMAgent
import argparse


def main():
    parser = argparse.ArgumentParser(description="LLM + SERAA Ethical Agent")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "openai", "anthropic"])
    parser.add_argument("--model", default="llama2", help="Model name")
    parser.add_argument("--domain", default="general", choices=["general", "government", "corporate", "tech"])
    
    args = parser.parse_args()
    
    print("="*70)
    print("LLM + SERAA ETHICAL AGENT")
    print("="*70)
    
    agent = EthicalLLMAgent(
        llm_backend=args.backend,
        model=args.model,
        seraa_domain=args.domain
    )
    
    # Test questions
    test_questions = [
        "Is it ethical for a social media company to use user data for AI training without explicit consent?",
        
        "Should hospitals prioritize younger patients over older patients during resource shortages?",
        
        "Is it acceptable for employers to monitor employee emails and messages without notification?",
        
        "Should autonomous vehicles prioritize passenger safety over pedestrian safety?",
        
        "Is it ethical for governments to implement mass surveillance for national security?"
    ]
    
    print("\n" + "="*70)
    print("EVALUATING 5 ETHICAL SCENARIOS")
    print("="*70)
    
    for i, question in enumerate(test_questions, 1):
        result = agent.evaluate_question(question)
        
        print(f"\n{'='*70}")
        print(f"RESULT {i}/5")
        print(f"{'='*70}")
        print(f"Verdict: {result['verdict']}")
        print(f"PAC Score: {result['pac_score']:.2f}/1.0")
        print(f"\nExplanation:")
        print(result['explanation'])
        
        if result['violations']:
            print(f"\nViolations: {', '.join(result['violations'])}")
    
    print("\n" + "="*70)
    print("EVALUATION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
