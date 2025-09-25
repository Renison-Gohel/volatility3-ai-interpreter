# AI Interpreter Plugin for Volatility 3

[![Volatility 3](https://img.shields.io/badge/Volatility-3-blue)](https://github.com/volatilityfoundation/volatility3)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/downloads/)


The AI Interpreter plugin for Volatility 3 translates natural language queries into Volatility commands, making memory forensics more accessible to both beginners and experienced analysts.

## Features

- 🤖 **AI-Powered Interpretation**: Translate natural language queries into Volatility commands
- 🔌 **Multiple AI Backends**: Support for both OpenAI (cloud) and Ollama (local) backends
- 🛡️ **Hallucination Reduction**: Validates AI-generated commands before execution
- ⚡ **Fast Execution**: Direct command execution with proper error handling
- 🌐 **Cross-Platform**: Works on Kali Linux, Ubuntu, and other Linux distributions
- 🔒 **Secure**: Validates commands and implements proper API key handling

## Requirements

### Core Dependencies
- Volatility 3 Framework 2.0+
- Python 3.8+
- `openai` Python library (for OpenAI backend)
- `requests` Python library (for Ollama backend)

### AI Backend Options
Choose one or both:

#### OpenAI Backend
- OpenAI API key
- Internet connectivity
- Supported models: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo`, etc.

#### Ollama Backend (Local)
- [Ollama](https://ollama.com/) installed and running locally
- Supported models: `llama3`, `mistral`, `codellama`, etc.

## Installation

### 1. Install Dependencies

```bash
# Install required Python packages
pip install openai requests

# Or if using pipx (recommended for Volatility)
pipx inject volatility3 openai requests
```

### 2. Install Ollama (Optional for Local AI)

```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model for local processing
ollama pull llama3
```

### 3. Install the Plugin

```bash
# Clone the repository
git clone https://github.com/yourusername/volatility3-ai-interpreter.git
cd volatility3-ai-interpreter

# Copy the plugin to Volatility's plugins directory
# Find your Volatility plugins directory:
find ~/.local -name "plugins" -type d | grep volatility

# Copy the plugin (replace with your actual path):
cp ai_interpreter.py ~/.local/share/pipx/venvs/volatility3/lib/python3.13/site-packages/volatility3/plugins/

# Or if using system-wide Volatility installation:
sudo cp ai_interpreter.py /usr/local/lib/python3.13/dist-packages/volatility3/plugins/
```

### 4. Verify Installation

```bash
# Check if the plugin is available
vol -h | grep ai_interpreter

# Check plugin-specific help
vol -f <memory_file> ai_interpreter.AIInterpreter -h
```

## Usage

### Basic Syntax

```bash
vol -f <memory_file> ai_interpreter.AIInterpreter --query "<natural_language_query>" [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--query QUERY` | Natural language query for memory analysis | *Required* |
| `--backend BACKEND` | AI backend to use (`ollama` or `openai`) | `ollama` |
| `--model MODEL` | Model to use for AI processing | `llama3` (Ollama) or `gpt-3.5-turbo` (OpenAI) |
| `--openai-api-key KEY` | OpenAI API key (required if backend=openai) | *None* |

### Examples

#### Using OpenAI Backend

```bash
# Get operating system information
vol -f memory_dump.raw ai_interpreter.AIInterpreter \
  --query "What is the operating system of this memory dump?" \
  --backend openai \
  --openai-api-key sk-your-api-key-here \
  --model gpt-4

# List running processes
vol -f memory_dump.raw ai_interpreter.AIInterpreter \
  --query "List all running processes" \
  --backend openai \
  --openai-api-key sk-your-api-key-here

# Find network connections
vol -f memory_dump.raw ai_interpreter.AIInterpreter \
  --query "Show me all network connections and listening ports" \
  --backend openai \
  --openai-api-key sk-your-api-key-here
```

#### Using Ollama Backend (Local)

```bash
# Get operating system information
vol -f memory_dump.raw ai_interpreter.AIInterpreter \
  --query "What is the operating system of this memory dump?" \
  --backend ollama \
  --model llama3

# List running processes
vol -f memory_dump.raw ai_interpreter.AIInterpreter \
  --query "List all running processes" \
  --backend ollama

# Extract browser history
vol -f memory_dump.raw ai_interpreter.AIInterpreter \
  --query "Extract Chrome browser history if available" \
  --backend ollama \
  --model mistral
```

## Sample Outputs

### Operating System Detection
```
Volatility 3 Framework 2.26.0

Variable        Value

Kernel Base     0xf80002601000
DTB             0x187000
Symbols         file:///home/user/.local/share/pipx/venvs/volatility3/lib/python3.13/site-packages/volatility3/symbols/windows/ntkrnlmp.pdb/3844DBB920174967BE7AA4A2C20430FA-2.json.xz
Is64Bit         True
IsPAE           False
layer_name      0 WindowsIntel32e
memory_layer    1 FileLayer
KdDebuggerDataBlock     0xf800027f20a0
NTBuildLab      7601.17514.amd64fre.win7sp1_rtm.
CSDVersion      1
KdVersionBlock  0xf800027f2068
Major/Minor     15.7601
MachineType     34404
KeNumberProcessors      1
SystemTime      2019-12-14 10:38:46+00:00
NtSystemRoot    C:\\Windows
NtProductType   NtProductWinNt
NtMajorVersion  6
NtMinorVersion  1
PE MajorOperatingSystemVersion 6
PE MinorOperatingSystemVersion  1
PE Machine      34404
PE TimeDateStamp        Sat Nov 20 09:30:02 2010
```

### Process List
```
Volatility 3 Framework 2.26.0

PID     PPID    ImageFileName   Offset(V)       Threads Handles SessionId      Wow64   CreateTime      ExitTime        File output

4       0       System          0xfa8000ca0040  80      541     N/A     False   2019-12-14 10:35:21.000000 UTC  N/A     Disabled
248     4       smss.exe        0xfa80014976c0  3       37      N/A     False   2019-12-14 10:35:21.000000 UTC  N/A     Disabled
320     312     csrss.exe       0xfa80014fdb30  10      446     0       False   2019-12-14 10:35:27.000000 UTC  N/A     Disabled
...
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Plugin Not Recognized
**Problem**: `vol -h` doesn't show the AI Interpreter plugin
**Solution**: 
```bash
# Verify the plugin is in the correct directory
ls ~/.local/share/pipx/venvs/volatility3/lib/python3.13/site-packages/volatility3/plugins/ | grep ai_interpreter

# If not, copy it manually
cp ai_interpreter.py ~/.local/share/pipx/venvs/volatility3/lib/python3.13/site-packages/volatility3/plugins/
```

#### 2. Missing Dependencies
**Problem**: Import errors for `openai` or `requests`
**Solution**:
```bash
# Install missing packages
pip install openai requests

# Or for pipx installations
pipx inject volatility3 openai requests
```

#### 3. Ollama Service Not Running
**Problem**: Connection errors when using Ollama backend
**Solution**:
```bash
# Start Ollama service
systemctl start ollama
# or
ollama serve

# Verify service is running
curl http://localhost:11434/api/tags
```

#### 4. OpenAI API Key Issues
**Problem**: Authentication errors with OpenAI backend
**Solution**:
```bash
# Verify API key format (should start with sk-)
echo "sk-your-api-key" | grep "^sk-"

# Test API key with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-your-api-key"
```

#### 5. Model Not Found
**Problem**: "Model not found" errors
**Solution**:
```bash
# For Ollama, pull the required model
ollama pull llama3

# List available models
ollama list
```

#### 6. Memory File Path Issues
**Problem**: "Could not find location for layer" errors
**Solution**: This usually indicates an issue with the memory file. Verify:
- The file exists and is readable
- The file is a valid memory dump
- Try with a different memory dump file

### Debugging Tips

Enable verbose logging to diagnose issues:
```bash
# Run with verbose output
vol -vv -f memory_dump.raw ai_interpreter.AIInterpreter --query "List processes"
```

Check Volatility's plugin loading:
```bash
# See all loaded plugins
vol -h | grep -A 50 "PLUGIN"
```

## Security Considerations

### Command Validation
The plugin implements several safeguards to prevent execution of malicious commands:
- Validates AI-generated commands against known Volatility patterns
- Checks Volatility version compatibility
- Confirms AI confidence level before execution
- Sanitizes command strings before execution

### API Key Security
- Never commit API keys to version control
- Use environment variables for API keys in production
- Rotate API keys regularly
- Monitor API usage through vendor dashboards

### Data Privacy
- With Ollama backend: All processing happens locally
- With OpenAI backend: Queries and memory file names are sent to OpenAI
- Consider data sensitivity when choosing backend

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The AI Interpreter plugin builds upon the Volatility 3 Framework, which is licensed separately. Please see the [Volatility Foundation](https://www.volatilityfoundation.org/license/vsl-v1.0) for details.

## Acknowledgments

- Thanks to the [Volatility Foundation](https://www.volatilityfoundation.org/) for the amazing memory forensics framework
- Thanks to [OpenAI](https://openai.com/) for providing powerful AI models
- Thanks to [Ollama](https://ollama.com/) for making local AI accessible
- Inspired by the need to make digital forensics more accessible to everyone

---

**Note**: This plugin is designed for legitimate security research and digital forensics purposes. Always ensure you have proper authorization before analyzing memory dumps.
