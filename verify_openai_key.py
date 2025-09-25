#!/usr/bin/env python3
"""
Script to verify OpenAI API key and check available models.
"""

import openai
import sys

def verify_api_key(api_key):
    """Verify OpenAI API key."""
    try:
        client = openai.OpenAI(api_key=api_key)
        # Try to list models to verify the key
        models = client.models.list()
        return True, "API key is valid"
    except openai.AuthenticationError:
        return False, "Invalid API key"
    except openai.APIConnectionError:
        return False, "Cannot connect to OpenAI API"
    except openai.RateLimitError:
        return False, "Rate limit exceeded"
    except openai.APIStatusError as e:
        return False, f"API error: {e.status_code} - {e.message}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def list_models(api_key):
    """List available models for the API key."""
    try:
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        return [model.id for model in models.data]
    except Exception:
        return []

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python3 verify_openai_key.py <api_key>")
        print("Example: python3 verify_openai_key.py sk-your-api-key-here")
        return 1
    
    api_key = sys.argv[1]
    
    print("=== OpenAI API Key Verifier ===\n")
    
    # Verify API key
    print("1. Verifying API key...")
    valid, message = verify_api_key(api_key)
    if valid:
        print(f"   ✓ {message}")
    else:
        print(f"   ✗ {message}")
        return 1
    
    # List available models
    print("\n2. Available models:")
    models = list_models(api_key)
    if models:
        # Sort models for better presentation
        models.sort()
        for model in models:
            print(f"   ✓ {model}")
    else:
        print("   Unable to retrieve models")
    
    print("\n=== API key verification successful! ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())