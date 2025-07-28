"""
Discord Username Monitor - Core monitoring logic
"""

import asyncio
import random
import time
import threading
from datetime import datetime
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor
import requests

from curl_cffi import requests as curl_requests
from pystyle import Colors, Write

from .session_manager import SessionManager
from .browser_session import BrowserSessionAcquisition
from .captcha_solver import CaptchaSolver
from utils.webhook_manager import WebhookManager
from utils.proxy_manager import ProxyManager
from utils.account_parser import AccountParser
from utils.logger import get_logger
from models.account import Account
from models.username import Username

class DiscordUsernameMonitor:
    """Main Discord username monitoring class"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Core components
        self.session_manager = SessionManager(config)
        self.browser_session = BrowserSessionAcquisition(config)
        self.captcha_solver = CaptchaSolver(config)
        self.webhook_manager = WebhookManager(config)
        self.proxy_manager = ProxyManager(config)
        
        # Inject captcha solver into session manager
        self.session_manager.captcha_solver = self.captcha_solver
        
        # Statistics
        self.stats = {
            'checked_count': 0,
            'available_found': 0,
            'cycles_completed': 0,
            'current_position': 0,
            'rate_limited_count': 0,
            'start_time': time.time()
        }
        
        # Threading
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        
        # Data storage
        self.accounts = []
        self.username_list = []
        self.username_cycle = None
        self.username_status = {}
        
    async def start(self):
        """Start the monitoring system"""
        try:
            await self._initialize()
            await self._run_monitoring()
        except Exception as e:
            self.logger.error(f"Monitor startup failed: {e}")
            raise
    
    async def _initialize(self):
        """Initialize all components"""
        print(f"\n{Colors.cyan}━━━ Initialization ━━━{Colors.white}")
        
        # Load accounts
        await self._load_accounts()
        
        # Acquire browser sessions
        await self._acquire_browser_sessions()
        
        # Configure webhooks
        await self._configure_webhooks()
        
        # Setup username list
        await self._setup_username_list()
        
        # Configure proxies
        await self._configure_proxies()
        
        # Setup monitoring parameters
        await self._configure_monitoring()
        
        print(f"{Colors.green}✓ Initialization complete{Colors.white}")
    
    async def _load_accounts(self):
        """Load and parse account data"""
        print("Loading accounts...")
        
        parser = AccountParser()
        self.accounts = await parser.load_accounts()
        
        if not self.accounts:
            raise ValueError("No valid accounts loaded")
            
        print(f"✓ Loaded {len(self.accounts)} accounts")
    
    async def _acquire_browser_sessions(self):
        """Acquire authentic browser sessions"""
        print("Acquiring browser sessions...")
        
        session_data = await self.browser_session.acquire_sessions(self.accounts)
        await self.session_manager.initialize_sessions(self.accounts, session_data)
        
        print("✓ Browser sessions acquired")
    
    async def _configure_webhooks(self):
        """Configure webhook notifications"""
        print("Configuring webhooks...")
        
        await self.webhook_manager.configure()
        
        if self.webhook_manager.has_webhooks():
            print("✓ Webhooks configured")
        else:
            print("! No webhooks configured - notifications disabled")
    
    async def _setup_username_list(self):
        """Setup username list for monitoring"""
        print("Setting up username list...")
        
        source = Write.Input(
            'Username source - (f)ile, (d)ictionary, or (g)enerate: ',
            Colors.blue_to_cyan, interval=0.02
        ).lower()
        
        if source == 'f':
            self.username_list = await self._load_username_file()
        elif source == 'd':
            self.username_list = await self._generate_dictionary_usernames()
        elif source == 'g':
            self.username_list = await self._generate_random_usernames()
        else:
            self.username_list = ['test', 'user', 'name', 'cool']
        
        if not self.username_list:
            self.username_list = ['test', 'user', 'name']
            
        self.username_cycle = cycle(self.username_list)
        print(f"✓ Username list ready: {len(self.username_list)} usernames")
    
    async def _configure_proxies(self):
        """Configure proxy rotation"""
        print("Configuring proxies...")
        
        await self.proxy_manager.configure()
        
        if self.proxy_manager.has_proxies():
            print(f"✓ Proxy rotation enabled: {self.proxy_manager.proxy_count()} proxies")
        else:
            print("✓ Direct connection mode")
    
    async def _configure_monitoring(self):
        """Configure monitoring parameters"""
        print("Configuring monitoring parameters...")
        
        self.mode = Write.Input(
            'Monitoring mode - (a)uto-claim or (n)otifications-only: ',
            Colors.blue_to_cyan, interval=0.02
        ).lower()
        
        self.thread_count = int(Write.Input(
            'Worker threads (1-25, recommended: 12): ',
            Colors.blue_to_cyan, interval=0.02
        ) or "12")
        
        self.delay_range = (
            float(Write.Input('Min delay (seconds): ', Colors.blue_to_cyan, interval=0.02) or "0.2"),
            float(Write.Input('Max delay (seconds): ', Colors.blue_to_cyan, interval=0.02) or "1.5")
        )
        
        print(f"✓ Monitoring configured: {self.thread_count} threads, {self.mode} mode")
    
    async def _run_monitoring(self):
        """Run the main monitoring loop"""
        print(f"\n{Colors.green}Starting username monitoring...{Colors.white}")
        print("Press Ctrl+C to stop\n")
        print("=" * 80)
        
        # Start worker tasks
        tasks = []
        for i in range(self.thread_count):
            task = asyncio.create_task(self._worker(i + 1))
            tasks.append(task)
        
        # Start statistics updater
        stats_task = asyncio.create_task(self._stats_updater())
        
        try:
            # Wait for tasks to complete
            await asyncio.gather(*tasks, stats_task)
        except KeyboardInterrupt:
            print(f"\n\n{Colors.yellow}Shutdown requested...{Colors.white}")
            self.stop_event.set()
            
            # Cancel all tasks
            for task in tasks + [stats_task]:
                task.cancel()
            
            # Wait for cancellation
            await asyncio.gather(*tasks, stats_task, return_exceptions=True)
            
        finally:
            await self._display_final_results()
    
    async def _worker(self, worker_id):
        """Worker coroutine for monitoring usernames"""
        worker_name = f"Worker-{worker_id}"
        
        while not self.stop_event.is_set():
            try:
                # Get next username
                username = next(self.username_cycle)
                
                # Add delay
                delay = random.uniform(*self.delay_range)
                await asyncio.sleep(delay)
                
                # Check availability
                is_available, retry_after = await self._check_username_availability(username)
                
                # Handle rate limiting
                if retry_after > 0:
                    await asyncio.sleep(retry_after)
                    continue
                
                # Update statistics
                with self.lock:
                    self.stats['checked_count'] += 1
                    self.stats['current_position'] += 1
                    
                    if self.stats['current_position'] >= len(self.username_list):
                        self.stats['current_position'] = 0
                        self.stats['cycles_completed'] += 1
                
                # Handle availability
                if is_available:
                    await self._handle_available_username(username, worker_name)
                
                # Update display periodically
                if self.stats['checked_count'] % 25 == 0:
                    self._display_stats()
                    
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)
    
    def _get_check_headers(self):
        """Generate headers for username availability check"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "America/New_York",
            "Connection": "keep-alive"
        }
        
    async def _check_username_availability(self, username):
        """Check if a username is available"""
        session = curl_requests.Session(impersonate="chrome136")
        
        # Apply proxy if available
        proxy = self.proxy_manager.get_proxy()
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        
        try:
            response = session.post(
                "https://discord.com/api/v9/unique-username/username-attempt-unauthed",
                json={"username": username},
                headers=self._get_check_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return not data.get('taken', True), 0
                
            elif response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 5))
                
                with self.lock:
                    self.stats['rate_limited_count'] += 1
                
                # Optimize retry delay with proxies
                if proxy and retry_after > 3.0:
                    return False, 0.5  # Quick proxy rotation
                else:
                    return False, min(retry_after, 10.0)
            
            else:
                self.logger.warning(f"Unexpected status {response.status_code} for {username}")
                return False, 2
                
        except Exception as e:
            self.logger.error(f"Check error for {username}: {e}")
            return False, 5
    
    
        # CAPTCHA SOLVER METHOD 
    def solve_hcaptcha(self, sitekey, rqdata=None):
        """Solve hCaptcha using external service"""
        task_id = None
        try:
            # Create captcha task
            task_payload = {
                "clientKey": self.captcha_client_key,
                "task": {
                    "type": "HCaptchaEnterpriseTask",
                    "websiteURL": "https://discord.com",
                    "websitePublicKey": sitekey,
                    # "isInvisible": False,
                    "data": rqdata
                }
            }
            
            response = requests.post(
                f"{self.captcha_service_url}/createTask",
                json=task_payload,
                timeout=10
            )
            print(f"[DEBUG] createTask status={response.status_code}, body={response.text}")
            
            if response.status_code == 200:
                task_data = response.json()
                if task_data.get("errorId") == 0:
                    task_id = task_data["taskId"]
            
            if not task_id:
                return None

            # Poll for solution
            start_time = time.time()
            while time.time() - start_time < 120:  # 2 min timeout
                time.sleep(5)
                result_payload = {"clientKey": self.captcha_client_key, "taskId": task_id}
                result_response = requests.post(
                    f"{self.captcha_service_url}/getTaskResult",
                    json=result_payload,
                    timeout=10
                )
                print(f"[DEBUG] getTaskResult status={result_response.status_code}, body={result_response.text}")
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get("status") == "ready":
                        return result_data["solution"]["gRecaptchaResponse"]
        
        except Exception as e:
            self.log_error(f"CAPTCHA solving failed: {str(e)}")
        return None

    async def _handle_available_username(self, username, worker_name):
        """Handle when a username becomes available"""
        print(f"\n{Colors.green}🎯 [{worker_name}] {username} is AVAILABLE!{Colors.white}")
        
        # Get account for claiming
        account = self._get_next_account()
        
        # Log immediately
        self._log_available_username(username, account)
        
        with self.lock:
            self.stats['available_found'] += 1
        
        # Handle based on mode
        if self.mode == 'a':
            # Auto-claim mode
            claim_success = await self._attempt_claim(username, account)
            await self.webhook_manager.send_notification(username, account, claim_success)
        else:
            # Notification-only mode
            await self.webhook_manager.send_notification(username, account)
        
        print(f"{Colors.green}🎉 [{worker_name}] Notification sent for {username}!{Colors.white}")
    
            # ===== NEW: AUTOMATIC CLAIM METHOD =====
    async def _attempt_claim(self, username, account):
        """Attempt to claim username using session manager"""
        try:
            success = await self.session_manager.claim_username(account, username)
            return success
        except Exception as e:
            self.logger.error(f"Claim attempt failed for {username}: {e}")
            return False
    
    def _get_next_account(self):
        """Get next account for claiming"""
        return random.choice(self.accounts)
    
    def _log_available_username(self, username, account):
        """Log available username immediately"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to results file
        result_line = f"{username}:{account.email}:{account.password or 'N/A'}:{account.token}\n"
        
        try:
            with open("results/available_usernames.txt", "a", encoding="utf-8") as f:
                f.write(result_line)
                f.flush()
                
            self.logger.info(f"AVAILABLE: {username} - {account.email}")
            
        except Exception as e:
            self.logger.error(f"Failed to log available username: {e}")
    
    def _display_stats(self):
        """Display live statistics"""
        runtime = int(time.time() - self.stats['start_time'])
        hours, remainder = divmod(runtime, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        checks_per_min = (self.stats['checked_count'] / (runtime / 60)) if runtime > 0 else 0
        
        stats_line = (f"{Colors.blue}Checked: {self.stats['checked_count']} | "
                     f"{Colors.green}Found: {self.stats['available_found']} | "
                     f"{Colors.cyan}Cycles: {self.stats['cycles_completed']} | "
                     f"{Colors.yellow}Speed: {checks_per_min:.1f}/min | "
                     f"{Colors.white}Runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        print(f"\r{' ' * 120}", end="")
        print(f"\r{stats_line}", end="", flush=True)
    
    async def _stats_updater(self):
        """Background stats updater"""
        while not self.stop_event.is_set():
            try:
                await asyncio.sleep(30)
                self._save_session_stats()
            except Exception as e:
                self.logger.error(f"Stats updater error: {e}")
    
    def _save_session_stats(self):
        """Save session statistics"""
        import json
        
        stats_data = {
            **self.stats,
            "runtime_seconds": int(time.time() - self.stats['start_time']),
            "total_usernames": len(self.username_list),
            "thread_count": self.thread_count,
            "mode": self.mode,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open("data/session_stats.json", "w") as f:
                json.dump(stats_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save stats: {e}")
    
    async def _display_final_results(self):
        """Display final session results"""
        runtime = int(time.time() - self.stats['start_time'])
        hours, remainder = divmod(runtime, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        print(f"\n{Colors.cyan}{'='*80}")
        print("SESSION COMPLETE")
        print(f"{'='*80}{Colors.white}")
        
        print(f"Available usernames found: {Colors.green}{self.stats['available_found']}{Colors.white}")
        print(f"Total usernames checked: {self.stats['checked_count']}")
        print(f"Cycles completed: {self.stats['cycles_completed']}")
        print(f"Total runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        if self.stats['available_found'] > 0:
            print(f"\n{Colors.green}Results saved to results/available_usernames.txt{Colors.white}")
        
        print(f"\n{Colors.blue}Discord Username Monitor v2.0{Colors.white}")
    
    # Helper methods for username list setup
    async def _load_username_file(self):
        """Load usernames from file"""
        import easygui
        
        file_path = easygui.fileopenbox(
            msg="Select username list file",
            title="Username List",
            filetypes=["*.txt"]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    usernames = [line.strip().lower() for line in f if line.strip()]
                return list(set(usernames))
            except Exception as e:
                self.logger.error(f"Failed to load username file: {e}")
        
        return []
    
    async def _generate_dictionary_usernames(self):
        """Generate usernames from dictionary"""
        try:
            import nltk
            nltk.download('words', quiet=True)
            from nltk.corpus import words
            
            word_list = words.words()
            filtered = [w.lower() for w in word_list if 2 <= len(w) <= 12 and w.isalpha()]
            return random.sample(filtered, min(3000, len(filtered)))
            
        except ImportError:
            self.logger.warning("NLTK not available, using basic word list")
            return ['cat', 'dog', 'sun', 'moon', 'star', 'fire', 'water', 'earth']
    
    async def _generate_random_usernames(self):
        """Generate random usernames"""
        import string
        
        count = int(Write.Input('Number of usernames (100-5000): ', Colors.blue_to_cyan, interval=0.02) or "1000")
        length = int(Write.Input('Username length (2-12): ', Colors.blue_to_cyan, interval=0.02) or "4")
        
        usernames = set()
        chars = string.ascii_lowercase + string.digits
        
        while len(usernames) < count:
            username = ''.join(random.choices(chars, k=length))
            usernames.add(username)
            
            if len(usernames) > count * 2:  # Prevent infinite loop
                break
        
        return list(usernames)