#!/usr/bin/env python3
"""
Script to check if Ollama is running and available.
"""

import requests
import sys
import subprocess

def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        # Try to connect to Ollama API
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return True, "Ollama is running and accessible"
        else:
            return False, f"Ollama returned status code {response.status_code}"
    except requests.exceptions.ConnectionError:
        # Ollama is not running or not accessible
        return False, "Ollama is not running or not accessible on localhost:11434"
    except requests.exceptions.Timeout:
        return False, "Ollama connection timed out"
    except Exception as e:
        return False, f"Error checking Ollama: {str(e)}"

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "Ollama command failed"
    except FileNotFoundError:
        return False, "Ollama is not installed"
    except Exception as e:
        return False, f"Error checking Ollama installation: {str(e)}"

def list_models():
    """List available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
        else:
            return []
    except Exception:
        return []

def main():
    """Main function."""
    print("=== Ollama Status Checker ===\n")
    
    # Check if Ollama is installed
    print("1. Checking Ollama installation...")
    installed, version_info = check_ollama_installed()
    if installed:
        print(f"   ✓ {version_info}")
    else:
        print(f"   ✗ {version_info}")
        print("     Install Ollama from: https://ollama.com/download")
        return 1
    
    # Check if Ollama is running
    print("\n2. Checking Ollama service...")
    running, status = check_ollama_running()
    if running:
        print(f"   ✓ {status}")
    else:
        print(f"   ✗ {status}")
        print("     Start Ollama service: ollama serve")
        print("     Or on systemd systems: systemctl start ollama")
        return 1
    
    # List available models
    print("\n3. Available models:")
    models = list_models()
    if models:
        for model in models:
            print(f"   ✓ {model}")
    else:
        print("   No models found")
        print("   Pull a model: ollama pull llama3")
    
    print("\n=== Ollama is ready for use! ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())