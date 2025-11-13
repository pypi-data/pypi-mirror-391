"""
Aegis Agent CLI

Command-line interface for managing and running training agents.
"""

# CRITICAL: Set headless environment for OpenCV BEFORE any imports
# This prevents OpenCV from trying to load GUI libraries in headless environments
import os
from .headless_utils import setup_headless_environment
setup_headless_environment()

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Lazy imports to avoid requiring firebase_admin for all commands
def _import_agent_modules():
    """Lazy import of agent modules that require firebase_admin"""
    try:
        from .agent import TrainingAgent, AgentCapabilities
        from .agent_auth import AgentAuthenticator, AgentAuthenticationError
        return TrainingAgent, AgentCapabilities, AgentAuthenticator, AgentAuthenticationError
    except ImportError as e:
        if 'firebase_admin' in str(e) or 'google.cloud.firestore' in str(e):
            print("❌ Error: Required dependencies not found")
            print()
            print("Please reinstall aegis-vision:")
            print("  pip install --upgrade aegis-vision")
            print()
            print("If the error persists, try:")
            print("  pip install firebase-admin google-cloud-firestore")
            sys.exit(1)
        else:
            raise


def setup_logging(verbose: bool = False) -> None:
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def cmd_login(args) -> int:
    """Interactive login command (like huggingface-cli login)"""
    try:
        # Check for libGL before proceeding
        from .headless_utils import check_and_fix_libgl
        check_and_fix_libgl()
        
        _, _, AgentAuthenticator, _ = _import_agent_modules()
        
        print("🔐 Aegis AI Agent Login")
        print()
        print("To get your API key:")
        print("  1. Open Aegis AI application")
        print("  2. Go to: Model Training → Settings → Training Agents")
        print("  3. Click 'Add Agent' and copy the API key")
        print()
        
        # Get API key from user (visible input for easy verification)
        api_key = input("Enter your API key: ").strip()
        
        if not api_key:
            print("❌ API key is required")
            return 1
        
        # Validate API key format
        if not api_key.startswith('ak_'):
            print("❌ Invalid API key format. API keys should start with 'ak_'")
            return 1
        
        # Validate API key and retrieve owner info
        print()
        print("🔍 Validating API key...")
        import requests
        
        # Test API key by exchanging for token
        try:
            url = f"{args.cloud_function_url}/auth/agent/token"
            headers = {
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('success'):
                print(f"❌ API key validation failed: {data.get('message', 'Unknown error')}")
                return 1
            
            # Extract agent ID and owner info from response
            # IMPORTANT: Use the agent ID returned by the Cloud Function, not a generated one
            agent_id = data.get('agentId')
            if not agent_id:
                print("❌ API key validation failed: No agent ID returned")
                return 1
            
            owner_uid = data.get('ownerUid')
            owner_email = data.get('ownerEmail')
            owner_name = data.get('ownerName')
            
            print(f"✅ API key validated")
            print(f"   Agent ID: {agent_id}")
            if owner_uid:
                print(f"   Owner UID: {owner_uid}")
            if owner_email or owner_name:
                print(f"   Owner: {owner_name or ''} ({owner_email or 'no email'})")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to validate API key: {e}")
            return 1
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return 1
        
        # Get machine/host name for identification
        import socket
        default_hostname = socket.gethostname()
        print()
        machine_name = input(f"Enter machine name (press Enter for '{default_hostname}'): ").strip()
        if not machine_name:
            machine_name = default_hostname
        
        # Create config file with owner info
        config_path = AgentAuthenticator.create_config_file(
            agent_id=agent_id,
            api_key=api_key,
            config_path=Path(args.config) if args.config else None,
            agent_name=machine_name,
            cloud_function_url=args.cloud_function_url,
            firestore_project=args.firestore_project,
            owner_uid=owner_uid,
            owner_email=owner_email,
            owner_name=owner_name
        )
        
        print()
        print(f"✅ Login successful!")
        print(f"   Configuration saved to: {config_path}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Machine Name: {machine_name}")
        print()
        print("Next steps:")
        print("  1. Start the agent: aegis-agent start")
        print("  2. The agent will appear online in the Aegis AI application")
        print("  3. Submit training tasks from the application")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Login cancelled")
        return 1
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return 1


def cmd_init(args) -> int:
    """Initialize agent configuration"""
    try:
        # Check for libGL before proceeding
        from .headless_utils import check_and_fix_libgl
        check_and_fix_libgl()
        
        _, _, AgentAuthenticator, _ = _import_agent_modules()
        
        if not args.api_key:
            print("Error: --api-key is required")
            print("Get your API key from the Aegis AI application:")
            print("  Model Training → Settings → Training Agents → Add Agent")
            print()
            print("Tip: Use 'aegis-agent login' for interactive setup")
            return 1
        
        # Generate agent ID if not provided
        if not args.agent_id:
            import uuid
            agent_id = f"agent-{uuid.uuid4().hex[:16]}"
        else:
            agent_id = args.agent_id
        
        # Create config file
        config_path = AgentAuthenticator.create_config_file(
            agent_id=agent_id,
            api_key=args.api_key,
            config_path=Path(args.config) if args.config else None,
            agent_name=args.name,
            cloud_function_url=args.cloud_function_url,
            firestore_project=args.firestore_project
        )
        
        print(f"✅ Agent configuration created: {config_path}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Agent Name: {args.name or f'Agent {agent_id[:8]}'}")
        print()
        print("Next steps:")
        print("  1. Start the agent: aegis-agent start")
        print("  2. The agent will appear online in the Aegis AI application")
        print("  3. Submit training tasks from the application")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return 1


def cmd_start(args) -> int:
    """Start the agent daemon"""
    try:
        TrainingAgent, _, AgentAuthenticator, AgentAuthenticationError = _import_agent_modules()
        setup_logging(args.verbose)
        
        # Check environment compatibility BEFORE starting agent
        if not args.skip_env_check:
            from .environment_check import check_environment_interactive
            
            print()
            env_ok = check_environment_interactive()
            print()
            
            if not env_ok:
                print("❌ Environment check failed. Please fix the issues above.")
                print()
                print("💡 You can skip this check with --skip-env-check (not recommended)")
                return 1
        
        # Load authenticator
        config_path = Path(args.config) if args.config else None
        authenticator = AgentAuthenticator(config_path)
        
        # Create and start agent
        work_dir = Path(args.work_dir) if args.work_dir else None
        agent = TrainingAgent(authenticator, work_dir)
        
        print(f"🚀 Starting Aegis AI Training Agent")
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Work Directory: {agent.work_dir}")
        print()
        
        # Show capabilities
        caps = agent.capabilities
        print("📊 System Capabilities:")
        print(f"   Platform: {caps['platform']}")
        print(f"   Memory: {caps['totalMemoryGB']}GB total, {caps['availableMemoryGB']}GB available")
        print(f"   Storage: {caps['availableStorageGB']}GB available")
        print(f"   CPU Cores: {caps['cpuCount']}")
        if caps['hasGPU']:
            print(f"   GPU: Yes ({caps.get('gpuDetectionMethod', 'Unknown')})")
            print(f"   CUDA: {caps['cudaVersion']}")
            for gpu in caps['gpuInfo']:
                print(f"     {gpu['name']} ({gpu['memory']}GB, Compute: {gpu.get('computeCapability', 'Unknown')})")
        else:
            print(f"   GPU: No")
        print()
        
        # Start agent
        agent.start()
        
        return 0
        
    except AgentAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print()
        print("Make sure you have run 'aegis-agent init' first.")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Agent error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_status(args) -> int:
    """Show agent status"""
    try:
        _, AgentCapabilities, AgentAuthenticator, _ = _import_agent_modules()
        
        config_path = Path(args.config) if args.config else None
        authenticator = AgentAuthenticator(config_path)
        
        print(f"📊 Agent Status")
        print(f"   Agent ID: {authenticator.get_agent_id()}")
        print(f"   Config: {authenticator.config_path}")
        print(f"   Firestore Project: {authenticator.get_firestore_project()}")
        print()
        
        # Show capabilities
        caps = AgentCapabilities.detect()
        print("💻 System Capabilities:")
        print(f"   Platform: {caps['platform']}")
        print(f"   Python: {caps['pythonVersion']}")
        print(f"   Memory: {caps['availableMemoryGB']}GB / {caps['totalMemoryGB']}GB")
        print(f"   Storage: {caps['availableStorageGB']}GB / {caps['totalStorageGB']}GB")
        print(f"   CPU: {caps['cpuCount']} cores")
        if caps['hasGPU']:
            print(f"   GPU: Yes ({caps.get('gpuDetectionMethod', 'Unknown')})")
            print(f"   CUDA: {caps['cudaVersion']}")
            for gpu in caps['gpuInfo']:
                print(f"     {gpu['name']} ({gpu['memory']}GB, Compute: {gpu.get('computeCapability', 'Unknown')})")
        else:
            print(f"   GPU: No")
        
        # Test authentication
        print()
        print("🔐 Testing authentication...")
        try:
            token = authenticator.authenticate()
            print("   ✅ Authentication successful")
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_info(args) -> int:
    """Show system information"""
    _, AgentCapabilities, _, _ = _import_agent_modules()
    caps = AgentCapabilities.detect()
    
    print("📊 System Information")
    print()
    print(f"Platform: {caps['platform']}")
    print(f"Python Version: {caps['pythonVersion']}")
    print()
    print("Memory:")
    print(f"  Total: {caps['totalMemoryGB']:.2f} GB")
    print(f"  Available: {caps['availableMemoryGB']:.2f} GB")
    print()
    print("Storage:")
    print(f"  Total: {caps['totalStorageGB']:.2f} GB")
    print(f"  Available: {caps['availableStorageGB']:.2f} GB")
    print()
    print(f"CPU Cores: {caps['cpuCount']}")
    print()
    
    # Display acceleration information
    if caps['platform'] == 'Darwin':
        # macOS: Show MPS status instead of GPU
        print("🎯 ML Acceleration (macOS):")
        if caps['hasMPS']:
            print(f"  Metal Performance Shaders (MPS): ✓ Available")
            print(f"  Detection Method: {caps.get('gpuDetectionMethod', 'Unknown')}")
            for gpu in caps['gpuInfo']:
                print(f"  Device: {gpu['name']}")
            print()
            print("  💡 Use torch.device('mps') for 3-5x acceleration")
        else:
            print(f"  Metal Performance Shaders (MPS): ✗ Not available")
            print(f"  Note: Requires Apple Silicon (M1/M2/M3/M4) + PyTorch 1.12+")
            print(f"  Falling back to CPU training (slower)")
    
    elif caps['hasGPU']:
        # Linux/Windows: Show CUDA GPU info
        print("🎮 CUDA GPU Information:")
        print(f"  Detection Method: {caps.get('gpuDetectionMethod', 'Unknown')}")
        print(f"  CUDA Version: {caps['cudaVersion'] or 'Not detected'}")
        if caps.get('nvidiaDriverVersion'):
            print(f"  Driver Version: {caps['nvidiaDriverVersion']}")
        if caps.get('cudaRuntimeVersion'):
            print(f"  CUDA Runtime: {caps['cudaRuntimeVersion']}")
        print()
        for i, gpu in enumerate(caps['gpuInfo']):
            print(f"  GPU {gpu.get('index', i)}:")
            print(f"    Name: {gpu['name']}")
            print(f"    Memory: {gpu['memory']} GB")
            if gpu.get('computeCapability'):
                print(f"    Compute Capability: {gpu['computeCapability']}")
        print()
        print(f"  MPS Available: No (NVIDIA GPU detected)")
    
    else:
        # No GPU detected
        if caps['platform'] == 'Darwin':
            print("⚠️  ML Acceleration (macOS):")
            print(f"  Metal Performance Shaders (MPS): ✗ Not available")
            print(f"  Note: Requires Apple Silicon + PyTorch with MPS support")
            print(f"  Current setup: Intel Mac or MPS not available")
            print()
            print("  💡 Options:")
            print("     1. Use CPU training (slower)")
            print("     2. Upgrade to Apple Silicon Mac")
            print("     3. Use external GPU (eGPU) if available")
        else:
            print("⚠️  GPU Not Detected:")
            print(f"  Platform: {caps['platform']}")
            print(f"  Status: No GPU acceleration available")
            print()
            print("  💡 Troubleshooting:")
            print("     1. Check if nvidia-smi works: nvidia-smi")
            print("     2. Verify PyTorch CUDA: python -c \"import torch; print(torch.cuda.is_available())\"")
            print("     3. Check Docker: docker run --gpus all (if in Docker)")
            print("     4. Run diagnostic: python test-scripts/integration/test_docker_gpu_detection.py")
    
    return 0


def cmd_check_env(args) -> int:
    """Check environment compatibility"""
    from .environment_check import check_environment_interactive
    
    print()
    env_ok = check_environment_interactive()
    print()
    
    if env_ok:
        print("✅ Environment is ready for Aegis AI training.")
        return 0
    else:
        print("❌ Environment has issues that need to be addressed.")
        return 1


def cmd_clear_cache(args) -> int:
    """Clear Firebase configuration cache"""
    from pathlib import Path
    
    cache_path = Path.home() / '.aegis-vision' / 'cache' / 'firebase_config.json'
    
    if cache_path.exists():
        cache_path.unlink()
        print(f"✅ Cleared Firebase config cache: {cache_path}")
        return 0
    else:
        print("ℹ️  No cache found")
        return 0


def cmd_show_cache(args) -> int:
    """Show cached Firebase configuration"""
    from pathlib import Path
    import json
    
    cache_path = Path.home() / '.aegis-vision' / 'cache' / 'firebase_config.json'
    
    if not cache_path.exists():
        print("ℹ️  No cache found")
        print(f"   Expected location: {cache_path}")
        print()
        print("Cache will be created automatically when agent starts.")
        return 0
    
    try:
        with open(cache_path, 'r') as f:
            cache_data = json.load(f)
        
        print("📦 Cached Firebase Configuration:")
        print(f"   Cache file: {cache_path}")
        print(f"   Cached at: {cache_data.get('cached_at', 'unknown')}")
        print(f"   Fetched from: {cache_data.get('fetched_from', 'unknown')}")
        print(f"   Cache version: {cache_data.get('version', 'unknown')}")
        print()
        
        firebase_config = cache_data.get('firebaseConfig', {})
        print("Firebase Config:")
        print(f"   API Key: {firebase_config.get('apiKey', 'unknown')[:20]}...")
        print(f"   Project ID: {firebase_config.get('projectId', 'unknown')}")
        print(f"   Auth Domain: {firebase_config.get('authDomain', 'unknown')}")
        print()
        
        agent_info = cache_data.get('agentInfo', {})
        if agent_info:
            print("Agent Info:")
            print(f"   Agent ID: {agent_info.get('agentId', 'unknown')}")
            print(f"   Owner UID: {agent_info.get('ownerUid', 'unknown')}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to read cache: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Aegis AI Training Agent - Distributed model training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive login (recommended)
  aegis-agent login
  
  # Or initialize with API key directly
  aegis-agent init --api-key ak_xxxxxxxxxxxxx --name "My Training Server"
  
  # Start agent daemon
  aegis-agent start
  
  # Check agent status
  aegis-agent status
  
  # Show system capabilities
  aegis-agent info
  
  # Cache management
  aegis-agent show-cache     # Show cached Firebase config
  aegis-agent clear-cache    # Clear cache (force refetch)
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # login command
    login_parser = subparsers.add_parser('login', help='Interactive login (like huggingface-cli login)')
    login_parser.add_argument('--config', help='Config file path (default: ~/.aegis-ai/agent-config.json)')
    login_parser.add_argument(
        '--cloud-function-url',
        default='https://us-central1-aegis-vision-464501.cloudfunctions.net/aegis-vision-admin-api',
        help='Cloud Function URL'
    )
    login_parser.add_argument(
        '--firestore-project',
        default='aegis-vision-464501',
        help='Firestore project ID'
    )
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize agent configuration (non-interactive)')
    init_parser.add_argument('--api-key', required=True, help='API key from Aegis AI')
    init_parser.add_argument('--agent-id', help='Agent ID (auto-generated if not provided)')
    init_parser.add_argument('--name', help='Human-readable agent name')
    init_parser.add_argument('--config', help='Config file path (default: ~/.aegis-ai/agent-config.json)')
    init_parser.add_argument(
        '--cloud-function-url',
        default='https://us-central1-aegis-vision-464501.cloudfunctions.net/aegis-vision-admin-api',
        help='Cloud Function URL'
    )
    init_parser.add_argument(
        '--firestore-project',
        default='aegis-vision-464501',
        help='Firestore project ID'
    )
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start agent daemon')
    start_parser.add_argument('--config', help='Config file path')
    start_parser.add_argument('--work-dir', help='Working directory for training')
    start_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    start_parser.add_argument(
        '--skip-env-check',
        action='store_true',
        help='Skip environment compatibility check (not recommended)'
    )
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show agent status')
    status_parser.add_argument('--config', help='Config file path')
    
    # info command
    info_parser = subparsers.add_parser('info', help='Show system information')
    
    # check-env command
    check_env_parser = subparsers.add_parser(
        'check-env',
        help='Check environment compatibility and suggest fixes'
    )
    
    # clear-cache command
    clear_cache_parser = subparsers.add_parser(
        'clear-cache',
        help='Clear cached Firebase configuration'
    )
    
    # show-cache command
    show_cache_parser = subparsers.add_parser(
        'show-cache',
        help='Show cached Firebase configuration'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    if args.command == 'login':
        return cmd_login(args)
    elif args.command == 'init':
        return cmd_init(args)
    elif args.command == 'start':
        return cmd_start(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'info':
        return cmd_info(args)
    elif args.command == 'check-env':
        return cmd_check_env(args)
    elif args.command == 'clear-cache':
        return cmd_clear_cache(args)
    elif args.command == 'show-cache':
        return cmd_show_cache(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

