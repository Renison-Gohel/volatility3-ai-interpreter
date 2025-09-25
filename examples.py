#!/usr/bin/env python3
"""
Example usage scripts for the AI Interpreter plugin.
"""

EXAMPLES = {
    "os_detection": {
        "description": "Detect the operating system of a memory dump",
        "command": "vol -f memory_dump.raw ai_interpreter.AIInterpreter --query \"What is the operating system of this memory dump?\" --backend openai --openai-api-key YOUR_API_KEY --model gpt-4"
    },
    "process_list": {
        "description": "List all running processes",
        "command": "vol -f memory_dump.raw ai_interpreter.AIInterpreter --query \"List all running processes\" --backend ollama --model llama3"
    },
    "network_connections": {
        "description": "Show network connections and listening ports",
        "command": "vol -f memory_dump.raw ai_interpreter.AIInterpreter --query \"Show me all network connections and listening ports\" --backend openai --openai-api-key YOUR_API_KEY"
    },
    "browser_history": {
        "description": "Extract browser history if available",
        "command": "vol -f memory_dump.raw ai_interpreter.AIInterpreter --query \"Extract Chrome browser history if available\" --backend ollama --model mistral"
    },
    "malware_detection": {
        "description": "Find potential malware or suspicious processes",
        "command": "vol -f memory_dump.raw ai_interpreter.AIInterpreter --query \"Find any suspicious processes or potential malware injections\" --backend openai --openai-api-key YOUR_API_KEY --model gpt-4-turbo"
    }
}

def print_example(name):
    """Print a specific example."""
    if name in EXAMPLES:
        example = EXAMPLES[name]
        print(f"\n{example['description']}:")
        print("-" * len(example['description']))
        print(f"$ {example['command']}\n")
    else:
        print(f"Example '{name}' not found. Available examples:")
        for key in EXAMPLES.keys():
            print(f"  - {key}")

def print_all_examples():
    """Print all examples."""
    print("=== AI Interpreter Plugin Usage Examples ===\n")
    
    for name, example in EXAMPLES.items():
        print(f"{example['description']}:")
        print("-" * len(example['description']))
        print(f"$ {example['command']}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Print specific example
        print_example(sys.argv[1])
    else:
        # Print all examples
        print_all_examples()
        print("To run a specific example:")
        print("  python3 examples.py <example_name>")
        print("\nAvailable example names:")
        for key in EXAMPLES.keys():
            print(f"  - {key}")