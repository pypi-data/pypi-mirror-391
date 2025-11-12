"""
Interactive custom framework creator
"""

from seraa.llm import SeraaChat
import json


def interactive_framework_creator():
    """Guide user through creating custom framework."""
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     SERAA CUSTOM FRAMEWORK CREATOR                               ║
╚══════════════════════════════════════════════════════════════════╝
    
Create your own ethical framework with custom values and weights.
    """)
    
    # Get framework name
    name = input("Framework name: ").strip()
    description = input("Description (optional): ").strip()
    
    # Get moral weights
    print("\nDefine moral weights (values will be normalized):")
    print("Enter weight name and value, or 'done' to finish")
    
    weights = {}
    while True:
        weight_name = input("  Weight name (or 'done'): ").strip()
        if weight_name.lower() == 'done':
            break
        try:
            weight_value = float(input(f"  Value for '{weight_name}': "))
            weights[weight_name] = weight_value
        except ValueError:
            print("    Invalid number, try again")
    
    if not weights:
        print("No weights defined, aborting")
        return
    
    # Get core values
    print("\nDefine core values (0.0-1.0 scale):")
    print("Enter value name and importance, or 'done' to finish")
    
    core_values = {}
    while True:
        value_name = input("  Value name (or 'done'): ").strip()
        if value_name.lower() == 'done':
            break
        try:
            importance = float(input(f"  Importance for '{value_name}' (0.0-1.0): "))
            core_values[value_name] = max(0.0, min(1.0, importance))
        except ValueError:
            print("    Invalid number, try again")
    
    if not core_values:
        print("No core values defined, aborting")
        return
    
    # Create framework
    try:
        framework = SeraaChat.create_custom_framework(
            name=name,
            weights=weights,
            core_values=core_values,
            description=description,
            save_path=f"frameworks/{name.lower().replace(' ', '_')}.json"
        )
        
        print("\n✓ Framework created successfully!")
        print(f"\nFramework: {framework['name']}")
        print(f"Description: {framework['description']}")
        print(f"\nWeights:")
        for k, v in framework['weights'].items():
            print(f"  • {k}: {v:.2f}")
        print(f"\nCore Values:")
        for k, v in framework['core_values'].items():
            print(f"  • {k}: {v:.2f}")
        
        # Test it
        test = input("\nTest your framework? (y/N): ").strip().lower()
        if test == 'y':
            chat = SeraaChat(
                custom_framework_path=f"frameworks/{name.lower().replace(' ', '_')}.json"
            )
            
            question = input("\nEnter ethical scenario to evaluate: ").strip()
            result = chat.chat(question)
            print(result['chat_response'])
            
    except Exception as e:
        print(f"\n❌ Error creating framework: {e}")


if __name__ == "__main__":
    interactive_framework_creator()
