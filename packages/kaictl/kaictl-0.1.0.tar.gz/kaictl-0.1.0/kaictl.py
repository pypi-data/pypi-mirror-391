#!/usr/bin/env python3
"""
KaiCTL - Kubernetes AI Control
Natural Language Interface for kubectl
"""

import os
import subprocess
import sys
import json
import requests
from pathlib import Path
import tempfile
from datetime import datetime

def load_env():
    """Load environment variables from .env file"""
    # Check home directory first
    home_env = Path.home() / '.kaictl' / '.env'
    local_env = Path('.env')
    
    env_path = home_env if home_env.exists() else local_env
    
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def initialize_config():
    """Initialize ~/.kaictl directory and .env template if not exists"""
    kaictl_dir = Path.home() / '.kaictl'
    env_file = kaictl_dir / '.env'
    
    # Create directory if it doesn't exist
    if not kaictl_dir.exists():
        kaictl_dir.mkdir(parents=True, exist_ok=True)
        print(f"✨ Created config directory: {kaictl_dir}")
    
    # Interactive setup if .env doesn't exist
    if not env_file.exists():
        print("\n" + "=" * 60)
        print("🎉 WELCOME TO KaiCTL - First Time Setup")
        print("=" * 60)
        print("\nKaiCTL needs an AI provider to translate natural language")
        print("to kubectl commands. Choose your preferred provider:\n")
        
        print("1. 🤖 Claude (Anthropic) - Cloud-based, very powerful")
        print("   • Requires API key (paid)")
        print("   • Get key from: https://console.anthropic.com/")
        print("   • Best accuracy and reliability\n")
        
        print("2. 🦙 Ollama - Local LLM, runs on your machine")
        print("   • Free and private")
        print("   • Requires installation and model download")
        print("   • Good performance for most tasks\n")
        
        while True:
            choice = input("Choose provider (1 for Claude, 2 for Ollama): ").strip()
            
            if choice == '1':
                # Claude setup
                print("\n📝 Setting up Claude (Anthropic)...")
                print("\nTo get your API key:")
                print("  1. Visit: https://console.anthropic.com/")
                print("  2. Sign in or create an account")
                print("  3. Go to API Keys section")
                print("  4. Create a new API key\n")
                
                api_key = input("Enter your Anthropic API key (or 'skip' to configure later): ").strip()
                
                if api_key.lower() == 'skip' or not api_key:
                    api_key = 'your_anthropic_api_key_here'
                    print("⚠️  You'll need to add your API key later to use Claude")
                
                config_content = f"""# KaiCTL Configuration
# Kubernetes AI Control - Natural Language Interface for kubectl

# AI Provider Configuration
AI_PROVIDER=claude

# Claude API Configuration (Anthropic)
ANTHROPIC_API_KEY={api_key}

# Ollama Configuration (not used but available)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
"""
                
                with open(env_file, 'w') as f:
                    f.write(config_content)
                
                print(f"\n✅ Configuration saved to: {env_file}")
                
                if api_key == 'your_anthropic_api_key_here':
                    print("\n⚠️  Remember to add your API key before using KaiCTL:")
                    print(f"   Edit: {env_file}")
                    return False
                else:
                    print("\n✨ Setup complete! Starting KaiCTL...\n")
                    return True
            
            elif choice == '2':
                # Ollama setup
                print("\n🦙 Setting up Ollama...")
                print("\nOllama must be installed and running on your system.")
                
                # Check if Ollama is accessible
                try:
                    response = requests.get('http://localhost:11434/api/tags', timeout=2)
                    ollama_running = response.status_code == 200
                except:
                    ollama_running = False
                
                if not ollama_running:
                    print("\n❌ Ollama is not running or not installed.")
                    print("\nTo install Ollama:")
                    print("  macOS/Linux: curl -fsSL https://ollama.com/install.sh | sh")
                    print("  Windows: Download from https://ollama.com\n")
                    print("After installation, run: ollama serve\n")
                    
                    retry = input("Is Ollama running now? (yes/no): ").strip().lower()
                    if retry not in ['yes', 'y']:
                        print("\n⚠️  Please install and start Ollama, then run KaiCTL again.")
                        return False
                    
                    # Check again
                    try:
                        response = requests.get('http://localhost:11434/api/tags', timeout=2)
                        ollama_running = response.status_code == 200
                    except:
                        ollama_running = False
                    
                    if not ollama_running:
                        print("❌ Still cannot connect to Ollama. Please check your installation.")
                        return False
                
                # Ollama is running, check for models
                print("\n✅ Ollama is running!")
                
                try:
                    response = requests.get('http://localhost:11434/api/tags', timeout=2)
                    models = response.json().get('models', [])
                    model_names = [m['name'] for m in models]
                    
                    if model_names:
                        print(f"\n📦 Available models: {', '.join(model_names)}")
                        print("\nRecommended models:")
                        print("  • llama3.1 (good balance)")
                        print("  • llama3.3 (latest, best performance)")
                        print("  • qwen2.5 (excellent for coding)\n")
                        
                        model_choice = input(f"Enter model name (default: llama3.1): ").strip() or 'llama3.1'
                        
                        if model_choice not in model_names:
                            print(f"\n📥 Model '{model_choice}' not found. Downloading...")
                            print("This may take a few minutes depending on your connection.\n")
                            
                            download = input(f"Download {model_choice}? (yes/no): ").strip().lower()
                            if download in ['yes', 'y']:
                                print(f"\nTo download, run in another terminal:")
                                print(f"  ollama pull {model_choice}\n")
                                print("Then restart KaiCTL.")
                                return False
                    else:
                        print("\n📥 No models found. You need to download a model.")
                        print("Recommended: llama3.1\n")
                        print("To download, run in another terminal:")
                        print("  ollama pull llama3.1\n")
                        print("Then restart KaiCTL.")
                        return False
                    
                    model_name = model_choice
                    
                except Exception as e:
                    print(f"⚠️  Could not fetch models: {e}")
                    model_name = 'llama3.1'
                
                config_content = f"""# KaiCTL Configuration
# Kubernetes AI Control - Natural Language Interface for kubectl

# AI Provider Configuration
AI_PROVIDER=ollama

# Claude API Configuration (not used but available)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Ollama Configuration (Local LLM)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL={model_name}
"""
                
                with open(env_file, 'w') as f:
                    f.write(config_content)
                
                print(f"\n✅ Configuration saved to: {env_file}")
                print("\n✨ Setup complete! Starting KaiCTL...\n")
                return True
            
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        
    return True

def get_local_yaml_files():
    """Get list of YAML files in current directory"""
    yaml_files = []
    cwd = Path.cwd()
    
    for ext in ['*.yaml', '*.yml']:
        yaml_files.extend(cwd.glob(ext))
    
    return [f.name for f in sorted(yaml_files)]

def get_kubectl_context():
    """Get current kubectl context information"""
    try:
        context = subprocess.check_output(
            ['kubectl', 'config', 'current-context'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        namespace = subprocess.check_output(
            ['kubectl', 'config', 'view', '--minify', '-o', 
             'jsonpath={..namespace}'],
            stderr=subprocess.DEVNULL
        ).decode().strip() or 'default'
        
        return f"Current context: {context}, namespace: {namespace}"
    except subprocess.CalledProcessError:
        return "kubectl not configured or not accessible"

def get_context_info():
    """Get comprehensive context information including local files"""
    kubectl_ctx = get_kubectl_context()
    yaml_files = get_local_yaml_files()
    cwd = Path.cwd()
    
    context = f"{kubectl_ctx}\nCurrent directory: {cwd}"
    
    if yaml_files:
        context += f"\nYAML files in current directory: {', '.join(yaml_files)}"
    
    return context

def get_system_prompt():
    """Returns the system prompt for the AI model"""
    return """You are a Kubernetes expert that translates natural language requests into kubectl commands.

Your task:
1. Analyze the user's request
2. Generate the appropriate kubectl command(s)
3. Respond ONLY with a JSON object in this exact format (no markdown, no code blocks):

{
  "command": "the kubectl command to execute",
  "explanation": "brief explanation of what the command does",
  "safe": true/false (false if command is destructive like delete/drain),
  "needs_analysis": true/false (true if this requires custom analysis beyond just running kubectl)
}

Important rules:
- Use proper kubectl syntax and best practices
- For listing/getting resources, use appropriate output formats (-o wide, -o yaml, -o json, etc.)
- Consider namespace context when relevant
- Be concise but accurate
- If the request is ambiguous, make reasonable assumptions based on common kubectl usage
- If multiple commands are needed, chain them or use the most appropriate single command
- Return ONLY the JSON object, no markdown formatting, no explanations outside the JSON
- For kubectl patch commands, use -p with inline JSON (the system will handle file conversion automatically)
- Use proper JSON format with escaped quotes in patch commands
- You CAN use shell features like pipes (|), grep, awk, jq for filtering and processing output
- For complex filtering, prefer kubectl's native filtering when possible, but use pipes when needed
- When YAML files are available in the current directory, you can reference them by filename in kubectl apply/create/delete commands
- If user asks to deploy/apply/create resources and YAML files are available, use those files

Special analysis commands:
- ANALYZE_RESOURCES: Compare resource requests/limits against actual usage from metrics
- ANALYZE_RESOURCES namespace=<ns>: Analyze specific namespace
- ANALYZE_RESOURCES pod=<n>: Analyze specific pod

Examples:
User: "show me all pods"
Response: {"command": "kubectl get pods -A", "explanation": "Lists all pods across all namespaces", "safe": true, "needs_analysis": false}

User: "deploy nginx" (when nginx.yaml exists in current directory)
Response: {"command": "kubectl apply -f nginx.yaml", "explanation": "Deploys resources from nginx.yaml file", "safe": true, "needs_analysis": false}

User: "apply the deployment"
Response: {"command": "kubectl apply -f deployment.yaml", "explanation": "Applies the deployment.yaml file from current directory", "safe": true, "needs_analysis": false}

User: "delete the pod named nginx"
Response: {"command": "kubectl delete pod nginx", "explanation": "Deletes the pod named nginx in the current namespace", "safe": false, "needs_analysis": false}

User: "compare cpu and memory requests vs usage"
Response: {"command": "ANALYZE_RESOURCES", "explanation": "Analyzes resource requests/limits against actual usage from metrics", "safe": true, "needs_analysis": true}"""

def translate_with_claude(user_input, context_info, api_key, history_context=None):
    """Use Claude API to translate natural language to kubectl command"""
    try:
        from anthropic import Anthropic
    except ImportError:
        return json.dumps({
            "error": "anthropic package not installed. Run: pip install anthropic",
            "command": None,
            "explanation": "Missing dependency",
            "safe": True
        })
    
    client = Anthropic(api_key=api_key)
    
    message = f"""{context_info}

User request: {user_input}"""

    if history_context:
        message = f"""{context_info}

{history_context}

User request: {user_input}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=get_system_prompt(),
            messages=[{"role": "user", "content": message}]
        )
        return response.content[0].text
    except Exception as e:
        return json.dumps({
            "error": f"Claude API error: {str(e)}",
            "command": None,
            "explanation": "API call failed",
            "safe": True
        })

def translate_with_ollama(user_input, context_info, ollama_url, model, history_context=None):
    """Use Ollama to translate natural language to kubectl command"""
    
    prompt = f"""{get_system_prompt()}

{context_info}"""

    if history_context:
        prompt += f"\n\n{history_context}"
    
    prompt += f"""

User request: {user_input}

Remember: Respond with ONLY the JSON object, no markdown code blocks."""

    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        return result['response']
    
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "error": f"Failed to connect to Ollama: {str(e)}",
            "command": None,
            "explanation": "Could not reach Ollama API",
            "safe": True
        })

def translate_to_kubectl(user_input, context_info, provider_config, history_context=None):
    """Route translation to the appropriate provider"""
    if provider_config['type'] == 'claude':
        return translate_with_claude(user_input, context_info, provider_config['api_key'], history_context)
    elif provider_config['type'] == 'ollama':
        return translate_with_ollama(
            user_input, 
            context_info, 
            provider_config['url'], 
            provider_config['model'],
            history_context
        )
    else:
        return json.dumps({
            "error": "Invalid provider configuration",
            "command": None,
            "explanation": "Configuration error",
            "safe": True
        })

def execute_kubectl_raw(command):
    """Execute a raw kubectl command and return the result"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result

def analyze_resource_usage(params=None):
    """Analyze resource requests/limits vs actual usage"""
    import re
    
    # Parse parameters
    namespace = None
    pod_name = None
    
    if params:
        ns_match = re.search(r'namespace=(\S+)', params)
        pod_match = re.search(r'pod=(\S+)', params)
        if ns_match:
            namespace = ns_match.group(1)
        if pod_match:
            pod_name = pod_match.group(1)
    
    try:
        # Get pod specs (requests/limits)
        if pod_name:
            if namespace:
                get_cmd = f"kubectl get pod {pod_name} -n {namespace} -o json"
            else:
                get_cmd = f"kubectl get pod {pod_name} -o json"
        else:
            if namespace:
                get_cmd = f"kubectl get pods -n {namespace} -o json"
            else:
                get_cmd = "kubectl get pods -A -o json"
        
        result = execute_kubectl_raw(get_cmd)
        if result.returncode != 0:
            return f"Error getting pod specs: {result.stderr}"
        
        pods_data = json.loads(result.stdout)
        if 'items' not in pods_data:
            pods_data = {'items': [pods_data]}
        
        # Get metrics
        if pod_name:
            if namespace:
                metrics_cmd = f"kubectl top pod {pod_name} -n {namespace} --no-headers"
            else:
                metrics_cmd = f"kubectl top pod {pod_name} --no-headers"
        else:
            if namespace:
                metrics_cmd = f"kubectl top pod -n {namespace} --no-headers"
            else:
                metrics_cmd = "kubectl top pod -A --no-headers"
        
        result = execute_kubectl_raw(metrics_cmd)
        if result.returncode != 0:
            return f"Error getting metrics: {result.stderr}\n(Make sure metrics-server is installed: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml)"
        
        # Parse metrics
        metrics = {}
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                if namespace or pod_name:
                    name, cpu, mem = parts[0], parts[1], parts[2]
                    ns = namespace if namespace else 'default'
                else:
                    ns, name, cpu, mem = parts[0], parts[1], parts[2], parts[3]
                metrics[f"{ns}/{name}"] = {'cpu': cpu, 'memory': mem}
        
        def parse_resource(value):
            """Parse k8s resource values to comparable numbers"""
            if not value or value == 'N/A':
                return 0
            value = str(value)
            if value.endswith('m'):
                return float(value[:-1])  # Keep in millicores
            elif value.endswith('Mi'):
                return float(value[:-2])
            elif value.endswith('Gi'):
                return float(value[:-2]) * 1024
            elif value.endswith('Ki'):
                return float(value[:-2]) / 1024
            else:
                try:
                    # Assume it's in cores if no unit
                    return float(value) * 1000  # Convert to millicores
                except:
                    return 0
        
        def format_cpu(value):
            """Format CPU value consistently"""
            if value == 'N/A' or value == 0:
                return 'Not Set'
            if isinstance(value, str):
                return value
            # Value is in millicores
            if value >= 1000:
                return f"{value/1000:.2f}"
            return f"{int(value)}m"
        
        def format_memory(value):
            """Format memory value consistently"""
            if value == 'N/A' or value == 0:
                return 'Not Set'
            return str(value)
        
        # Build analysis output
        output = []
        output.append("\n" + "=" * 140)
        output.append(f"{'POD NAME':<45} {'CPU REQ':<12} {'CPU USE':<12} {'CPU %':<10} {'MEM REQ':<12} {'MEM USE':<12} {'MEM %':<10} {'STATUS':<15}")
        output.append("=" * 140)
        
        # Totals tracking
        total_cpu_req = 0
        total_cpu_use = 0
        total_mem_req = 0
        total_mem_use = 0
        pods_with_metrics = 0
        
        for pod in pods_data['items']:
            pod_name_str = pod['metadata']['name']
            pod_ns = pod['metadata'].get('namespace', 'default')
            pod_key = f"{pod_ns}/{pod_name_str}"
            
            pod_metrics = metrics.get(pod_key, {})
            actual_cpu_str = pod_metrics.get('cpu', 'N/A')
            actual_mem_str = pod_metrics.get('memory', 'N/A')
            
            # Aggregate resources across all containers in the pod
            pod_cpu_req = 0
            pod_mem_req = 0
            
            for container in pod['spec'].get('containers', []):
                resources = container.get('resources', {})
                
                cpu_req = resources.get('requests', {}).get('cpu', 'N/A')
                mem_req = resources.get('requests', {}).get('memory', 'N/A')
                
                if cpu_req != 'N/A':
                    pod_cpu_req += parse_resource(cpu_req)
                if mem_req != 'N/A':
                    pod_mem_req += parse_resource(mem_req)
            
            # Parse actual usage
            actual_cpu_val = parse_resource(actual_cpu_str) if actual_cpu_str != 'N/A' else 0
            actual_mem_val = parse_resource(actual_mem_str) if actual_mem_str != 'N/A' else 0
            
            # Calculate percentages
            cpu_pct = "N/A"
            mem_pct = "N/A"
            status = "✓ OK"
            
            if actual_cpu_val > 0 and pod_cpu_req > 0:
                pct = (actual_cpu_val / pod_cpu_req) * 100
                cpu_pct = f"{pct:.1f}%"
                if pct > 90:
                    status = "⚠ HIGH CPU"
                elif pct < 30:
                    status = "💡 Low CPU"
            
            if actual_mem_val > 0 and pod_mem_req > 0:
                pct = (actual_mem_val / pod_mem_req) * 100
                mem_pct = f"{pct:.1f}%"
                if pct > 90:
                    status = "⚠ HIGH MEM"
                elif pct < 30 and status == "✓ OK":
                    status = "💡 Low Mem"
            
            # Format display values
            cpu_req_display = format_cpu(pod_cpu_req) if pod_cpu_req > 0 else "Not Set"
            cpu_use_display = format_cpu(actual_cpu_str) if actual_cpu_str != 'N/A' else "No Metrics"
            mem_req_display = format_memory(f"{int(pod_mem_req)}Mi") if pod_mem_req > 0 else "Not Set"
            mem_use_display = format_memory(actual_mem_str) if actual_mem_str != 'N/A' else "No Metrics"
            
            # Add to totals
            if actual_cpu_val > 0:
                total_cpu_use += actual_cpu_val
                pods_with_metrics += 1
            if pod_cpu_req > 0:
                total_cpu_req += pod_cpu_req
            if actual_mem_val > 0:
                total_mem_use += actual_mem_val
            if pod_mem_req > 0:
                total_mem_req += pod_mem_req
            
            output.append(f"{pod_name_str:<45} {cpu_req_display:<12} {cpu_use_display:<12} {cpu_pct:<10} {mem_req_display:<12} {mem_use_display:<12} {mem_pct:<10} {status:<15}")
        
        output.append("=" * 140)
        
        # Totals section
        total_cpu_req_display = format_cpu(total_cpu_req) if total_cpu_req > 0 else "0"
        total_cpu_use_display = format_cpu(total_cpu_use) if total_cpu_use > 0 else "0"
        total_mem_req_display = f"{int(total_mem_req)}Mi" if total_mem_req > 0 else "0"
        total_mem_use_display = f"{int(total_mem_use)}Mi" if total_mem_use > 0 else "0"
        
        total_cpu_pct = f"{(total_cpu_use / total_cpu_req * 100):.1f}%" if total_cpu_req > 0 else "N/A"
        total_mem_pct = f"{(total_mem_use / total_mem_req * 100):.1f}%" if total_mem_req > 0 else "N/A"
        
        output.append(f"{'TOTAL':<45} {total_cpu_req_display:<12} {total_cpu_use_display:<12} {total_cpu_pct:<10} {total_mem_req_display:<12} {total_mem_use_display:<12} {total_mem_pct:<10}")
        output.append("=" * 140)
        
        output.append("\n📊 SUMMARY:")
        output.append(f"  • Total CPU Requested: {total_cpu_req_display} | Total CPU Used: {total_cpu_use_display} | Usage: {total_cpu_pct}")
        output.append(f"  • Total Memory Requested: {total_mem_req_display} | Total Memory Used: {total_mem_use_display} | Usage: {total_mem_pct}")
        output.append(f"  • Pods with metrics: {pods_with_metrics}/{len(pods_data['items'])}")
        
        output.append("\n💡 LEGEND:")
        output.append("  • REQ = Resources Requested (what you asked Kubernetes to reserve)")
        output.append("  • USE = Actual Usage (what the pod is currently using)")
        output.append("  • % = Percentage of requested resources being used")
        output.append("  • 'Not Set' = No resource requests configured (not recommended)")
        output.append("  • 'No Metrics' = Pod exists but metrics-server has no data yet")
        output.append("  • ⚠ HIGH = Using >90% of requested (may need more resources)")
        output.append("  • 💡 Low = Using <30% of requested (potentially over-provisioned)")
        
        return '\n'.join(output)
        
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {e}"
    except Exception as e:
        return f"Error analyzing resources: {e}"

def execute_kubectl(command):
    """Execute kubectl command and return output"""
    import tempfile
    import shlex
    
    # Check if this is a special analysis command
    if command.startswith('ANALYZE_RESOURCES'):
        params = command.replace('ANALYZE_RESOURCES', '').strip()
        return analyze_resource_usage(params if params else None)
    
    try:
        # Check if command contains pipes, redirects, or other shell features
        has_shell_features = any(op in command for op in ['|', '>', '<', '&&', '||', ';'])
        
        # Check if this is a patch command with inline JSON
        if ('-p ' in command or '--patch ' in command) and ('{' in command or '[' in command):
            # Extract the patch JSON and convert to file-based approach
            parts = shlex.split(command)
            patch_json = None
            new_parts = []
            skip_next = False
            
            for i, part in enumerate(parts):
                if skip_next:
                    skip_next = False
                    continue
                    
                if part in ['-p', '--patch']:
                    # Next part is the JSON
                    if i + 1 < len(parts):
                        patch_json = parts[i + 1]
                        skip_next = True
                        # Replace with file-based patch
                        new_parts.append('--patch-file')
                        continue
                
                new_parts.append(part)
            
            if patch_json:
                # Write patch to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(patch_json)
                    temp_file = f.name
                
                new_parts.append(temp_file)
                
                try:
                    result = subprocess.run(
                        new_parts,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
            else:
                # Shouldn't happen, but fallback
                result = subprocess.run(
                    parts,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
        elif has_shell_features:
            # Execute as shell command to handle pipes, etc.
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                executable='/bin/bash'
            )
        else:
            # Normal command execution
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30
            )
        
        if result.returncode == 0:
            return result.stdout if result.stdout else "✓ Command executed successfully (no output)"
        else:
            return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error executing command: {str(e)}"

def troubleshoot_interactive(issue_description, context_info, provider_config):
    """Interactive troubleshooting session with user approval for fixes"""
    print("\n🔍 " + "=" * 70)
    print("TROUBLESHOOTING MODE")
    print("=" * 70)
    print(f"Issue: {issue_description}")
    print("\nAnalyzing the problem...\n")
    
    # Ask AI to diagnose the issue
    diagnosis_prompt = f"""Based on this issue description, provide a troubleshooting plan.

Issue: {issue_description}

Context: {context_info}

Respond with a JSON object containing:
{{
  "diagnosis": "explanation of what might be wrong",
  "investigation_steps": [
    {{"command": "kubectl command", "purpose": "why run this"}},
    ...
  ],
  "potential_fixes": [
    {{"fix": "description", "command": "kubectl command", "risk": "low/medium/high", "verification": "kubectl command to verify fix worked"}},
    ...
  ]
}}

Focus on common Kubernetes issues like:
- Pods not starting (ImagePullBackOff, CrashLoopBackOff)
- Resource constraints (OOMKilled, CPU throttling)
- Network issues (Service not reachable)
- Configuration problems (ConfigMap/Secret issues)
- Permission issues (RBAC)

For verification commands, use commands that check if the issue is resolved (e.g., check pod status, check if service is reachable).
"""

    response_text = translate_to_kubectl(diagnosis_prompt, context_info, provider_config)
    
    try:
        # Parse response
        cleaned_text = response_text.strip()
        if cleaned_text.startswith('```'):
            lines = cleaned_text.split('\n')
            cleaned_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_text
            cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
        
        troubleshoot_data = json.loads(cleaned_text)
        
        # Show diagnosis
        print("📋 DIAGNOSIS:")
        print(f"   {troubleshoot_data.get('diagnosis', 'Analyzing...')}\n")
        
        # Run investigation steps
        investigation_steps = troubleshoot_data.get('investigation_steps', [])
        if investigation_steps:
            print("🔎 INVESTIGATION STEPS:")
            
            for i, step in enumerate(investigation_steps, 1):
                command = step.get('command', '')
                purpose = step.get('purpose', '')
                
                print(f"\n{i}. {purpose}")
                print(f"   Command: {command}")
                
                run = input("   Run this? (yes/no/skip): ").lower()
                
                if run in ['y', 'yes']:
                    print("   Executing...\n")
                    output = execute_kubectl(command)
                    print(f"   Result:\n{output}")
                elif run == 'skip':
                    print("   ⏭️  Skipped remaining investigation\n")
                    break
                else:
                    print("   ❌ Skipped\n")
            
            print("\n" + "=" * 70)
        
        # Show potential fixes
        potential_fixes = troubleshoot_data.get('potential_fixes', [])
        if potential_fixes:
            print("\n🔧 POTENTIAL FIXES:")
            
            for i, fix in enumerate(potential_fixes, 1):
                fix_desc = fix.get('fix', '')
                command = fix.get('command', '')
                verification_cmd = fix.get('verification', '')
                risk = fix.get('risk', 'unknown').upper()
                
                # Color code by risk
                risk_indicator = {
                    'LOW': '✅',
                    'MEDIUM': '⚠️ ',
                    'HIGH': '🚨'
                }.get(risk, '❓')
                
                print(f"\n{i}. {fix_desc}")
                print(f"   Risk Level: {risk_indicator} {risk}")
                print(f"   Command: {command}")
                
                apply = input("   Apply this fix? (yes/no/skip): ").lower()
                
                if apply in ['y', 'yes']:
                    print("   Applying fix...\n")
                    output = execute_kubectl(command)
                    print(f"   Result:\n{output}\n")
                    
                    # Wait a moment for changes to propagate
                    print("   ⏳ Waiting for changes to propagate (3 seconds)...")
                    import time
                    time.sleep(3)
                    
                    # Verify fix automatically
                    print("   🔍 Verifying fix...\n")
                    
                    if verification_cmd:
                        # Use provided verification command
                        verify_output = execute_kubectl(verification_cmd)
                        print(f"   Verification result:\n{verify_output}\n")
                        
                        # Ask AI to analyze if the issue is resolved
                        analysis_prompt = f"""Analyze if this fix resolved the issue.

Original issue: {issue_description}
Fix applied: {fix_desc}
Command run: {command}

Verification command: {verification_cmd}
Verification output: {verify_output}

Respond with JSON:
{{
  "resolved": true/false,
  "confidence": "high/medium/low",
  "explanation": "why you think it's resolved or not"
}}
"""
                        
                        analysis_response = translate_to_kubectl(analysis_prompt, context_info, provider_config)
                        
                        try:
                            cleaned = analysis_response.strip()
                            if cleaned.startswith('```'):
                                lines = cleaned.split('\n')
                                cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned
                                cleaned = cleaned.replace('```json', '').replace('```', '').strip()
                            
                            analysis = json.loads(cleaned)
                            
                            is_resolved = analysis.get('resolved', False)
                            confidence = analysis.get('confidence', 'unknown').upper()
                            explanation = analysis.get('explanation', 'Analysis unavailable')
                            
                            if is_resolved:
                                confidence_icon = {
                                    'HIGH': '✅',
                                    'MEDIUM': '✓',
                                    'LOW': '?'
                                }.get(confidence, '?')
                                
                                print(f"   {confidence_icon} Issue appears RESOLVED (confidence: {confidence})")
                                print(f"   Reason: {explanation}\n")
                                
                                if confidence == 'HIGH':
                                    return {
                                        'resolved': True,
                                        'fix_applied': fix_desc,
                                        'command': command,
                                        'confidence': confidence
                                    }
                                else:
                                    cont = input("   Continue with more fixes? (yes/no): ").lower()
                                    if cont not in ['y', 'yes']:
                                        return {
                                            'resolved': True,
                                            'fix_applied': fix_desc,
                                            'command': command,
                                            'confidence': confidence
                                        }
                            else:
                                print(f"   ❌ Issue NOT resolved")
                                print(f"   Reason: {explanation}\n")
                                print("   Trying next fix...\n")
                        
                        except json.JSONDecodeError:
                            print(f"   ⚠️  Could not auto-verify. Check manually.\n")
                    else:
                        # No verification command provided
                        manual_verify = input("   Did this resolve the issue? (yes/no): ").lower()
                        if manual_verify in ['y', 'yes']:
                            return {
                                'resolved': True,
                                'fix_applied': fix_desc,
                                'command': command,
                                'manual_verification': True
                            }
                
                elif apply == 'skip':
                    print("   ⏭️  Skipping remaining fixes\n")
                    break
                else:
                    print("   ❌ Skipped\n")
            
            print("=" * 70)
        
        # Final recommendation
        print("\n💡 RECOMMENDATIONS:")
        print("   • Review Kubernetes events: kubectl get events --sort-by='.lastTimestamp'")
        print("   • Monitor pod status: kubectl get pods -w")
        print("   • Check resource metrics: kubectl top pods")
        
        return {'resolved': False}
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing troubleshooting response: {e}")
        return {'resolved': False, 'error': str(e)}
    except Exception as e:
        print(f"❌ Troubleshooting error: {e}")
        return {'resolved': False, 'error': str(e)}

class SessionLogger:
    """Manages session logging to local files"""
    
    def __init__(self):
        # Use ~/.kaictl/sessions directory
        kaictl_dir = Path.home() / '.kaictl'
        self.sessions_dir = kaictl_dir / 'sessions'
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Start with timestamp, will rename at end
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.temp_file = self.sessions_dir / f'session_{timestamp}_temp.log'
        self.session_file = None
        self.session_start = datetime.now()
        self.interactions = []
        
        # Log session start
        self._write_header()
    
    def _write_header(self):
        """Write session header"""
        with open(self.temp_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"KaiCTL - Kubernetes Natural Language Agent - Session Log\n")
            f.write(f"Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Context: {get_kubectl_context()}\n")
            f.write(f"Working Directory: {Path.cwd()}\n")
            yaml_files = get_local_yaml_files()
            if yaml_files:
                f.write(f"YAML files available: {', '.join(yaml_files)}\n")
            f.write("=" * 80 + "\n\n")
    
    def _generate_session_name(self):
        """Generate a meaningful session name based on interactions"""
        if not self.interactions:
            return "empty_session"
        
        # Extract key actions and resources
        actions = set()
        resources = set()
        
        for interaction in self.interactions[:5]:
            cmd = interaction['command'].lower()
            parts = cmd.split()
            
            if len(parts) > 1:
                action = parts[1]
                actions.add(action)
            
            if len(parts) > 2:
                resource = parts[2].rstrip('s')
                if resource not in ['all', '-a', '-n', '--namespace']:
                    resources.add(resource)
        
        action_str = '_'.join(sorted(actions)[:3]) if actions else 'kubectl'
        resource_str = '_'.join(sorted(resources)[:3]) if resources else 'ops'
        
        action_str = action_str.replace('-', '_')
        resource_str = resource_str.replace('-', '_')
        
        timestamp = self.session_start.strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{action_str}_{resource_str}"
    
    def log_interaction(self, user_input, command, explanation, safe, output, error=None):
        """Log a complete interaction"""
        self.interactions.append({
            'user_input': user_input,
            'command': command,
            'explanation': explanation
        })
        
        with open(self.temp_file, 'a') as f:
            timestamp = datetime.now().strftime('%H:%M:%S')
            f.write(f"[{timestamp}] User: {user_input}\n")
            f.write(f"Command: {command}\n")
            f.write(f"Info: {explanation}\n")
            if not safe:
                f.write(f"⚠️  Destructive command\n")
            if error:
                f.write(f"Status: {error}\n")
            else:
                f.write(f"Output:\n{output}\n")
            f.write("-" * 80 + "\n\n")
    
    def log_error(self, error_message):
        """Log an error"""
        with open(self.temp_file, 'a') as f:
            timestamp = datetime.now().strftime('%H:%M:%S')
            f.write(f"[{timestamp}] ERROR: {error_message}\n")
            f.write("-" * 80 + "\n\n")
    
    def close(self):
        """Close the session and rename file based on content"""
        duration = (datetime.now() - self.session_start).total_seconds()
        with open(self.temp_file, 'a') as f:
            f.write("=" * 80 + "\n")
            f.write(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {int(duration // 60)}m {int(duration % 60)}s\n")
            f.write("=" * 80 + "\n")
        
        session_name = self._generate_session_name()
        self.session_file = self.sessions_dir / f"{session_name}.log"
        
        counter = 1
        final_file = self.session_file
        while final_file.exists():
            final_file = self.sessions_dir / f"{session_name}_{counter}.log"
            counter += 1
        
        self.temp_file.rename(final_file)
        self.session_file = final_file
        
        print(f"\n📝 Session saved to: {self.session_file}")

class SessionHistory:
    """Manages and retrieves relevant session history"""
    
    def __init__(self, sessions_dir=None):
        if sessions_dir is None:
            kaictl_dir = Path.home() / '.kaictl'
            self.sessions_dir = kaictl_dir / 'sessions'
        else:
            self.sessions_dir = Path(sessions_dir)
    
    def get_recent_sessions(self, limit=5):
        """Get the most recent session files"""
        if not self.sessions_dir.exists():
            return []
        
        sessions = sorted(
            self.sessions_dir.glob('*.log'),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        return sessions[:limit]
    
    def parse_session_file(self, session_file):
        """Parse a session file and extract interactions"""
        interactions = []
        
        try:
            with open(session_file, 'r') as f:
                content = f.read()
                
            blocks = content.split('-' * 80)
            
            for block in blocks:
                if 'User:' in block and 'Command:' in block:
                    lines = block.strip().split('\n')
                    interaction = {}
                    
                    for line in lines:
                        if line.startswith('[') and 'User:' in line:
                            interaction['user_input'] = line.split('User:', 1)[1].strip()
                        elif line.startswith('Command:'):
                            interaction['command'] = line.split('Command:', 1)[1].strip()
                        elif line.startswith('Info:'):
                            interaction['explanation'] = line.split('Info:', 1)[1].strip()
                    
                    if 'command' in interaction:
                        interactions.append(interaction)
        
        except Exception:
            pass
        
        return interactions
    
    def find_similar_interactions(self, user_input, limit=3):
        """Find similar past interactions based on user input"""
        sessions = self.get_recent_sessions(limit=10)
        similar = []
        
        user_words = set(user_input.lower().split())
        
        for session in sessions:
            interactions = self.parse_session_file(session)
            
            for interaction in interactions:
                past_input = interaction.get('user_input', '').lower()
                past_words = set(past_input.split())
                
                overlap = len(user_words & past_words)
                if overlap > 0:
                    similar.append({
                        'score': overlap,
                        'interaction': interaction,
                        'session': session.name
                    })
        
        similar.sort(key=lambda x: x['score'], reverse=True)
        return similar[:limit]
    
    def get_context_summary(self, user_input):
        """Get a context summary from past sessions"""
        similar = self.find_similar_interactions(user_input, limit=3)
        
        if not similar:
            return None
        
        summary = "Past similar interactions:\n"
        for item in similar:
            interaction = item['interaction']
            summary += f"  • \"{interaction['user_input']}\" → {interaction['command']}\n"
        
        return summary

def setup_provider():
    """Determine which AI provider to use and validate setup"""
    load_env()
    
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.1')
    provider = os.getenv('AI_PROVIDER', 'auto').lower()
    
    if provider == 'claude' or (provider == 'auto' and anthropic_key and anthropic_key != 'your_anthropic_api_key_here'):
        if not anthropic_key or anthropic_key == 'your_anthropic_api_key_here':
            print("❌ ANTHROPIC_API_KEY not configured")
            print(f"Edit: {Path.home() / '.kaictl' / '.env'}")
            return None
        
        try:
            from anthropic import Anthropic
            print("🤖 Using: Claude (Anthropic)")
            return {'type': 'claude', 'api_key': anthropic_key}
        except ImportError:
            print("⚠️  anthropic package not installed")
            print("Run: pip install anthropic")
            if provider != 'auto':
                return None
            print("Falling back to Ollama...\n")
    
    if provider == 'ollama' or provider == 'auto':
        print(f"🤖 Using: Ollama at {ollama_url}")
        print(f"🧠 Model: {ollama_model}")
        
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            available_models = [m['name'] for m in models]
            
            if ollama_model not in available_models:
                print(f"⚠️  Warning: Model '{ollama_model}' not found.")
                print(f"Available models: {', '.join(available_models)}")
                print(f"To download: ollama pull {ollama_model}")
                return None
            
            return {'type': 'ollama', 'url': ollama_url, 'model': ollama_model}
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Ollama at {ollama_url}")
            print(f"Error: {e}")
            print("\nMake sure Ollama is running: ollama serve")
            return None
    
    print(f"❌ Unknown AI_PROVIDER: {provider}")
    return None

def main():
    print("🚀 Kubernetes Natural Language Agent (KaiCTL)")
    print("=" * 50)
    
    if not initialize_config():
        print("\n⚠️  Configuration required before first use.")
        print("Run the script again after configuring.")
        sys.exit(0)
    
    logger = SessionLogger()
    history = SessionHistory()
    
    provider_config = setup_provider()
    if not provider_config:
        logger.close()
        sys.exit(1)
    
    print("✅ AI provider configured\n")
    
    context_info = get_context_info()
    print(f"📍 {context_info}\n")
    
    yaml_files = get_local_yaml_files()
    if yaml_files:
        print(f"📄 YAML files detected: {', '.join(yaml_files)}\n")
    
    recent_sessions = history.get_recent_sessions(limit=3)
    if recent_sessions:
        print(f"💡 Found {len(recent_sessions)} recent session(s)")
        print("   (Agent will learn from your past interactions)\n")
    
    print("Type your request in natural language (or 'quit' to exit)")
    print("Examples:")
    print("  - show me all pods in the kube-system namespace")
    print("  - get the logs for the nginx pod")
    print("  - deploy nginx.yaml")
    print("  - compare cpu and memory requests vs usage")
    print("  - troubleshoot nginx pod not starting")
    print("  - fix issue with my deployment")
    print("=" * 50 + "\n")
    
    try:
        while True:
            try:
                user_input = input("💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                troubleshoot_keywords = ['troubleshoot', 'debug', 'fix', 'diagnose', 'issue with', 'problem with', 'not working', 'failing', "what's wrong", "what is wrong"]
                is_troubleshooting = any(keyword in user_input.lower() for keyword in troubleshoot_keywords)
                
                if is_troubleshooting:
                    result = troubleshoot_interactive(user_input, context_info, provider_config)
                    logger.log_interaction(user_input, "TROUBLESHOOT", 
                                         f"Troubleshooting session - Resolved: {result.get('resolved', False)}", 
                                         True, json.dumps(result, indent=2))
                    continue
                
                history_context = history.get_context_summary(user_input)
                if history_context:
                    print(f"💭 {history_context}")
                
                print("🤔 Thinking...", end='\r')
                response_text = translate_to_kubectl(user_input, context_info, provider_config, history_context)
                
                try:
                    cleaned_text = response_text.strip()
                    if cleaned_text.startswith('```'):
                        lines = cleaned_text.split('\n')
                        cleaned_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_text
                        cleaned_text = cleaned_text.replace('```json', '').replace('```', '').strip()
                    
                    response = json.loads(cleaned_text)
                    
                    if 'error' in response:
                        error_msg = response['error']
                        print(f"❌ {error_msg}")
                        logger.log_error(error_msg)
                        continue
                    
                    command = response['command']
                    explanation = response['explanation']
                    safe = response.get('safe', True)
                    needs_analysis = response.get('needs_analysis', False)
                except json.JSONDecodeError as e:
                    error_msg = f"Error parsing response: {response_text}"
                    print(f"❌ {error_msg}")
                    print(f"JSON Error: {e}")
                    logger.log_error(error_msg)
                    continue
                
                print(f"🔧 Command: {command}")
                print(f"📝 {explanation}")
                
                if not safe:
                    confirm = input("⚠️  This is a destructive command. Execute? (yes/no): ")
                    if confirm.lower() not in ['yes', 'y']:
                        print("❌ Command cancelled\n")
                        logger.log_interaction(user_input, command, explanation, safe, 
                                             "Command cancelled by user")
                        continue
                
                print("\n📤 Executing...\n")
                
                try:
                    if needs_analysis or command.startswith('ANALYZE_'):
                        output = analyze_resource_usage(command.replace('ANALYZE_RESOURCES', '').strip() if command.startswith('ANALYZE_RESOURCES') else None)
                    else:
                        output = execute_kubectl(command)
                    
                    print(output)
                    print()
                    
                    logger.log_interaction(user_input, command, explanation, safe, output)
                except Exception as e:
                    error_msg = f"Execution error: {str(e)}"
                    print(f"❌ {error_msg}\n")
                    logger.log_error(error_msg)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Error: {error_msg}\n")
                logger.log_error(error_msg)
    finally:
        logger.close()

if __name__ == "__main__":
    main()