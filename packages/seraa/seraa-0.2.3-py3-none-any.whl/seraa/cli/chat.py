"""
seraa/cli/chat.py - Interactive chat CLI for SERAA
"""
import argparse
from ..llm.chat_agent import SeraaChat  # <-- fix import, no trailing comma
from .constraint_explanations import CONSTRAINT_EXPLANATIONS

def parse_custom_values(values_str: str) -> dict:
    """Parse custom values from command line string."""
    if not values_str:
        return {}
    values = {}
    for pair in values_str.split(','):
        key, val = pair.strip().split('=')
        values[key.strip()] = float(val.strip())
    return values

def print_constraint_analysis(result):
    print("\nConstraint Analysis:")
    violated = result.get('violated_constraints', [])
    satisfied = result.get('satisfied_constraints', [])
    shown = set()
    for c in violated:
        explain = CONSTRAINT_EXPLANATIONS.get(c, {"label": c, "why": ""})
        print(f"  ❌ {explain['label']}: {explain['why']}")
        shown.add(c)
    for c in satisfied:
        if c not in shown:
            explain = CONSTRAINT_EXPLANATIONS.get(c, {"label": c, "why": ""})
            print(f"  ✅ {explain['label']}: {explain['why']}")

def print_tip(result):
    if result.get('violated_constraints'):
        print("\nTip: The problems marked ❌ above should be fixed for an improved ethical outcome.")

def main():
    parser = argparse.ArgumentParser(description="SERAA Interactive Chat Agent")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "openai", "anthropic"])
    parser.add_argument("--model", default="qwen2.5:1.5b", help="Model name")
    parser.add_argument("--domain", default="general", choices=["general", "government", "corporate", "tech"])
    parser.add_argument(
        "--framework",
        default="secular",
        help="Ethical framework to apply (Choose from predefined frameworks or create your own)"
    )
    parser.add_argument(
        "--values",
        default="",
        help="Custom moral weights (e.g., 'compassion=0.4,justice=0.3,wisdom=0.3')"
    )
    args = parser.parse_args()
    custom_values = parse_custom_values(args.values)
    framework = args.framework

    # Load available/predefined frameworks
    AvailableFrameworks = getattr(SeraaChat, 'FRAMEWORKS', [
        "secular", "christian", "buddhist", "ubuntu", "stoic", "virtue_ethics"
        # add more defaults if SeraaChat doesn't have attribute
    ])

    # Handle custom framework and values
    if framework not in AvailableFrameworks:
        print(f"\nCreating custom ethical framework: '{framework}'")
        print("Available predefined frameworks:", ", ".join(AvailableFrameworks))
        if not custom_values:
            print("\nYou didn't specify any custom values. Let's create them!")
            print("Enter values as 'value=weight', separated by commas (e.g., compassion=0.4,justice=0.3):")
            user_values = input("Enter custom moral values: ").strip()
            custom_values = parse_custom_values(user_values)
            print(f"Custom values set: {custom_values}")
        else:
            print(f"Using provided custom values: {custom_values}")
    else:
        print(f"\nUsing predefined ethical framework: '{framework}'")
        if custom_values:
            print("Note: Custom values will be ignored when using a predefined framework.")
        else:
            print("Using default values for the selected framework.")

    print("="*70)
    print("SERAA INTERACTIVE CHAT AGENT")
    print("="*70)
    print()
    chat = SeraaChat(
        llm_backend=args.backend,
        model=args.model,
        seraa_domain=args.domain,
        custom_values=custom_values,
        ethical_framework=framework
    )
    print()
    print("="*70)
    print("Commands:")
    print("  - Ask any question or describe a scenario to get ethical analysis.")
    print("  - 'history' - View conversation history")
    print("  - 'weights' - View current moral weights")
    print("  - 'reset' - Clear conversation history")
    print("  - 'quit' or 'exit' - Exit chat")
    print("="*70)
    print()
    while True:
        try:
            user_input = input("\n🤔 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            if user_input.lower() == 'history':
                print("\n" + chat.get_conversation_summary())
                continue
            if user_input.lower() == 'weights':
                print("\n**Current Moral Weights:**")
                print(chat._format_weights())
                continue
            if user_input.lower() == 'reset':
                chat.reset()
                continue
            print("\n🤖 SERAA: Analyzing...\n")
            result = chat.chat(user_input)
            print_constraint_analysis(result)
            print(f"\nEthical Verdict: {result.get('verdict', 'Unknown')}\n")
            print(result.get('plain_explanation', result.get('chat_response', '')))
            print_tip(result)
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}")

if __name__ == "__main__":
    main()
