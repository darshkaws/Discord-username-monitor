"""
Discord Username Monitor - Session Management
Handles persistent Discord API sessions with proper authentication
"""

import time
import threading
import base64
import json
import random
import string
from curl_cffi import requests as curl_requests
import asyncio
from pystyle import Colors, Colorate, Write, Center
from utils.logger import get_logger
import traceback
import discord

class SessionManager:
    """Manages persistent Discord API sessions"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        self.sessions = {}
        self.session_lock = threading.Lock()
        self.fingerprint_cache = None
        
    async def initialize_sessions(self, accounts, session_data):
        """Initialize sessions for all accounts"""
        self.logger.info(f"Initializing sessions for {len(accounts)} accounts")
        
        initialized = 0
        failed = 0
        
        for account in accounts:
            try:
                session = await self._create_session(account, session_data.get(account.email, {}))
                if session:
                    with self.session_lock:
                        self.sessions[account.email] = {
                            'session': session,
                            'created': time.time(),
                            'account': account,
                            'failures': 0
                        }
                    initialized += 1
                    self.logger.info(f"Session initialized: {account.email}")
                else:
                    failed += 1
                    self.logger.error(f"Session failed: {account.email}")
                    
                # Prevent rate limiting during initialization
                await asyncio.sleep(0.3)
                
            except Exception as e:
                failed += 1
                self.logger.error(f"Session error for {account.email}: {e}")
        
        self.logger.info(f"Sessions initialized: {initialized} success, {failed} failed")
    
    async def _create_session(self, account, browser_data):
        """Create a persistent session for an account"""
        try:
            session = curl_requests.Session(impersonate="chrome136")
            
            # Use browser data if available, otherwise generate headers
            if browser_data and browser_data.get('headers'):
                session.headers.update(browser_data['headers'])
                if browser_data.get('cookies'):
                    session.cookies.update(browser_data['cookies'])
            else:
                session.headers.update(self._generate_headers(account.token))
                # Fetch initial cookies
                try:
                    response = session.get("https://discord.com/login", timeout=10)
                    # Cookies are automatically handled by the session
                except Exception as e:
                    self.logger.warning(f"Failed to fetch initial cookies: {e}")
            
            # Validate session
            if await self._validate_session(session):
                return session
            else:
                session.close()
                return None
                
        except Exception as e:
            self.logger.error(f"Session creation failed: {e}")
            return None
    
    async def _validate_session(self, session):
        """Validate that a session is working"""
        try:
            response = session.get("https://discord.com/api/v9/users/@me", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_session(self, account_email):
        """Get a session for an account"""
        with self.session_lock:
            if account_email not in self.sessions:
                return None
                
            session_data = self.sessions[account_email]
            
            # Check if session is too old (5 minutes)
            if time.time() - session_data['created'] > 300:
                try:
                    session_data['session'].close()
                except:
                    pass
                del self.sessions[account_email]
                return None
            
            return session_data['session']
    
    def _generate_headers(self, token):
        """Generate Discord headers for a token"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Authorization": token,
            "Origin": "https://discord.com",
            "Referer": "https://discord.com/channels/@me",
            "Sec-Ch-Ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Super-Properties": self._generate_super_properties(),
            "X-Discord-Locale": "en-US",
            "X-Discord-Timezone": "America/New_York",
            "X-Fingerprint": self._get_fingerprint(),
            "X-Context-Properties": "e30=",  # Base64 empty JSON
            "DNT": "1",
            "Connection": "keep-alive"
        }
    
    def _generate_super_properties(self):
        """Generate X-Super-Properties header"""
        properties = {
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
            "client_build_number": 423077,
            "client_event_source": None,
            "has_client_mods": False,
            "client_launch_id": self._generate_uuid(),
            "launch_signature": self._generate_uuid(),
            "client_app_state": "focused",
            "client_heartbeat_session_id": self._generate_uuid(),
            "design_id": 0
        }
        
        return base64.b64encode(
            json.dumps(properties, separators=(',', ':')).encode()
        ).decode()
    
    def _generate_uuid(self):
        """Generate a UUID-like string"""
        return f"{random.randint(10000000, 99999999):08x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{''.join(random.choices(string.hexdigits.lower(), k=12))}"
    
    def _get_fingerprint(self):
        """Get Discord fingerprint"""
        if self.fingerprint_cache:
            return self.fingerprint_cache
            
        try:
            session = curl_requests.Session(impersonate="chrome136")
            response = session.get("https://discord.com/api/v9/experiments", timeout=10)
            
            if response.status_code == 200:
                self.fingerprint_cache = response.json().get("fingerprint", "")
                return self.fingerprint_cache
                
        except Exception as e:
            self.logger.warning(f"Failed to get fingerprint: {e}")
            
        return ""
    
    def cleanup_sessions(self):
        """Clean up old or invalid sessions"""
        current_time = time.time()
        
        with self.session_lock:
            emails_to_remove = []
            
            for email, session_data in self.sessions.items():
                # Remove sessions older than 10 minutes
                if current_time - session_data['created'] > 600:
                    emails_to_remove.append(email)
            
            for email in emails_to_remove:
                try:
                    self.sessions[email]['session'].close()
                except:
                    pass
                del self.sessions[email]
                self.logger.info(f"Session cleaned up: {email}")
    
        # ===== NEW: AUTOMATIC CLAIM METHOD =====
    async def claim_username(self, account, username):
        """
        Attempt to claim a username using discord.py client first, falling back to session-based approach
        """
        client = None
        email = account.email
        password = account.password
        token = account.token

        # Validate required account information
        if not email or not token:
            self.logger.error(f"No email or token in account: {email or 'unknown'}")
            return False
        if not password:
            self.logger.error(f"No password in account: {email}. Cannot claim {username}")
            return False

        try:
            # Step 1: Attempt discord.py client connection
            client = discord.Client()

            async def attempt_client_connection():
                try:
                    await client.start(token)
                except Exception as e:
                    self.logger.error(f"Client start error for {email}: {e}")
                    raise

            # Run client connection in a task
            task = asyncio.create_task(attempt_client_connection())

            try:
                # Wait for the client to be ready
                await asyncio.wait_for(client.wait_until_ready(), timeout=12)

                # Step 2: Attempt to claim username with discord.py
                try:
                    await client.user.edit(username=username, password=password)
                    self.logger.info(f"SUCCESS: Claimed {username} with {email} via discord.py")
                    print(f"\n{Colors.green}🎉 SUCCESS! Claimed {username} for {email} via discord.py!{Colors.white}")
                    return True
                except discord.errors.HTTPException as e:
                    self.logger.error(f"Discord.py claim failed for {username} with {email}: {e}")
                    # Continue to session-based approach
                except Exception as e:
                    self.logger.error(f"Unexpected error during discord.py claim for {username} with {email}: {e}")
                    # Continue to session-based approach
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout waiting for client ready for {email}")
                # Continue to session-based approach

            # Step 3: Fallback to session-based claim
            self.logger.info(f"FALLBACK: Attempting session-based claim for {username} with {email}")
            
            # Get session for this account
            session = self.get_session(account.email)
            if not session:
                # Create new session if needed
                session_data = {}  # You might want to load this from browser_session data
                session = await self._create_session(account, session_data)
                if not session:
                    self.logger.error(f"Failed to create session for {email}")
                    return False

            # Step 4: Perform pomelo-attempt
            self.logger.info(f"CLAIM_FLOW: [{username}] Attempting pomelo check with {email}")
            pomelo_payload = {"username": username}
            pomelo_response = session.post(
                "https://discord.com/api/v9/users/@me/pomelo-attempt",
                json=pomelo_payload,
                timeout=15
            )
            self.logger.info(f"POMELO_ATTEMPT: [{username}] Status: {pomelo_response.status_code}")

            if pomelo_response.status_code != 200:
                self.logger.error(f"Pomelo attempt failed for {username}: {pomelo_response.status_code}")
                if pomelo_response.status_code == 429:
                    retry_after = float(pomelo_response.headers.get('Retry-After', 5))
                    self.logger.info(f"RATE_LIMIT: Pomelo attempt for {username}, retry after {retry_after}s")
                    await asyncio.sleep(retry_after)
                return False

            # Step 5: Attempt the final claim
            self.logger.info(f"CLAIM_FLOW: [{username}] Pomelo success. Proceeding to final claim.")
            claim_payload = {"username": username, "password": password}
            claim_response = session.patch(
                "https://discord.com/api/v9/users/@me", 
                json=claim_payload,
                timeout=15
            )

            # Step 6: Handle potential CAPTCHA challenge
            if claim_response.status_code == 400:
                try:
                    error_data = claim_response.json()
                    if 'captcha_key' in error_data:
                        self.logger.info(f"CAPTCHA_REQUIRED: [{username}] - Challenge received.")
                        
                        # Use the captcha solver from the main monitor
                        # from core.discord_monitor import DiscordUsernameMonitor
                        captcha_solution = None
                        
                        # This is a bit of a hack - ideally captcha solver should be injected
                        if hasattr(self, 'captcha_solver'):
                            captcha_solution = await self.captcha_solver.solve_hcaptcha(
                                error_data.get("captcha_sitekey"), 
                                error_data.get("captcha_rqdata")
                            )
                        
                        # In SessionManager.claim_username, after CAPTCHA solving
                        if captcha_solution:
                            self.logger.info(f"CAPTCHA_SOLVED: [{username}] - Retrying claim with solution.")
                            claim_payload["captcha_key"] = captcha_solution
                            if error_data.get("captcha_rqtoken"):
                                claim_payload["captcha_rqtoken"] = error_data.get("captcha_rqtoken")
                            claim_response = session.patch(
                                "https://discord.com/api/v9/users/@me",
                                json=claim_payload,
                                timeout=15
                            )
                            # Retry once more if still 400
                            if claim_response.status_code == 400:
                                self.logger.info(f"RETRY: Attempting claim again for {username} due to 400 status")
                                claim_response = session.patch(
                                    "https://discord.com/api/v9/users/@me",
                                    json=claim_payload,
                                    timeout=15
                                )
                        else:
                            self.logger.error(f"CAPTCHA solving failed for {username}. Aborting claim.")
                            return False
                except json.JSONDecodeError:
                    pass

            # Step 7: Final check for success
            if claim_response.status_code == 200:
                self.logger.info(f"SUCCESS: Claimed {username} with {email} via session-based approach!")
                print(f"\n{Colors.green}🎉 SUCCESS! Claimed {username} for {email} via session-based approach!{Colors.white}")
                return True
            else:
                self.logger.error(f"FINAL CLAIM FAILED for {username}: {claim_response.status_code} - {claim_response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Claim error for {username} with {email}: {str(e)}")
            return False
        finally:
            # Ensure the client is closed
            if client and not client.is_closed():
                try:
                    await client.close()
                except Exception as e:
                    self.logger.error(f"Error closing client for {email}: {e}")