"""
Discord Username Monitor - Configuration Management
Handles loading and validation of configuration settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from utils.logger import get_logger
from pystyle import Colors, Write

class ConfigManager:
    """Manages configuration loading and validation"""
    
    def __init__(self, config_path: str = "config/settings.json"):
        self.logger = get_logger(__name__)
        self.config_path = Path(config_path)
        self.default_config_path = Path("config/example_settings.json")
        self.config = {}
        
    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration"""
        self.logger.info("Loading configuration...")
        
        try:
            # Check if config file exists, if not, copy from example
            if not self.config_path.exists():
                self._create_default_config()
                
            # Load configuration
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                
            # Validate configuration
            self._validate_config()
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            print(f"{Colors.green}✓ Configuration loaded successfully{Colors.white}")
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            print(f"{Colors.red}✗ Error loading configuration: {e}{Colors.white}")
            raise
    
    def _create_default_config(self):
        """Create default configuration file from example"""
        try:
            if self.default_config_path.exists():
                with open(self.default_config_path, 'r', encoding='utf-8') as default_f:
                    default_config = json.load(default_f)
                
                # Ensure config directory exists
                self.config_path.parent.mkdir(exist_ok=True)
                
                with open(self.config_path, 'w', encoding='utf-8') as config_f:
                    json.dump(default_config, config_f, indent=2)
                    
                self.logger.info(f"Created default configuration at {self.config_path}")
                print(f"{Colors.green}✓ Created default configuration{Colors.white}")
                
            else:
                self.logger.error("Default configuration file not found")
                raise FileNotFoundError("Default configuration file not found")
                
        except Exception as e:
            self.logger.error(f"Failed to create default configuration: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration structure and values"""
        required_sections = [
            'monitoring',
            'browser',
            'captcha',
            'webhooks',
            'proxy',
            'logging'
        ]
        
        # Check for required sections
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate monitoring settings
        monitoring = self.config['monitoring']
        if not isinstance(monitoring.get('default_thread_count'), int) or monitoring['default_thread_count'] < 1:
            monitoring['default_thread_count'] = 12
        if not isinstance(monitoring.get('delay_min'), (int, float)) or monitoring['delay_min'] < 0:
            monitoring['delay_min'] = 0.2
        if not isinstance(monitoring.get('delay_max'), (int, float)) or monitoring['delay_max'] < monitoring['delay_min']:
            monitoring['delay_max'] = 1.5
        if not isinstance(monitoring.get('session_timeout'), int) or monitoring['session_timeout'] < 60:
            monitoring['session_timeout'] = 300
        if not isinstance(monitoring.get('max_retries'), int) or monitoring['max_retries'] < 0:
            monitoring['max_retries'] = 3
        if not isinstance(monitoring.get('rate_limit_backoff'), (int, float)) or monitoring['rate_limit_backoff'] < 0:
            monitoring['rate_limit_backoff'] = 1.5
            
        # Validate browser settings
        browser = self.config['browser']
        if not isinstance(browser.get('headless'), bool):
            browser['headless'] = False
        if not browser.get('user_agent'):
            browser['user_agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        if not isinstance(browser.get('session_reuse_time'), int) or browser['session_reuse_time'] < 300:
            browser['session_reuse_time'] = 3600
        if not isinstance(browser.get('login_wait_time'), int) or browser['login_wait_time'] < 5:
            browser['login_wait_time'] = 15
            
        # Validate captcha settings
        captcha = self.config['captcha']
        if not captcha.get('service_url'):
            captcha['service_url'] = "https://freecaptchabypass.com"
        if not isinstance(captcha.get('timeout'), int) or captcha['timeout'] < 30:
            captcha['timeout'] = 120
        if not isinstance(captcha.get('enabled'), bool):
            captcha['enabled'] = False
            
        # Validate webhook settings
        webhooks = self.config['webhooks']
        if not isinstance(webhooks.get('test_on_startup'), bool):
            webhooks['test_on_startup'] = True
        if not isinstance(webhooks.get('periodic_stats'), bool):
            webhooks['periodic_stats'] = True
        if not isinstance(webhooks.get('stats_interval'), int) or webhooks['stats_interval'] < 60:
            webhooks['stats_interval'] = 1800
            
        # Validate proxy settings
        proxy = self.config['proxy']
        if not isinstance(proxy.get('enabled'), bool):
            proxy['enabled'] = False
        if not isinstance(proxy.get('rotation_enabled'), bool):
            proxy['rotation_enabled'] = True
        if not isinstance(proxy.get('timeout'), int) or proxy['timeout'] < 5:
            proxy['timeout'] = 15
        if not isinstance(proxy.get('retry_failed'), bool):
            proxy['retry_failed'] = False
            
        # Validate logging settings
        logging_config = self.config['logging']
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if logging_config.get('level') not in valid_log_levels:
            logging_config['level'] = 'INFO'
        if not logging_config.get('max_file_size', '').endswith(('KB', 'MB', 'GB')):
            logging_config['max_file_size'] = '10MB'
        if not isinstance(logging_config.get('backup_count'), int) or logging_config['backup_count'] < 1:
            logging_config['backup_count'] = 5
            
        # Save validated config
        self._save_config()
    
    def _save_config(self):
        """Save validated configuration back to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            self.logger.info("Validated configuration saved")
        except Exception as e:
            self.logger.error(f"Failed to save validated configuration: {e}")
    
    def get_config(self, section: str = None) -> Dict[str, Any]:
        """Get configuration or specific section"""
        if section:
            return self.config.get(section, {})
        return self.config
