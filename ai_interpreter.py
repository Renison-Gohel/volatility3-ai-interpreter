import logging
import subprocess
import json
import os
import shutil
from typing import List, Dict, Any
from volatility3.framework import interfaces, renderers
from volatility3.framework.configuration import requirements
from volatility3.framework.interfaces import plugins

# Import the OpenAI library
try:
    from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI library not available. Install with 'pip install openai' for OpenAI backend support.")

vollog = logging.getLogger(__name__)

class AIInterpreter(plugins.PluginInterface):
    """AI Interpreter plugin for Volatility 3 that translates natural language queries to Volatility commands."""
    
    _required_framework_version = (2, 0, 0)
    _version = (1, 2, 0)  # Updated version to reflect new OpenAI library usage

    @classmethod
    def get_requirements(cls) -> List[interfaces.configuration.RequirementInterface]:
        return [
            requirements.TranslationLayerRequirement(
                name='primary',
                description='Memory layer for the kernel',
                architectures=["Intel32", "Intel64"]
            ),
            requirements.StringRequirement(
                name='query',
                description='Natural language query for memory analysis',
                optional=False
            ),
            requirements.StringRequirement(
                name='backend',
                description='AI backend to use (ollama or openai)',
                optional=True,
                default='ollama'
            ),
            requirements.StringRequirement(
                name='model',
                description='Model to use for AI processing',
                optional=True,
                default='llama3'
            ),
            requirements.StringRequirement(
                name='openai_api_key',
                description='OpenAI API key (required if backend=openai)',
                optional=True
            )
        ]

    def _detect_volatility_executable(self) -> str:
        """
        Detects the correct Volatility executable to use.
        In Kali, 'vol' is often available. Otherwise, we'll assume a standard vol.py installation.
        """
        # Check if 'vol' command is available (common in Kali)
        if shutil.which('vol'):
            vollog.info("Detected 'vol' command, likely Kali Linux environment.")
            return 'vol'
        else:
            # For standard installations, we would need the full path to vol.py
            # This is a simplification - in a real plugin, you might need to locate vol.py
            vollog.info("Using 'python3 vol.py' as the command.")
            return 'python3 vol.py'

    def _get_memory_file_path(self) -> str:
        """
        Retrieves the memory file path from the current Volatility context.
        """
        # Get the primary layer name from config
        primary_layer_name = self.config.get('primary', None)
        if not primary_layer_name:
            raise ValueError("Primary layer not found in configuration")
            
        # For WindowsIntel32e layers, the actual file location is in the memory_layer
        try:
            layer = self.context.layers[primary_layer_name]
            if hasattr(layer, 'config') and 'memory_layer' in layer.config:
                memory_layer_name = layer.config['memory_layer']
                memory_layer_location_path = f"plugins.{self.__class__.__name__}.{memory_layer_name}.location"
                location_uri = self.context.config.get(memory_layer_location_path, None)
                if location_uri and location_uri.startswith("file://"):
                    return location_uri[7:]  # Remove "file://" prefix
                elif location_uri:
                    return location_uri
                    
            # Try to get location from the layer config directly
            if hasattr(layer, 'config') and 'memory_layer.location' in layer.config:
                location_uri = layer.config['memory_layer.location']
                if location_uri.startswith("file://"):
                    return location_uri[7:]  # Remove "file://" prefix
                else:
                    return location_uri
                    
        except Exception as e:
            vollog.warning(f"Could not get location from layer object: {e}")
        
        # Fallback: Try common paths
        possible_paths = [
            f"plugins.{self.__class__.__name__}.primary.memory_layer.location",
            f"layers.{primary_layer_name}.location"
        ]
        
        for path in possible_paths:
            location_uri = self.context.config.get(path, None)
            if location_uri:
                vollog.info(f"Location found at path {path}: {location_uri}")
                if isinstance(location_uri, str) and location_uri.startswith("file://"):
                    return location_uri[7:]  # Remove "file://" prefix
                elif isinstance(location_uri, str):
                    return location_uri
        
        # If we still can't find it, let's try to get it from the file layer
        try:
            # Get the file layer
            file_layer_name = f"{primary_layer_name}_file_layer"
            if file_layer_name in self.context.layers:
                file_layer = self.context.layers[file_layer_name]
                if hasattr(file_layer, '_location') and file_layer._location:
                    location_uri = file_layer._location
                    if isinstance(location_uri, str) and location_uri.startswith("file://"):
                        return location_uri[7:]  # Remove "file://" prefix
                    elif isinstance(location_uri, str):
                        return location_uri
        except Exception as e:
            vollog.warning(f"Could not get location from file layer: {e}")
        
        raise ValueError(f"Could not find location for layer {primary_layer_name}")

    def _call_ollama_service(self, query: str) -> Dict[str, Any]:
        """
        Calls the Ollama service to interpret the natural language query.
        """
        # Get model from config or use default
        model = self.config.get('model', 'llama3')
        
        # Prompt for the AI service
        prompt = f"""
        You are a Volatility memory forensics expert. You are integrated into a Volatility 3 plugin.
        The user's request is: {query}
        
        Based on this request, generate the EXACT Volatility 3 command that achieves the goal.
        You must ONLY respond with a JSON object in the following format:
        {{
            "volatility_version": "3",
            "command": "volatility command with placeholders",
            "confidence": "high" or "low"
        }}
        
        Important instructions:
        1. ONLY use standard, well-known Volatility 3 plugins.
        2. ALWAYS specify volatility_version as "3".
        3. Use "<MEMORY_FILE>" as a placeholder for the memory file path.
        4. ONLY respond with the JSON, nothing else.
        5. Set "confidence" to "low" if you are not highly confident.
        6. Example command format: "vol -f <MEMORY_FILE> windows.pslist.PsList"
        
        Generate the command now:
        """
        
        # Try to import requests
        try:
            import requests
        except ImportError:
            vollog.error("Requests library not available. Please install with 'pip install requests'.")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        
        # Prepare the request for Ollama
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            # Make the request to Ollama
            response = requests.post(ollama_url, json=payload, timeout=60)
            response.raise_for_status()
            
            # Parse the response
            ai_response = response.json()
            response_text = ai_response.get('response', '')
            
            # Extract JSON from the response text
            # This is a simple extraction - in practice, you might need more robust parsing
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                vollog.error("Ollama service did not return valid JSON.")
                return {
                    "volatility_version": "unknown",
                    "command": "",
                    "confidence": "low"
                }
                
        except requests.exceptions.RequestException as e:
            vollog.error(f"Error calling Ollama service: {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        except json.JSONDecodeError as e:
            vollog.error(f"Error parsing Ollama response as JSON: {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        except Exception as e:
            vollog.error(f"Unexpected error in _call_ollama_service: {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }

    def _call_openai_service(self, query: str) -> Dict[str, Any]:
        """
        Calls the OpenAI service to interpret the natural language query.
        """
        # Check if OpenAI library is available
        if not OPENAI_AVAILABLE:
            vollog.error("OpenAI library not available. Please install with 'pip install openai'.")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        
        # Get API key and model from config
        api_key = self.config.get('openai_api_key', None)
        model = self.config.get('model', 'gpt-3.5-turbo')
        
        # Check if API key is provided
        if not api_key:
            vollog.error("OpenAI API key is required but not provided.")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        
        # Prompt for the AI service
        prompt = f"""
        You are a Volatility memory forensics expert. You are integrated into a Volatility 3 plugin.
        The user's request is: {query}
        
        Based on this request, generate the EXACT Volatility 3 command that achieves the goal.
        You must ONLY respond with a JSON object in the following format:
        {{
            "volatility_version": "3",
            "command": "volatility command with placeholders",
            "confidence": "high" or "low"
        }}
        
        Important instructions:
        1. ONLY use standard, well-known Volatility 3 plugins.
        2. ALWAYS specify volatility_version as "3".
        3. Use "<MEMORY_FILE>" as a placeholder for the memory file path.
        4. ONLY respond with the JSON, nothing else.
        5. Set "confidence" to "low" if you are not highly confident.
        6. Example command format: "vol -f <MEMORY_FILE> windows.pslist.PsList"
        
        Generate the command now:
        """
        
        try:
            # Create OpenAI client
            client = OpenAI(api_key=api_key)
            
            # Make the request to OpenAI
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from the response text
            # This is a simple extraction - in practice, you might need more robust parsing
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                vollog.error("OpenAI service did not return valid JSON.")
                return {
                    "volatility_version": "unknown",
                    "command": "",
                    "confidence": "low"
                }
                
        except APIConnectionError as e:
            vollog.error(f"Error connecting to OpenAI service: {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        except RateLimitError as e:
            vollog.error(f"OpenAI rate limit exceeded: {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        except APIStatusError as e:
            vollog.error(f"OpenAI API error (status {e.status_code}): {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }
        except Exception as e:
            vollog.error(f"Unexpected error calling OpenAI service: {e}")
            return {
                "volatility_version": "unknown",
                "command": "",
                "confidence": "low"
            }

    def _call_ai_service(self, query: str) -> Dict[str, Any]:
        """
        Calls the configured AI service to interpret the natural language query.
        """
        # Get backend from config or use default
        backend = self.config.get('backend', 'ollama')
        
        if backend == 'openai':
            return self._call_openai_service(query)
        else:  # Default to Ollama
            return self._call_ollama_service(query)

    def _validate_and_execute(self, ai_response: Dict[str, Any]) -> str:
        """
        Validates the AI response and executes the command if valid.
        """
        # Extract fields from AI response
        vol_version = ai_response.get("volatility_version", "unknown")
        command = ai_response.get("command", "")
        confidence = ai_response.get("confidence", "low")
        
        # Check confidence
        if confidence != "high":
            return "AI is not confident in the command generated. Please refine your query.\nSuggested command (unverified): " + command
        
        # Check version compatibility
        if vol_version != "3":
            return "AI generated command for Volatility " + vol_version + ", but this is Volatility 3. Command not executed.\nSuggested command: " + command
        
        # Get memory file path
        try:
            memory_file = self._get_memory_file_path()
        except Exception as e:
            return "Error getting memory file path: " + str(e) + "\nSuggested command: " + command
        
        # Replace placeholder with actual memory file path
        command = command.replace("<MEMORY_FILE>", memory_file)
        
        # Detect the correct executable
        volatility_executable = self._detect_volatility_executable()
        
        # For 'vol' command, we don't need to prepend python3
        # For vol.py, we would need to locate it properly
        if volatility_executable == 'vol':
            # Split command and replace the first part
            parts = command.split()
            if parts and (parts[0] == 'vol.py' or parts[0] == 'python3'):
                parts[0] = 'vol'
                command_to_execute = parts
            else:
                # If AI generated 'vol' correctly, use as is
                command_to_execute = command.split()
        else:
            # For standard vol.py installations, this would be more complex
            # For now, we'll just split the command
            command_to_execute = command.split()
        
        # Execute the command
        try:
            vollog.info("Executing command: " + " ".join(command_to_execute))
            result = subprocess.run(
                command_to_execute,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return "Command failed with return code " + str(result.returncode) + ":\n" + result.stderr
                
        except subprocess.TimeoutExpired:
            return "Command timed out after 5 minutes."
        except Exception as e:
            return "Error executing command: " + str(e)

    def run(self):
        """
        Main execution method for the plugin.
        """
        # Get the query from configuration
        query = self.config.get('query', None)
        if not query:
            return renderers.TreeGrid(
                [("Error", str)],
                [(0, ("No query provided. Use --query to specify your request.",))]
            )
        
        vollog.info("Received AI query: " + query)
        
        # Call AI service
        ai_response = self._call_ai_service(query)
        
        # Validate and execute
        execution_result = self._validate_and_execute(ai_response)
        
        # Return result in a TreeGrid
        return renderers.TreeGrid(
            [("AI Interpreter Result", str)],
            [(0, (execution_result,))]
        )