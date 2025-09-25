#!/bin/bash

# AI Interpreter Plugin Installation Script for Volatility 3

set -e  # Exit on any error

echo "=== AI Interpreter Plugin Installer ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is not recommended."
    echo "Consider installing in user space instead."
    echo
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_NAME="ai_interpreter.py"
REQUIREMENTS_FILE="requirements.txt"

echo "Checking prerequisites..."
echo

# Check if Volatility 3 is installed
if ! command -v vol &> /dev/null; then
    print_error "Volatility 3 is not installed or not in PATH."
    echo "Please install Volatility 3 first: https://github.com/volatilityfoundation/volatility3"
    exit 1
fi

print_success "Volatility 3 is installed."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed."
    exit 1
fi

print_success "Python 3 is available."

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed."
    echo "Please install pip3: sudo apt install python3-pip"
    exit 1
fi

print_success "pip3 is available."

# Check if required files exist
if [ ! -f "$SCRIPT_DIR/$PLUGIN_NAME" ]; then
    print_error "Plugin file $PLUGIN_NAME not found in $SCRIPT_DIR"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/$REQUIREMENTS_FILE" ]; then
    print_error "Requirements file $REQUIREMENTS_FILE not found in $SCRIPT_DIR"
    exit 1
fi

print_success "Required files found."

echo
echo "=== Installing Dependencies ==="
echo

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r "$SCRIPT_DIR/$REQUIREMENTS_FILE" || {
    print_error "Failed to install Python dependencies."
    exit 1
}

print_success "Python dependencies installed."

echo
echo "=== Locating Volatility 3 Installation ==="
echo

# Try to find Volatility 3 installation directory
VOLATILITY_PLUGIN_DIRS=()

# Common locations for Volatility 3 plugins
COMMON_PLUGIN_PATHS=(
    "~/.local/share/pipx/venvs/volatility3/lib/python*/site-packages/volatility3/plugins"
    "~/.local/lib/python*/site-packages/volatility3/plugins"
    "/usr/local/lib/python*/dist-packages/volatility3/plugins"
    "/usr/lib/python*/dist-packages/volatility3/plugins"
    "~/.local/lib/python*/site-packages/volatility3/framework/plugins"
    "/usr/local/lib/python*/dist-packages/volatility3/framework/plugins"
    "/usr/lib/python*/dist-packages/volatility3/framework/plugins"
)

echo "Searching for Volatility 3 plugin directories..."
FOUND=false

for path_pattern in "${COMMON_PLUGIN_PATHS[@]}"; do
    # Expand tilde and glob patterns
    expanded_paths=$(eval echo $path_pattern)
    for path in $expanded_paths; do
        if [ -d "$path" ]; then
            VOLATILITY_PLUGIN_DIRS+=("$path"
echo "Found plugin directory: $path"
            FOUND=true
        fi
    done
done

if [ "$FOUND" = false ]; then
    print_error "Could not find Volatility 3 plugin directory automatically."
    echo "Please specify the plugin directory manually:"
    echo "  cp $PLUGIN_NAME /path/to/volatility3/plugins/"
    exit 1
fi

echo
echo "=== Installing Plugin ==="
echo

# Copy plugin to all found directories
INSTALL_SUCCESS=false

for plugin_dir in "${VOLATILITY_PLUGIN_DIRS[@]}"; do
    echo "Attempting to install plugin to: $plugin_dir"
    
    # Try to copy the plugin
    if cp "$SCRIPT_DIR/$PLUGIN_NAME" "$plugin_dir/" 2>/dev/null; then
        print_success "Plugin installed to $plugin_dir"
        INSTALL_SUCCESS=true
    else
        print_warning "Failed to install to $plugin_dir (permission denied?)"
    fi
done

if [ "$INSTALL_SUCCESS" = false ]; then
    print_error "Failed to install plugin to any directory."
    echo "Try running with sudo or manually copying the plugin:"
    echo "  sudo cp $SCRIPT_DIR/$PLUGIN_NAME ${VOLATILITY_PLUGIN_DIRS[0]}/"
    exit 1
fi

print_success "Plugin installation completed!"

echo
echo "=== Verifying Installation ==="
echo

# Verify installation
echo "Checking if plugin is recognized by Volatility..."
if vol -h | grep -q "ai_interpreter"; then
    print_success "Plugin successfully installed and recognized by Volatility!"
else
    print_warning "Plugin installed but not recognized. You may need to restart your terminal."
fi

echo
echo "=== Installation Complete ==="
echo
print_success "AI Interpreter plugin has been successfully installed!"
echo
echo "Next steps:"
echo "1. If using Ollama backend:"
echo "   - Install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
echo "   - Pull a model: ollama pull llama3"
echo
echo "2. If using OpenAI backend:"
echo "   - Get an API key from https://platform.openai.com/"
echo
echo "3. Test the plugin:"
echo "   vol -f <memory_file> ai_interpreter.AIInterpreter --query \"What is the operating system?\""
echo
echo "For more information, see the README.md file."
echo