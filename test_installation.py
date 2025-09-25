#!/usr/bin/env python3
"""
Test script to verify AI Interpreter plugin installation and functionality.
"""

import sys
import os
import subprocess

def check_volatility_installed():
    \"\"\"Check if Volatility 3 is installed.\"\"\"
    try:
        result = subprocess.run(['vol', '--help'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_plugin_available():
    \"\"\"Check if AI Interpreter plugin is available.\"\"\"
    try:
        result = subprocess.run(['vol', '-h'], 
                              capture_output=True, text=True, timeout=10)
        return 'ai_interpreter' in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_dependencies():
    \"\"\"Check if required Python dependencies are installed.\"\"\"
    dependencies = []
    missing_deps = []
    
    # Check for OpenAI
    try:
        import openai
        dependencies.append(('openai', openai.__version__))
    except ImportError:
        missing_deps.append('openai')
    
    # Check for requests
    try:
        import requests
        dependencies.append(('requests', requests.__version__))
    except ImportError:
        missing_deps.append('requests')
    
    return dependencies, missing_deps

def main():
    \"\"\"Main test function.\"\"\"
    print(\"=== AI Interpreter Plugin Test ===\\n\")
    
    # Test 1: Check Volatility installation
    print(\"1. Checking Volatility 3 installation...\")
    if check_volatility_installed():
        print(\"   ✓ Volatility 3 is installed\")
    else:
        print(\"   ✗ Volatility 3 is not installed\")
        print(\"     Please install Volatility 3: https://github.com/volatilityfoundation/volatility3\")
        return 1
    
    # Test 2: Check plugin availability
    print(\"\\n2. Checking AI Interpreter plugin availability...\")
    if check_plugin_available():
        print(\"   ✓ AI Interpreter plugin is available\")
    else:
        print(\"   ✗ AI Interpreter plugin is not available\")
        print(\"     Please install the plugin using the installation script or manually\")
        return 1
    
    # Test 3: Check dependencies
    print(\"\\n3. Checking Python dependencies...\")
    dependencies, missing_deps = check_dependencies()
    
    if dependencies:
        for dep, version in dependencies:
            print(f\"   ✓ {dep} ({version})\")
    
    if missing_deps:
        for dep in missing_deps:
            print(f\"   ✗ {dep} (missing)\")
        print(\"     Install missing dependencies: pip install {}\".format(' '.join(missing_deps)))
        return 1
    else:
        print(\"   ✓ All required dependencies are installed\")
    
    print(\"\\n=== All Tests Passed ===\")
    print(\"The AI Interpreter plugin is properly installed and ready to use!\")
    print(\"\\nNext steps:\")
    print(\"1. If using Ollama backend:\")
    print(\"   - Install Ollama: curl -fsSL https://ollama.com/install.sh | sh\")
    print(\"   - Pull a model: ollama pull llama3\")
    print(\"\\n2. If using OpenAI backend:\")
    print(\"   - Get an API key from https://platform.openai.com/\")
    print(\"\\n3. Test the plugin:\")
    print(\"   vol -f <memory_file> ai_interpreter.AIInterpreter --query \\\"What is the operating system?\\\"\")
    
    return 0

if __name__ == \"__main__\":
    sys.exit(main())
