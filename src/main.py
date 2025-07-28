#!/usr/bin/env python3
"""
Discord Username Monitor - Main Entry Point
A professional Discord username availability monitoring tool.

Author: Community Project
License: MIT
"""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.monitor import DiscordUsernameMonitor
from utils.logger import setup_logging
from utils.config_manager import ConfigManager
from pystyle import Colors, Write


def display_banner():
    """Display professional banner"""
    banner = '''
╔══════════════════════════════════════════════════════════════════════════════╗
║                      Discord Username Monitor v1.0                          ║
║                        Checker and Monitoring Tool                         ║
║                    github.com/darshkaws/Discord-username-monitor             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ • Real-time Monitoring  • Browser Emulation  • Smart Rate Limiting         ║
║ • Multi-Account Support  • Webhook Notifications  • Proxy Rotation         ║
║ • Session Management  • Comprehensive Logging  • Professional Interface    ║
╚══════════════════════════════════════════════════════════════════════════════╝
    '''
    print(Colors.blue + banner + Colors.white)


def setup_directories():
    """Create necessary directories"""
    directories = ['logs', 'results', 'data', 'config', 'accounts', 'usernames', 'proxies']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
    print(f"{Colors.green}✓ Directory structure initialized{Colors.white}")


def main():
    """Main application entry point"""
    try:
        # Setup
        os.system("cls" if os.name == 'nt' else "clear")
        display_banner()
        setup_directories()
        setup_logging()
        
        print(f"\n{Colors.cyan}Initializing Discord Username Monitor...{Colors.white}")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # Create and run monitor
        monitor = DiscordUsernameMonitor(config)
        
        # Run the monitoring system
        asyncio.run(monitor.start())
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.yellow}Shutdown requested by user{Colors.white}")
        print("All data has been saved. Thank you for using Discord Username Monitor!")
        
    except Exception as e:
        print(f"\n{Colors.red}Critical error: {e}{Colors.white}")
        print("Check logs/error_log.txt for detailed information")
        
    finally:
        input(f"\n{Colors.cyan}Press Enter to exit...{Colors.white}")


if __name__ == "__main__":
    main()