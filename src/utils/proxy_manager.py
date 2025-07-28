"""
Discord Username Monitor - Proxy Management
Handles proxy rotation and validation for enhanced anonymity
"""

import random
import requests
import time
import threading
from pathlib import Path
from urllib.parse import urlparse
from pystyle import Colors, Write
from utils.logger import get_logger


class ProxyManager:
    """Manages proxy rotation and validation"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        self.proxies = []
        self.working_proxies = []
        self.failed_proxies = set()
        self.current_index = 0
        self.lock = threading.Lock()
        
        # Configuration
        self.enabled = False
        self.rotation_enabled = True
        self.timeout = config.get('proxy', {}).get('timeout', 15)
        self.retry_failed = config.get('proxy', {}).get('retry_failed', False)
    
    async def configure(self):
        """Configure proxy settings interactively"""
        print(f"\n{Colors.cyan}━━━ Proxy Configuration ━━━{Colors.white}")
        
        use_proxies = Write.Input(
            'Use proxies for enhanced anonymity? (y/n): ',
            Colors.blue_to_cyan, interval=0.02
        ).lower()
        
        if use_proxies != 'y':
            print("Direct connection mode enabled")
            self.enabled = False
            return
        
        # Load proxies from file
        await self._load_proxies()
        
        if not self.proxies:
            print(f"{Colors.red}No proxies loaded - using direct connection{Colors.white}")
            self.enabled = False
            return
        
        # Test proxies
        test_proxies = Write.Input(
            f'Test proxies before use? (recommended) (y/n): ',
            Colors.blue_to_cyan, interval=0.02
        ).lower() == 'y'
        
        if test_proxies:
            await self._test_proxies()
        else:
            self.working_proxies = self.proxies.copy()
        
        if self.working_proxies:
            self.enabled = True
            print(f"{Colors.green}✓ Proxy rotation enabled: {len(self.working_proxies)} proxies{Colors.white}")
        else:
            print(f"{Colors.red}No working proxies found - using direct connection{Colors.white}")
            self.enabled = False
    
    async def _load_proxies(self):
        """Load proxies from file"""
        proxy_file = None
        
        # Check for default proxy file
        default_file = Path("proxies/proxies.txt")
        if default_file.exists():
            proxy_file = str(default_file)
            print(f"Found proxy file: {proxy_file}")
        else:
            # Ask user to select file
            import easygui
            proxy_file = easygui.fileopenbox(
                msg="Select proxy list file\n\nSupported formats:\n• ip:port\n• ip:port:username:password\n• http://ip:port",
                title="Proxy File Selection",
                filetypes=["*.txt"]
            )
        
        if not proxy_file:
            print("No proxy file selected")
            return
        
        try:
            with open(proxy_file, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    proxy = self._parse_proxy_line(line)
                    if proxy:
                        self.proxies.append(proxy)
                except Exception as e:
                    self.logger.warning(f"Invalid proxy on line {line_num}: {e}")
            
            print(f"Loaded {len(self.proxies)} proxies from file")
            
        except Exception as e:
            self.logger.error(f"Failed to load proxy file: {e}")
            print(f"{Colors.red}Error loading proxy file: {e}{Colors.white}")
    
    def _parse_proxy_line(self, line):
        """Parse a single proxy line"""
        # Handle different proxy formats
        if line.startswith('http://') or line.startswith('https://'):
            # URL format: http://ip:port or http://user:pass@ip:port
            return line
        
        parts = line.split(':')
        
        if len(parts) == 2:
            # ip:port
            ip, port = parts
            return f"http://{ip}:{port}"
        
        elif len(parts) == 4:
            # ip:port:username:password
            ip, port, username, password = parts
            return f"http://{username}:{password}@{ip}:{port}"
        
        else:
            raise ValueError(f"Invalid proxy format: {line}")
    
    async def _test_proxies(self):
        """Test proxies for connectivity"""
        print(f"\n{Colors.cyan}Testing {len(self.proxies)} proxies...{Colors.white}")
        
        working_count = 0
        failed_count = 0
        
        for i, proxy in enumerate(self.proxies, 1):
            try:
                # Test with Discord's API
                response = requests.get(
                    "https://discord.com/api/v9/experiments",
                    proxies={"http": proxy, "https": proxy},
                    timeout=self.timeout,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                if response.status_code == 200:
                    self.working_proxies.append(proxy)
                    working_count += 1
                    print(f"{Colors.green}✓ Proxy {i}/{len(self.proxies)} working{Colors.white}")
                else:
                    failed_count += 1
                    print(f"{Colors.red}✗ Proxy {i}/{len(self.proxies)} failed (HTTP {response.status_code}){Colors.white}")
                    
            except Exception as e:
                failed_count += 1
                print(f"{Colors.red}✗ Proxy {i}/{len(self.proxies)} failed: {e}{Colors.white}")
                
            # Small delay between tests
            time.sleep(0.2)
        
        print(f"\nProxy testing complete:")
        print(f"  {Colors.green}Working: {working_count}{Colors.white}")
        print(f"  {Colors.red}Failed: {failed_count}{Colors.white}")
    
    def get_proxy(self):
        """Get next proxy for use"""
        if not self.enabled or not self.working_proxies:
            return None
        
        with self.lock:
            if not self.rotation_enabled:
                # Always use first proxy
                return self.working_proxies[0]
            
            # Rotate through working proxies
            proxy = self.working_proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.working_proxies)
            
            return proxy
    
    def get_random_proxy(self):
        """Get random proxy"""
        if not self.enabled or not self.working_proxies:
            return None
        
        return random.choice(self.working_proxies)
    
    def mark_proxy_failed(self, proxy):
        """Mark a proxy as failed"""
        if not self.retry_failed:
            with self.lock:
                if proxy in self.working_proxies:
                    self.working_proxies.remove(proxy)
                    self.failed_proxies.add(proxy)
                    self.logger.warning(f"Proxy marked as failed: {proxy}")
    
    def has_proxies(self):
        """Check if proxies are available"""
        return self.enabled and len(self.working_proxies) > 0
    
    def proxy_count(self):
        """Get count of working proxies"""
        return len(self.working_proxies) if self.enabled else 0
    
    def get_proxy_stats(self):
        """Get proxy statistics"""
        return {
            'enabled': self.enabled,
            'total_loaded': len(self.proxies),
            'working': len(self.working_proxies),
            'failed': len(self.failed_proxies),
            'current_index': self.current_index
        }
    
    def create_example_proxy_file(self):
        """Create an example proxy file"""
        example_content = """# Discord Username Monitor - Proxy List
# 
# Supported formats:
# 1. ip:port
# 2. ip:port:username:password
# 3. http://ip:port
# 4. http://username:password@ip:port
#
# Example entries:
# 127.0.0.1:8080
# 192.168.1.1:3128:user:pass
# http://proxy.example.com:8080
# http://user:pass@proxy.example.com:8080

# Add your proxies below:

"""
        
        try:
            proxies_dir = Path("proxies")
            proxies_dir.mkdir(exist_ok=True)
            
            example_file = proxies_dir / "proxies.txt.example"
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(example_content)
                
            print(f"Example proxy file created: {example_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to create example proxy file: {e}")