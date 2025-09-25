#!/bin/bash
# Installation script for AI Interpreter plugin

echo "AI Interpreter Plugin Installation Script"
echo "========================================"

# Try to find Volatility 3 installation
echo "Searching for Volatility 3 installation..."

# Common paths where Volatility 3 might be installed
possible_paths=(
    "/home/$USER/.local/lib/python*/site-packages/volatility3"
    "/home/$USER/.local/share/pipx/venvs/volatility3/lib/python*/site-packages/volatility3"
    "/usr/local/lib/python*/dist-packages/volatility3"
    "/usr/lib/python*/dist-packages/volatility3"
)

volatility_path=""
for path in "${possible_paths[@]}"; do
    # Use glob expansion
    for p in $path; do
        if [[ -d "$p" && -d "$p/framework/plugins" ]]; then
            volatility_path="$p"
            echo "Found Volatility 3 at: $volatility_path"
            break 2
        fi
    done
done

if [[ -z "$volatility_path" ]]; then
    echo "Error: Could not find Volatility 3 installation."
    echo "Please install Volatility 3 or specify the installation path manually."
    exit 1
fi

# Define the plugins directory
plugins_dir="$volatility_path/framework/plugins"

# Check if plugins directory exists
if [[ ! -d "$plugins_dir" ]]; then
    echo "Error: Plugins directory not found at $plugins_dir"
    exit 1
fi

# Copy the plugin file
echo "Copying plugin to $plugins_dir"
cp ai_interpreter.py "$plugins_dir/"

if [[ $? -eq 0 ]]; then
    echo "Plugin installed successfully!"
    
    # Verify installation
    if [[ -f "$plugins_dir/ai_interpreter.py" ]]; then
        echo "Verification: Plugin file exists in plugins directory."
    else
        echo "Warning: Could not verify plugin installation."
    fi
    
    echo ""
    echo "Next steps:"
    echo "1. Install Python requests: pip install requests"
    echo "2. For Ollama (local AI):"
    echo "   - Install Ollama from https://ollama.com/"
    echo "   - Pull a model: ollama pull llama3"
    echo "3. For OpenAI (cloud AI):"
    echo "   - Get an API key from https://platform.openai.com/"
    echo "4. Run the plugin:"
    echo "   - With Ollama: vol -f <memory_file> ai_interpreter --query \"<your query>\""
    echo "   - With OpenAI: vol -f <memory_file> ai_interpreter --query \"<your query>\" --backend openai --openai_api_key \"your-api-key\""
else
    echo "Error: Failed to copy plugin file."
    exit 1
fi