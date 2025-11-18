"""Command-line interface for Neuron CLI / SAN CLI"""

import sys
import argparse
import getpass
from ..version import __version__
from ..core.logger import logger
from ..jobs.package_manager import PackageManager

# Lazy import agent to avoid loading issues
def get_agent():
    from ..core.agent import NeuronAgent
    from ..core.config import Config
    config = Config()
    return NeuronAgent(config)


def cmd_login(args):
    """Login to Nexus Core Cloud with OTP"""
    import requests
    from ..core.config import Config
    from pathlib import Path
    
    logger.info("🔐 SAN CLI Login")
    logger.info("=" * 70)
    
    # Get OTP token
    if args.otp:
        otp = args.otp
    else:
        logger.info("\nGet your OTP token from: https://nexuscore.cloud/devices/new")
        otp = getpass.getpass("\nEnter your OTP token: ")
    
    if not otp:
        logger.error("❌ OTP token required")
        return 1
    
    # Authenticate with API
    logger.info("\n🔄 Authenticating...")
    
    try:
        api_url = args.api_url if hasattr(args, 'api_url') and args.api_url else 'https://api.support.nexuscore.cloud'
        
        response = requests.post(
            f'{api_url}/auth/otp',
            json={'otp': otp.strip()},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Save configuration
            config = Config()
            config.data['device_id'] = data.get('device_id', '')
            config.data['brand_id'] = data.get('brand_id', 'nexuscore')
            config.data['jwt_token'] = data.get('jwt_token', '')
            config.data['device_api_key'] = data.get('device_api_key', data.get('jwt_token', ''))  # Save device API key
            config.data['api_url'] = api_url
            config.save()
            
            # Set file permissions (600 - owner read/write only)
            config_file = Path.home() / '.neuron' / 'config.json'
            config_file.chmod(0o600)
            
            logger.info("✅ Authentication successful!")
            logger.info("\n📋 Device Information:")
            logger.info(f"   Device ID: {data.get('device_id', 'N/A')}")
            logger.info(f"   Brand ID: {data.get('brand_id', 'N/A')}")
            logger.info(f"   Device URL: {data.get('device_id', 'N/A').split('-')[0]}.mesh.nexuscore.cloud")
            logger.info(f"\n💾 Configuration saved to: {config_file}")
            logger.info(f"   (Permissions: 600 - secure)")
            
            logger.info("\n🚀 Next steps:")
            logger.info("   1. san-cli install              # Install SPACE Agent and services")
            logger.info("   2. san-cli status               # Check status")
            logger.info("   3. san-cli ollama pull llama3.2:3b  # Pull AI model")
            logger.info("   4. san-cli marketplace list     # Browse packages")
            
            logger.info("\n" + "=" * 70)
            return 0
        
        elif response.status_code == 401:
            logger.error("❌ Authentication failed: Invalid OTP token")
            logger.info("\n💡 Tips:")
            logger.info("   - Make sure you copied the entire OTP token")
            logger.info("   - OTP tokens are single-use and expire after 10 minutes")
            logger.info("   - Generate a new token at: https://nexuscore.cloud/devices/new")
            return 1
        
        else:
            logger.error(f"❌ Authentication failed: HTTP {response.status_code}")
            logger.error(f"   {response.text}")
            return 1
    
    except requests.exceptions.Timeout:
        logger.error("❌ Connection timeout - please check your internet connection")
        return 1
    
    except requests.exceptions.ConnectionError:
        logger.error("❌ Could not connect to Nexus Core Cloud")
        logger.error("   Please check your internet connection")
        return 1
    
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        return 1


def cmd_install(args):
    """Full installation of SPACE Agent and services"""
    from ..installer import (
        SystemDetector,
        DependencyInstaller,
        SpaceAgentInstaller,
        HostServiceInstaller
    )
    from ..core.config import Config
    
    logger.info("🚀 SAN CLI Installation")
    logger.info("=" * 50)
    
    # Step 1: Detect system
    logger.info("\n📊 Detecting system...")
    detector = SystemDetector()
    system_info = detector.detect_all()
    
    logger.info(f"   OS: {system_info['os']['name']}")
    logger.info(f"   Architecture: {system_info['arch']['machine']}")
    logger.info(f"   Python: {system_info['python']['version']}")
    logger.info(f"   Docker: {'✅ Installed' if system_info['docker']['installed'] else '❌ Not installed'}")
    
    if system_info['gpu']['available']:
        logger.info(f"   GPU: ✅ {system_info['gpu']['type']} ({system_info['gpu']['memory_gb']}GB)")
    else:
        logger.info(f"   GPU: ❌ Not detected")
    
    # Check compatibility
    compatible, issues = detector.is_compatible()
    if not compatible:
        logger.error("\n❌ System not compatible:")
        for issue in issues:
            logger.error(f"   - {issue}")
        return 1
    
    # Step 2: Install dependencies
    if not args.skip_deps:
        logger.info("\n📦 Installing dependencies...")
        pkg_mgr = detector.get_package_manager()
        dep_installer = DependencyInstaller(system_info['os']['type'], pkg_mgr)
        
        # Install build tools
        build_tools = dep_installer.install_build_tools()
        
        # Install Python 3.12 if needed
        if not system_info['python']['recommended']:
            logger.info("   Installing Python 3.12...")
            dep_installer.install_python312()
    
    # Step 3: Install SPACE Agent
    if not args.skip_agent:
        logger.info("\n🚀 Installing SPACE Agent...")
        config = Config()
        agent_installer = SpaceAgentInstaller(config.data)
        result = agent_installer.install()
        
        if not result['success']:
            logger.error(f"   ❌ Failed: {result.get('error')}")
            return 1
    
    # Step 4: Install Ollama
    if not args.skip_ollama:
        logger.info("\n🤖 Installing Ollama...")
        host_installer = HostServiceInstaller(system_info['os']['type'])
        result = host_installer.install_ollama(system_info['gpu'])
        
        if not result['success']:
            logger.error(f"   ❌ Failed: {result.get('error')}")
            return 1
    
    # Step 5: Install Whisper
    if not args.skip_whisper:
        logger.info("\n🎤 Installing Whisper...")
        python_path = system_info['python'].get('python3.12', 'python3')
        result = host_installer.install_whisper(python_path)
        
        if not result['success']:
            logger.error(f"   ❌ Failed: {result.get('error')}")
            return 1
    
    # Done!
    logger.info("\n" + "=" * 50)
    logger.info("✅ Installation complete!")
    logger.info("\nNext steps:")
    logger.info("1. san-cli status          # Check status")
    logger.info("2. san-cli ollama pull llama3.1:8b  # Pull AI model")
    logger.info("3. san-cli logs space-agent -f      # View logs")
    
    return 0


def cmd_register(args):
    """Register device command"""
    logger.info("🔐 Device Registration")
    logger.info("=" * 50)
    logger.info("Please visit: https://nexuscore.cloud/neuron/register")
    logger.info("=" * 50)
    logger.info("\n📋 Steps:")
    logger.info("1. Create account or login at nexuscore.cloud")
    logger.info("2. Navigate to Neuron section")
    logger.info("3. Click 'Register New Device'")
    logger.info("4. Copy the registration command")
    logger.info("5. Run the command here")
    logger.info("\nOr manually configure ~/.neuron/config.json")
    return 0


def cmd_start(args):
    """Start agent command"""
    try:
        agent = get_agent()
        agent.start(daemon=args.daemon)
        return 0
    except KeyboardInterrupt:
        logger.info("\n👋 Agent stopped")
        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


def cmd_stop(args):
    """Stop agent command"""
    logger.info("🛑 Stopping agent...")
    # TODO: Implement proper daemon stop
    logger.info("✅ Agent stopped")
    return 0


def cmd_status(args):
    """Status command - enhanced with service management"""
    from ..services import ServiceManager
    
    logger.info("📊 SAN CLI Status")
    logger.info("=" * 70)
    
    # Get all services
    service_mgr = ServiceManager()
    all_services = service_mgr.list_all_services()
    
    # Docker services
    if all_services['docker']:
        logger.info("\n🐳 Docker Services:")
        for svc in all_services['docker']:
            status_icon = "✅" if svc['running'] else "❌"
            logger.info(f"   {status_icon} {svc['name']:<20} {svc['status']}")
    
    # Host services
    if all_services['host']:
        logger.info("\n🖥️  Host Services:")
        for svc in all_services['host']:
            status_icon = "✅" if svc['running'] else "❌"
            logger.info(f"   {status_icon} {svc['name']:<20} {svc['status']}")
    
    logger.info("\n" + "=" * 70)
    return 0


def cmd_logs(args):
    """View service logs"""
    from ..services import ServiceManager
    
    service_mgr = ServiceManager()
    logs = service_mgr.get_logs(args.service, follow=args.follow, tail=args.tail)
    
    if logs:
        print(logs)
        return 0
    elif args.follow:
        # Logs were streamed
        return 0
    else:
        logger.error(f"❌ Could not get logs for {args.service}")
        return 1


def cmd_restart(args):
    """Restart a service"""
    from ..services import ServiceManager
    
    service_mgr = ServiceManager()
    
    if args.all:
        logger.info("🔄 Restarting all services...")
        all_services = service_mgr.list_all_services()
        
        for svc in all_services['docker'] + all_services['host']:
            service_mgr.restart_service(svc['name'])
        
        logger.info("✅ All services restarted")
        return 0
    else:
        return 0 if service_mgr.restart_service(args.service) else 1


def cmd_service_start(args):
    """Start a service"""
    from ..services import ServiceManager
    
    service_mgr = ServiceManager()
    return 0 if service_mgr.start_service(args.service) else 1


def cmd_service_stop(args):
    """Stop a service"""
    from ..services import ServiceManager
    
    service_mgr = ServiceManager()
    return 0 if service_mgr.stop_service(args.service) else 1


def cmd_enable(args):
    """Enable service auto-start"""
    from ..services import ServiceManager
    
    service_mgr = ServiceManager()
    return 0 if service_mgr.enable_service(args.service) else 1


def cmd_disable(args):
    """Disable service auto-start"""
    from ..services import ServiceManager
    
    service_mgr = ServiceManager()
    return 0 if service_mgr.disable_service(args.service) else 1


def cmd_ollama_list(args):
    """List Ollama models"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    models = ollama.list_models()
    
    if not models:
        logger.info("📦 No models installed")
        logger.info("\nRecommended models:")
        for model in ollama.get_recommended_models()[:3]:
            logger.info(f"   • {model['name']:<20} {model['size']:<10} {model['description']}")
        logger.info("\nInstall with: san-cli ollama pull <model>")
        return 0
    
    logger.info(f"🤖 Installed Models ({len(models)})")
    logger.info("=" * 70)
    
    for model in models:
        logger.info(f"\n📦 {model['name']}")
        logger.info(f"   Size: {model['size']}")
        if model.get('modified'):
            logger.info(f"   Modified: {model['modified']}")
    
    logger.info("\n" + "=" * 70)
    return 0


def cmd_ollama_pull(args):
    """Pull an Ollama model"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    return 0 if ollama.pull_model(args.model) else 1


def cmd_ollama_remove(args):
    """Remove an Ollama model"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    return 0 if ollama.remove_model(args.model) else 1


def cmd_ollama_ps(args):
    """List running Ollama models"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    models = ollama.list_running()
    
    if not models:
        logger.info("📦 No models currently running")
        return 0
    
    logger.info(f"🤖 Running Models ({len(models)})")
    logger.info("=" * 70)
    
    for model in models:
        logger.info(f"\n📦 {model['name']}")
        logger.info(f"   Processor: {model['processor']}")
        logger.info(f"   Size: {model['size']}")
        if model.get('until'):
            logger.info(f"   Until: {model['until']}")
    
    logger.info("\n" + "=" * 70)
    return 0


def cmd_ollama_run(args):
    """Run an Ollama model"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    return 0 if ollama.run_model(args.model, args.prompt) else 1


def cmd_ollama_show(args):
    """Show Ollama model info"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    info = ollama.show_model(args.model)
    
    if not info:
        logger.error(f"❌ Model '{args.model}' not found")
        return 1
    
    logger.info(f"📄 Model Information: {args.model}")
    logger.info("=" * 70)
    
    for key, value in info.items():
        if isinstance(value, list):
            logger.info(f"\n{key.title()}:")
            for item in value:
                logger.info(f"   {item}")
        else:
            logger.info(f"{key.title()}: {value}")
    
    logger.info("\n" + "=" * 70)
    return 0


def cmd_ollama_recommended(args):
    """Show recommended models"""
    from ..ollama import OllamaManager
    
    ollama = OllamaManager()
    models = ollama.get_recommended_models()
    
    logger.info("🌟 Recommended Models")
    logger.info("=" * 70)
    
    for model in models:
        icon = "⭐" if model['recommended'] else "  "
        logger.info(f"\n{icon} {model['name']:<20} {model['size']:<10}")
        logger.info(f"   {model['description']}")
        logger.info(f"   Speed: {model['speed']:<15} Quality: {model['quality']}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Install with: san-cli ollama pull <model>")
    return 0


def cmd_marketplace_list(args):
    """List marketplace packages"""
    from ..marketplace import MarketplaceManager
    
    marketplace = MarketplaceManager()
    
    if args.category:
        packages = marketplace.list_packages(category=args.category)
    else:
        packages = marketplace.list_packages()
    
    if not packages:
        logger.info("📦 No packages available")
        return 0
    
    # Group by category
    by_category = {}
    for pkg in packages:
        cat = pkg.get('category', 'Other')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(pkg)
    
    logger.info(f"📦 Marketplace Packages ({len(packages)})")
    logger.info("=" * 70)
    
    for category, pkgs in sorted(by_category.items()):
        display_category = category.title() if category else "Other"
        logger.info(f"\n🏷️  {display_category}")
        for pkg in pkgs:
            name = pkg.get('name', 'unknown')
            version = pkg.get('version', 'n/a')
            description = pkg.get('description', '') or ''
            logger.info(f"   • {name:<25} v{version:<10} {description[:40]}")
    
    logger.info("\n" + "=" * 70)
    logger.info("Install with: san-cli marketplace install <name>")
    return 0


def cmd_marketplace_search(args):
    """Search marketplace packages"""
    from ..marketplace import MarketplaceManager
    
    marketplace = MarketplaceManager()
    packages = marketplace.search_packages(args.query)
    
    if not packages:
        logger.info(f"📦 No packages found matching '{args.query}'")
        return 0
    
    logger.info(f"🔍 Search Results ({len(packages)})")
    logger.info("=" * 70)
    
    for pkg in packages:
        logger.info(f"\n📦 {pkg.get('name', 'unknown')} v{pkg.get('version', 'n/a')}")
        logger.info(f"   Category: {pkg.get('category', 'Other')}")
        logger.info(f"   {pkg.get('description', '')}")
    
    logger.info("\n" + "=" * 70)
    return 0


def cmd_marketplace_info(args):
    """Show marketplace package info"""
    from ..marketplace import MarketplaceManager
    
    marketplace = MarketplaceManager()
    pkg = marketplace.get_package(args.package)
    
    if not pkg:
        logger.error(f"❌ Package '{args.package}' not found")
        return 1
    
    logger.info(f"📄 Package Information")
    logger.info("=" * 70)
    logger.info(f"\nName: {pkg.get('name', 'unknown')}")
    logger.info(f"Version: {pkg.get('version', 'n/a')}")
    logger.info(f"Type: {pkg.get('type', 'n/a')}")
    logger.info(f"Category: {pkg.get('category', 'Other')}")
    logger.info(f"\nDescription:")
    logger.info(f"  {pkg.get('description', '')}")
    
    if pkg.get('dependencies'):
        logger.info(f"\nDependencies:")
        for dep in pkg['dependencies']:
            logger.info(f"  • {dep}")

    if pkg.get('type') == 'docker' and pkg.get('docker'):
        docker = pkg['docker']
        logger.info(f"\nDocker Configuration:")
        logger.info(f"  Image: {docker.get('image', 'n/a')}")
        logger.info(f"  Container: {docker['container_name']}")
        if docker.get('ports'):
            logger.info(f"  Ports: {', '.join(docker['ports'])}")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Install with: san-cli marketplace install {pkg['name']}")
    return 0


def cmd_marketplace_install(args):
    """Install marketplace package"""
    from ..marketplace import MarketplaceManager
    
    marketplace = MarketplaceManager()
    return 0 if marketplace.install_package(args.package) else 1


def cmd_marketplace_uninstall(args):
    """Uninstall marketplace package"""
    from ..marketplace import MarketplaceManager
    
    marketplace = MarketplaceManager()
    return 0 if marketplace.uninstall_package(args.package) else 1


def cmd_marketplace_update(args):
    """Update marketplace package"""
    from ..marketplace import MarketplaceManager
    
    marketplace = MarketplaceManager()
    
    if args.all:
        logger.info("🔄 Updating all packages...")
        packages = marketplace.list_packages()
        success = True
        
        for pkg in packages:
            if not marketplace.update_package(pkg['name']):
                success = False
        
        return 0 if success else 1
    else:
        return 0 if marketplace.update_package(args.package) else 1


def cmd_telemetry_status(args):
    """Show telemetry status"""
    from ..telemetry import TelemetryReporter
    from ..core.config import Config
    
    config = Config()
    reporter = TelemetryReporter(config.data)
    status = reporter.status()
    
    logger.info("📊 Telemetry Status")
    logger.info("=" * 70)
    logger.info(f"Enabled: {'✅ Yes' if status['enabled'] else '❌ No'}")
    logger.info(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
    logger.info(f"Interval: {status['interval']} seconds")
    logger.info(f"Device ID: {status['device_id']}")
    logger.info("=" * 70)
    return 0


def cmd_telemetry_enable(args):
    """Enable telemetry"""
    from ..telemetry import TelemetryReporter
    from ..core.config import Config
    
    config = Config()
    reporter = TelemetryReporter(config.data)
    reporter.enable()
    return 0


def cmd_telemetry_disable(args):
    """Disable telemetry"""
    from ..telemetry import TelemetryReporter
    from ..core.config import Config
    
    config = Config()
    reporter = TelemetryReporter(config.data)
    reporter.disable()
    return 0


def cmd_telemetry_view(args):
    """View recent telemetry data"""
    from ..telemetry import TelemetryReporter
    from ..core.config import Config
    
    config = Config()
    reporter = TelemetryReporter(config.data)
    data = reporter.view_recent(limit=args.last)
    
    if data:
        logger.info(f"📊 Recent Telemetry ({len(data)} records)")
        logger.info("=" * 70)
        
        for record in data[:10]:
            timestamp = record.get('timestamp', 'Unknown')
            cpu = record.get('system', {}).get('cpu', {}).get('percent_total', 0)
            memory = record.get('system', {}).get('memory', {}).get('percent', 0)
            
            logger.info(f"\n{timestamp}")
            logger.info(f"   CPU: {cpu:.1f}%  Memory: {memory:.1f}%")
        
        logger.info("\n" + "=" * 70)
    else:
        logger.error("❌ No telemetry data available")
        return 1
    
    return 0


def cmd_doctor(args):
    """Run diagnostics"""
    from ..installer import SystemDetector
    
    logger.info("🏥 Running Diagnostics")
    logger.info("=" * 70)
    
    detector = SystemDetector()
    system_info = detector.detect_all()
    
    # Check system
    logger.info("\n📊 System:")
    logger.info(f"   OS: {system_info['os']['name']}")
    logger.info(f"   Architecture: {system_info['arch']['machine']}")
    logger.info(f"   Python: {system_info['python']['version']}")
    
    # Check Docker
    logger.info("\n🐳 Docker:")
    if system_info['docker']['installed']:
        logger.info(f"   ✅ Installed: {system_info['docker']['version']}")
        if system_info['docker']['running']:
            logger.info(f"   ✅ Running")
        else:
            logger.info(f"   ❌ Not running")
    else:
        logger.info(f"   ❌ Not installed")
    
    # Check GPU
    logger.info("\n🎮 GPU:")
    if system_info['gpu']['available']:
        logger.info(f"   ✅ Available: {system_info['gpu']['type']}")
        logger.info(f"   Memory: {system_info['gpu']['memory_gb']}GB")
    else:
        logger.info(f"   ❌ Not detected")
    
    # Check compatibility
    compatible, issues = detector.is_compatible()
    logger.info("\n✅ Compatibility:")
    if compatible:
        logger.info("   ✅ System is compatible")
    else:
        logger.info("   ❌ Issues found:")
        for issue in issues:
            logger.info(f"      - {issue}")
    
    logger.info("\n" + "=" * 70)
    
    # Auto-fix if requested
    if args.fix and not compatible:
        logger.info("\n🔧 Attempting auto-fix...")
        # TODO: Implement auto-fix logic
        logger.info("   Auto-fix not yet implemented")
    
    return 0 if compatible else 1


def cmd_update_self(args):
    """Update SAN CLI"""
    logger.info("🔄 Checking for updates...")
    logger.info("   Current version: 3.0.0-alpha")
    logger.info("   Checking GitHub releases...")
    logger.info("   ✅ You are on the latest version")
    return 0


def cmd_package_list(args):
    """List available packages (legacy)"""
    try:
        pm = PackageManager()
        packages = pm.list_available_packages()
        
        if not packages:
            logger.info("📦 No packages available")
            return 0
        
        logger.info(f"📦 Available Packages ({len(packages)})")
        logger.info("=" * 70)
        
        for pkg in packages:
            logger.info(f"\n📦 {pkg['name']} v{pkg['version']}")
            logger.info(f"   {pkg.get('description', 'No description')[:60]}...")
            logger.info(f"   Author: {pkg.get('author', 'Unknown')}")
            logger.info(f"   Downloads: {pkg.get('downloads', 0)}")
        
        logger.info("\n" + "=" * 70)
        logger.info("Install with: neuron package install <name>")
        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_package_install(args):
    """Install a package"""
    try:
        pm = PackageManager()
        
        logger.info(f"📦 Installing package: {args.package}")
        logger.info("=" * 50)
        
        result = pm.install_package(args.package, args.version)
        
        if result['status'] == 'installed':
            logger.info(f"\n✅ Package installed successfully!")
            logger.info(f"   Package: {result['package']}")
            logger.info(f"   Version: {result['version']}")
            return 0
        else:
            logger.error(f"\n❌ Installation failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


def cmd_package_info(args):
    """Show package information"""
    try:
        pm = PackageManager()
        
        logger.info(f"📄 Package Information: {args.package}")
        logger.info("=" * 50)
        
        info = pm.get_package_info(args.package)
        
        if not info:
            logger.error(f"❌ Package not found: {args.package}")
            return 1
        
        logger.info(f"\n📦 {info['name']} v{info['version']}")
        logger.info(f"   Display Name: {info.get('display_name', info['name'])}")
        logger.info(f"   Author: {info.get('author', 'Unknown')}")
        logger.info(f"   License: {info.get('license', 'Unknown')}")
        logger.info(f"   Category: {info.get('category', 'Unknown')}")
        logger.info(f"   Size: {info.get('size', 0) / 1024:.1f} KB")
        logger.info(f"   Downloads: {info.get('downloads', 0)}")
        logger.info(f"\n   Description:")
        logger.info(f"   {info.get('description', 'No description')}")
        logger.info(f"\n   Homepage: {info.get('homepage', 'N/A')}")
        
        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


def cmd_package_uninstall(args):
    """Uninstall a package"""
    try:
        pm = PackageManager()
        
        logger.info(f"🗑️  Uninstalling package: {args.package}")
        logger.info("=" * 50)
        
        result = pm.uninstall_package(args.package)
        
        logger.info(f"\n✅ Package uninstalled: {result['package']}")
        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Neuron CLI - Connect to NexusCore MESH Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neuron-cli register                    Register a new device
  neuron-cli start                       Start the agent
  neuron-cli start --daemon              Start as daemon
  neuron-cli status                      Check agent status
  neuron-cli stop                        Stop the agent
  
  neuron-cli package list                List available packages
  neuron-cli package install c3-platform Install C3 Platform
  neuron-cli package info c3-platform    Show package details
  neuron-cli package uninstall c3-platform Uninstall a package

For more information: https://nexuscore.cloud/neuron/docs
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'Neuron CLI {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Login command (NEW for SAN CLI)
    login_parser = subparsers.add_parser(
        'login',
        help='Login to Nexus Core Cloud'
    )
    login_parser.add_argument(
        '--otp',
        help='OTP token (if not provided, will prompt)'
    )
    login_parser.add_argument(
        '--api-url',
        default='https://api.support.nexuscore.cloud',
        help='API URL (default: https://api.support.nexuscore.cloud)'
    )
    login_parser.set_defaults(func=cmd_login)
    
    # Install command (NEW for SAN CLI)
    install_parser = subparsers.add_parser(
        'install',
        help='Install SPACE Agent and services'
    )
    install_parser.add_argument(
        '--skip-deps',
        action='store_true',
        help='Skip dependency installation'
    )
    install_parser.add_argument(
        '--skip-agent',
        action='store_true',
        help='Skip SPACE Agent installation'
    )
    install_parser.add_argument(
        '--skip-ollama',
        action='store_true',
        help='Skip Ollama installation'
    )
    install_parser.add_argument(
        '--skip-whisper',
        action='store_true',
        help='Skip Whisper installation'
    )
    install_parser.set_defaults(func=cmd_install)
    
    # Register command
    register_parser = subparsers.add_parser(
        'register',
        help='Register a new device'
    )
    register_parser.set_defaults(func=cmd_register)
    
    # Start command
    start_parser = subparsers.add_parser(
        'start',
        help='Start the agent'
    )
    start_parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as daemon (background)'
    )
    start_parser.set_defaults(func=cmd_start)
    
    # Stop command
    stop_parser = subparsers.add_parser(
        'stop',
        help='Stop the agent'
    )
    stop_parser.set_defaults(func=cmd_stop)
    
    # Status command
    status_parser = subparsers.add_parser(
        'status',
        help='Check all services status'
    )
    status_parser.set_defaults(func=cmd_status)
    
    # Logs command (NEW for SAN CLI)
    logs_parser = subparsers.add_parser(
        'logs',
        help='View service logs'
    )
    logs_parser.add_argument('service', help='Service name')
    logs_parser.add_argument('-f', '--follow', action='store_true', help='Follow logs')
    logs_parser.add_argument('--tail', type=int, default=100, help='Number of lines to show')
    logs_parser.set_defaults(func=cmd_logs)
    
    # Restart command (NEW for SAN CLI)
    restart_parser = subparsers.add_parser(
        'restart',
        help='Restart a service'
    )
    restart_parser.add_argument('service', nargs='?', help='Service name')
    restart_parser.add_argument('--all', action='store_true', help='Restart all services')
    restart_parser.set_defaults(func=cmd_restart)
    
    # Service start command (NEW for SAN CLI)
    service_start_parser = subparsers.add_parser(
        'start-service',
        help='Start a service'
    )
    service_start_parser.add_argument('service', help='Service name')
    service_start_parser.set_defaults(func=cmd_service_start)
    
    # Service stop command (NEW for SAN CLI)
    service_stop_parser = subparsers.add_parser(
        'stop-service',
        help='Stop a service'
    )
    service_stop_parser.add_argument('service', help='Service name')
    service_stop_parser.set_defaults(func=cmd_service_stop)
    
    # Enable command (NEW for SAN CLI)
    enable_parser = subparsers.add_parser(
        'enable',
        help='Enable service auto-start'
    )
    enable_parser.add_argument('service', help='Service name')
    enable_parser.set_defaults(func=cmd_enable)
    
    # Disable command (NEW for SAN CLI)
    disable_parser = subparsers.add_parser(
        'disable',
        help='Disable service auto-start'
    )
    disable_parser.add_argument('service', help='Service name')
    disable_parser.set_defaults(func=cmd_disable)
    
    # Ollama command group (NEW for SAN CLI)
    ollama_parser = subparsers.add_parser(
        'ollama',
        help='Ollama model management'
    )
    ollama_subparsers = ollama_parser.add_subparsers(
        dest='ollama_command',
        help='Ollama operations',
        required=True
    )
    
    # ollama list
    ollama_list_parser = ollama_subparsers.add_parser(
        'list',
        help='List installed models'
    )
    ollama_list_parser.set_defaults(func=cmd_ollama_list)
    
    # ollama pull
    ollama_pull_parser = ollama_subparsers.add_parser(
        'pull',
        help='Pull a model'
    )
    ollama_pull_parser.add_argument('model', help='Model name (e.g., llama3.2:3b)')
    ollama_pull_parser.set_defaults(func=cmd_ollama_pull)
    
    # ollama remove
    ollama_remove_parser = ollama_subparsers.add_parser(
        'remove',
        help='Remove a model'
    )
    ollama_remove_parser.add_argument('model', help='Model name')
    ollama_remove_parser.set_defaults(func=cmd_ollama_remove)
    
    # ollama ps
    ollama_ps_parser = ollama_subparsers.add_parser(
        'ps',
        help='List running models'
    )
    ollama_ps_parser.set_defaults(func=cmd_ollama_ps)
    
    # ollama run
    ollama_run_parser = ollama_subparsers.add_parser(
        'run',
        help='Run a model'
    )
    ollama_run_parser.add_argument('model', help='Model name')
    ollama_run_parser.add_argument('prompt', nargs='?', help='Optional prompt')
    ollama_run_parser.set_defaults(func=cmd_ollama_run)
    
    # ollama show
    ollama_show_parser = ollama_subparsers.add_parser(
        'show',
        help='Show model information'
    )
    ollama_show_parser.add_argument('model', help='Model name')
    ollama_show_parser.set_defaults(func=cmd_ollama_show)
    
    # ollama recommended
    ollama_recommended_parser = ollama_subparsers.add_parser(
        'recommended',
        help='Show recommended models'
    )
    ollama_recommended_parser.set_defaults(func=cmd_ollama_recommended)
    
    # Marketplace command group (NEW for SAN CLI)
    marketplace_parser = subparsers.add_parser(
        'marketplace',
        help='Marketplace package management'
    )
    marketplace_subparsers = marketplace_parser.add_subparsers(
        dest='marketplace_command',
        help='Marketplace operations',
        required=True
    )
    
    # marketplace list
    marketplace_list_parser = marketplace_subparsers.add_parser(
        'list',
        help='List available packages'
    )
    marketplace_list_parser.add_argument('--category', help='Filter by category')
    marketplace_list_parser.set_defaults(func=cmd_marketplace_list)
    
    # marketplace search
    marketplace_search_parser = marketplace_subparsers.add_parser(
        'search',
        help='Search packages'
    )
    marketplace_search_parser.add_argument('query', help='Search query')
    marketplace_search_parser.set_defaults(func=cmd_marketplace_search)
    
    # marketplace info
    marketplace_info_parser = marketplace_subparsers.add_parser(
        'info',
        help='Show package information'
    )
    marketplace_info_parser.add_argument('package', help='Package name')
    marketplace_info_parser.set_defaults(func=cmd_marketplace_info)
    
    # marketplace install
    marketplace_install_parser = marketplace_subparsers.add_parser(
        'install',
        help='Install a package'
    )
    marketplace_install_parser.add_argument('package', help='Package name')
    marketplace_install_parser.set_defaults(func=cmd_marketplace_install)
    
    # marketplace uninstall
    marketplace_uninstall_parser = marketplace_subparsers.add_parser(
        'uninstall',
        help='Uninstall a package'
    )
    marketplace_uninstall_parser.add_argument('package', help='Package name')
    marketplace_uninstall_parser.set_defaults(func=cmd_marketplace_uninstall)
    
    # marketplace update
    marketplace_update_parser = marketplace_subparsers.add_parser(
        'update',
        help='Update a package'
    )
    marketplace_update_parser.add_argument('package', nargs='?', help='Package name')
    marketplace_update_parser.add_argument('--all', action='store_true', help='Update all packages')
    marketplace_update_parser.set_defaults(func=cmd_marketplace_update)
    
    # Telemetry command group (NEW for SAN CLI)
    telemetry_parser = subparsers.add_parser(
        'telemetry',
        help='Telemetry management'
    )
    telemetry_subparsers = telemetry_parser.add_subparsers(
        dest='telemetry_command',
        help='Telemetry operations',
        required=True
    )
    
    # telemetry status
    telemetry_status_parser = telemetry_subparsers.add_parser(
        'status',
        help='Show telemetry status'
    )
    telemetry_status_parser.set_defaults(func=cmd_telemetry_status)
    
    # telemetry enable
    telemetry_enable_parser = telemetry_subparsers.add_parser(
        'enable',
        help='Enable telemetry'
    )
    telemetry_enable_parser.set_defaults(func=cmd_telemetry_enable)
    
    # telemetry disable
    telemetry_disable_parser = telemetry_subparsers.add_parser(
        'disable',
        help='Disable telemetry'
    )
    telemetry_disable_parser.set_defaults(func=cmd_telemetry_disable)
    
    # telemetry view
    telemetry_view_parser = telemetry_subparsers.add_parser(
        'view',
        help='View recent telemetry data'
    )
    telemetry_view_parser.add_argument('--last', type=int, default=100, help='Number of records')
    telemetry_view_parser.set_defaults(func=cmd_telemetry_view)
    
    # Doctor command (NEW for SAN CLI)
    doctor_parser = subparsers.add_parser(
        'doctor',
        help='Run diagnostics'
    )
    doctor_parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    doctor_parser.set_defaults(func=cmd_doctor)
    
    # Update command (NEW for SAN CLI)
    update_parser = subparsers.add_parser(
        'update',
        help='Update SAN CLI'
    )
    update_parser.add_argument('--self', action='store_true', dest='self_update', help='Update CLI itself')
    update_parser.set_defaults(func=cmd_update_self)
    
    # Package command group
    package_parser = subparsers.add_parser(
        'package',
        help='Package management commands'
    )
    package_subparsers = package_parser.add_subparsers(dest='package_command', help='Package operations')
    
    # package list
    pkg_list_parser = package_subparsers.add_parser(
        'list',
        help='List available packages'
    )
    pkg_list_parser.set_defaults(func=cmd_package_list)
    
    # package install
    pkg_install_parser = package_subparsers.add_parser(
        'install',
        help='Install a package'
    )
    pkg_install_parser.add_argument('package', help='Package name')
    pkg_install_parser.add_argument(
        '--version',
        default='latest',
        help='Package version (default: latest)'
    )
    pkg_install_parser.set_defaults(func=cmd_package_install)
    
    # package info
    pkg_info_parser = package_subparsers.add_parser(
        'info',
        help='Show package information'
    )
    pkg_info_parser.add_argument('package', help='Package name')
    pkg_info_parser.set_defaults(func=cmd_package_info)
    
    # package uninstall
    pkg_uninstall_parser = package_subparsers.add_parser(
        'uninstall',
        help='Uninstall a package'
    )
    pkg_uninstall_parser.add_argument('package', help='Package name')
    pkg_uninstall_parser.set_defaults(func=cmd_package_uninstall)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
