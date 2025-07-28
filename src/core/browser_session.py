"""
Discord Username Monitor - Browser Session Acquisition
Uses Selenium to capture authentic browser sessions for enhanced reliability
"""

import json
import time
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from utils.logger import get_logger
from pystyle import Colors


class BrowserSessionAcquisition:
    """Handles browser session acquisition using Selenium"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.session_file = Path("data/browser_sessions.json")
        
    async def acquire_sessions(self, accounts):
        """Acquire browser sessions for accounts"""
        self.logger.info("Starting browser session acquisition")
        
        # Check if we should reuse existing sessions
        if self._should_reuse_sessions():
            return self._load_existing_sessions()
        
        # Acquire new sessions
        return await self._acquire_new_sessions(accounts)
    
    def _should_reuse_sessions(self):
        """Check if we should reuse existing session data"""
        if not self.session_file.exists():
            return False
            
        try:
            file_age = time.time() - self.session_file.stat().st_mtime
            if file_age < 3600:  # Less than 1 hour
                from pystyle import Write
                reuse = Write.Input(
                    f'Found recent session data ({file_age/60:.0f}min old). Reuse? (y/n): ',
                    Colors.blue_to_cyan, interval=0.02
                ).lower()
                return reuse == 'y'
        except Exception as e:
            self.logger.error(f"Error checking session file: {e}")
            
        return False
    
    def _load_existing_sessions(self):
        """Load existing session data from file"""
        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)
            self.logger.info("Loaded existing browser session data")
            return data
        except Exception as e:
            self.logger.error(f"Failed to load existing sessions: {e}")
            return {}
    
    async def _acquire_new_sessions(self, accounts):
        """Acquire new browser sessions using Selenium"""
        print(f"\n{Colors.cyan}━━━ Browser Session Acquisition ━━━{Colors.white}")
        print("Chrome will launch to capture authentic session data")
        
        session_data = {}
        driver = None
        
        try:
            driver = self._create_driver()
            
            for account in accounts:
                print(f"\n{Colors.cyan}Processing account: {account.email}{Colors.white}")
                
                try:
                    account_data = await self._capture_account_session(driver, account)
                    if account_data:
                        session_data[account.email] = account_data
                        print(f"{Colors.green}✓ Session captured for {account.email}{Colors.white}")
                    else:
                        print(f"{Colors.red}✗ Failed to capture session for {account.email}{Colors.white}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing {account.email}: {e}")
                    print(f"{Colors.red}✗ Error processing {account.email}: {e}{Colors.white}")
                    
                # Delay between accounts
                time.sleep(2)
                
        finally:
            if driver:
                driver.quit()
        
        # Save session data
        if session_data:
            self._save_session_data(session_data)
            print(f"{Colors.green}✓ Session data saved{Colors.white}")
        
        return session_data
    
    def _create_driver(self):
        """Create a Chrome WebDriver instance"""
        options = webdriver.ChromeOptions()
        
        # Enhanced stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Enable performance logging for network capture
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        # Uncomment for headless mode
        # options.add_argument('--headless')
        
        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            # Execute stealth script
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except WebDriverException as e:
            self.logger.error(f"Failed to create WebDriver: {e}")
            raise
    
    async def _capture_account_session(self, driver, account):
        """Capture session data for a specific account"""
        try:
            # Navigate to Discord login
            self.logger.info(f"Navigating to Discord login for {account.email}")
            driver.get("https://discord.com/login")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check for Cloudflare
            if "cloudflare" in driver.page_source.lower():
                self.logger.warning("Cloudflare challenge detected")
            
            # Execute login script
            self.logger.info(f"Executing login script for {account.email}")
            login_script = f"""
            const token = '{account.token}';
            
            function login(token) {{
                setInterval(() => {{
                    document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${{token}}"`;
                }}, 50);
                setTimeout(() => {{
                    location.reload();
                }}, 2500);
            }}
            
            login(token);
            """
            
            driver.execute_script(login_script)
            
            # Wait for login
            self.logger.info("Waiting for login completion")
            time.sleep(15)
            
            # Navigate to channels
            driver.get("https://discord.com/channels/@me")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check login success
            current_url = driver.current_url
            login_success = "channels/@me" in current_url and "login" not in current_url
            
            if login_success:
                self.logger.info(f"Login successful for {account.email}")
            else:
                self.logger.warning(f"Login may have failed for {account.email}")
            
            # Capture network requests
            session_data = self._extract_session_data(driver, account, login_success)
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"Session capture failed for {account.email}: {e}")
            return None
    
    def _extract_session_data(self, driver, account, login_success):
        """Extract session data from browser"""
        try:
            # Get performance logs for network requests
            performance_logs = driver.get_log("performance")
            
            headers = {}
            for log_entry in performance_logs:
                try:
                    log = json.loads(log_entry["message"])["message"]
                    if log["method"] == "Network.requestWillBeSent":
                        url = log["params"]["request"]["url"]
                        if "api/v" in url and "users/@me" in url:
                            headers = log["params"]["request"].get("headers", {})
                            break
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Get cookies
            cookies = {}
            try:
                selenium_cookies = driver.get_cookies()
                cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}
            except Exception as e:
                self.logger.warning(f"Failed to get cookies: {e}")
            
            # If no headers captured, generate fallback
            if not headers:
                self.logger.warning(f"No network headers captured for {account.email}, using fallback")
                headers = self._generate_fallback_headers(account.token)
            
            return {
                "email": account.email,
                "token": account.token,
                "headers": headers,
                "cookies": cookies,
                "user_agent": headers.get("User-Agent", ""),
                "authorization": headers.get("Authorization", account.token),
                "x_super_properties": headers.get("X-Super-Properties", ""),
                "login_successful": login_success,
                "captured_at": time.time(),
                "captured_via": "selenium_network_capture" if headers else "fallback_generated"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract session data: {e}")
            return self._generate_fallback_session_data(account)
    
    def _generate_fallback_headers(self, token):
        """Generate fallback headers when capture fails"""
        import base64
        
        super_properties = {
            "os": "Windows",
            "browser": "Chrome", 
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "browser_version": "136.0.0.0",
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "https://discord.com/",
            "referring_domain_current": "discord.com",
            "release_channel": "stable",
            "client_build_number": 423077
        }
        
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": token,
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me",
            "X-Super-Properties": base64.b64encode(json.dumps(super_properties).encode()).decode()
        }
    
    def _generate_fallback_session_data(self, account):
        """Generate fallback session data"""
        return {
            "email": account.email,
            "token": account.token,
            "headers": self._generate_fallback_headers(account.token),
            "cookies": {},
            "login_successful": False,
            "captured_at": time.time(),
            "captured_via": "error_fallback"
        }
    
    def _save_session_data(self, session_data):
        """Save session data to file"""
        try:
            # Ensure data directory exists
            self.session_file.parent.mkdir(exist_ok=True)
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
                
            self.logger.info(f"Session data saved to {self.session_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session data: {e}")