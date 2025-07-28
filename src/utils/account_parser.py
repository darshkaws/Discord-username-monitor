"""
Discord Username Monitor - Account Parser
Handles loading and parsing of account data in various formats
"""

import os
import asyncio
from pathlib import Path
import easygui
from pystyle import Colors, Write
from curl_cffi import requests as curl_requests

from utils.logger import get_logger
from models.account import Account


class AccountParser:
    """Parses and validates Discord account data"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
    async def load_accounts(self):
        """Load accounts from file with interactive selection"""
        print(f"\n{Colors.cyan}━━━ Account Configuration ━━━{Colors.white}")
        
        # Ask for token file
        token_file = easygui.fileopenbox(
            msg="Select your Discord tokens file\n\nSupported formats:\n• email:password:token\n• email:token\n• token",
            title="Discord Username Monitor - Token File",
            filetypes=["*.txt", "*.csv"]
        )
        
        if not token_file or not os.path.exists(token_file):
            print(f"{Colors.red}No token file selected{Colors.white}")
            
            # Check for default file
            default_file = Path("accounts/tokens.txt")
            if default_file.exists():
                print(f"Using default file: {default_file}")
                token_file = str(default_file)
            else:
                print("No tokens available")
                return []
        
        # Load and parse accounts
        accounts = await self._parse_account_file(token_file)
        
        if not accounts:
            print(f"{Colors.red}No valid accounts loaded{Colors.white}")
            return []
        
        # Ask about token validation
        validate_tokens = Write.Input(
            f'Validate tokens before use? (recommended) (y/n): ',
            Colors.blue_to_cyan, interval=0.02
        ).lower() == 'y'
        
        if validate_tokens:
            accounts = await self._validate_accounts(accounts)
        
        print(f"{Colors.green}✓ Loaded {len(accounts)} accounts{Colors.white}")
        return accounts
    
    async def _parse_account_file(self, file_path):
        """Parse account file and return Account objects"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
            
            accounts = []
            supported_formats = set()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    account = self._parse_account_line(line, line_num)
                    if account:
                        accounts.append(account)
                        supported_formats.add(account.format)
                        
                except Exception as e:
                    self.logger.warning(f"Line {line_num} parsing error: {e}")
                    print(f"{Colors.yellow}⚠️  Line {line_num}: {e}{Colors.white}")
                    continue
            
            print(f"Parsed {len(accounts)} accounts in {len(supported_formats)} formats")
            if supported_formats:
                print(f"Detected formats: {', '.join(supported_formats)}")
            
            return accounts
            
        except Exception as e:
            self.logger.error(f"Failed to parse account file: {e}")
            print(f"{Colors.red}Error parsing account file: {e}{Colors.white}")
            return []
    
    def _parse_account_line(self, line, line_num):
        """Parse a single account line"""
        # Determine separator
        separator = ':' if ':' in line else '|' if '|' in line else None
        
        if not separator:
            # Check if it's a token-only line
            if len(line) > 50 and '.' in line:
                return Account(
                    email=f'user_{line_num}@token.local',
                    password=None,
                    token=line,
                    format='token_only',
                    line_num=line_num
                )
            else:
                raise ValueError("Invalid format - not a valid token")
        
        parts = [part.strip() for part in line.split(separator)]
        
        if len(parts) == 2:
            # email:token or username:token
            email, token = parts
            
            # Basic email validation
            if '@' in email:
                return Account(
                    email=email,
                    password=None,
                    token=token,
                    format='email:token',
                    line_num=line_num
                )
            else:
                # Treat as username:token
                return Account(
                    email=f'{email}@username.local',
                    username=email,
                    password=None,
                    token=token,
                    format='username:token',
                    line_num=line_num
                )
                
        elif len(parts) == 3:
            # email:password:token
            email, password, token = parts
            return Account(
                email=email,
                password=password,
                token=token,
                format='email:password:token',
                line_num=line_num
            )
            
        elif len(parts) == 4:
            # username:email:password:token
            username, email, password, token = parts
            return Account(
                username=username,
                email=email,
                password=password,
                token=token,
                format='username:email:password:token',
                line_num=line_num
            )
            
        else:
            raise ValueError(f"Unsupported format - expected 2-4 parts, got {len(parts)}")
    
    async def _validate_accounts(self, accounts):
        """Validate account tokens"""
        print(f"\n{Colors.cyan}Validating {len(accounts)} account tokens...{Colors.white}")
        
        valid_accounts = []
        invalid_count = 0
        
        # Create semaphore to limit concurrent validations
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent validations
        
        async def validate_account(account):
            async with semaphore:
                try:
                    is_valid = await self._validate_token(account.token)
                    
                    if is_valid:
                        print(f"{Colors.green}✓ Valid: {account.email}{Colors.white}")
                        return account
                    else:
                        print(f"{Colors.red}✗ Invalid: {account.email}{Colors.white}")
                        return None
                        
                except Exception as e:
                    self.logger.error(f"Validation error for {account.email}: {e}")
                    print(f"{Colors.red}✗ Error: {account.email} - {e}{Colors.white}")
                    return None
        
        # Run validations concurrently
        tasks = [validate_account(account) for account in accounts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results
        for result in results:
            if isinstance(result, Account):
                valid_accounts.append(result)
            else:
                invalid_count += 1
        
        print(f"\nValidation complete:")
        print(f"  {Colors.green}Valid tokens: {len(valid_accounts)}{Colors.white}")
        print(f"  {Colors.red}Invalid tokens: {invalid_count}{Colors.white}")
        
        return valid_accounts
    
    async def _validate_token(self, token):
        """Validate a single Discord token"""
        try:
            session = curl_requests.Session(impersonate="chrome136")
            
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
            }
            
            response = session.get(
                "https://discord.com/api/v9/users/@me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            elif response.status_code == 429:
                # Rate limited - wait and retry once
                retry_after = float(response.headers.get('Retry-After', 5))
                await asyncio.sleep(min(retry_after, 10))  # Cap at 10 seconds
                
                # Retry once
                response = session.get(
                    "https://discord.com/api/v9/users/@me",
                    headers=headers,
                    timeout=10
                )
                return response.status_code == 200
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return False
    
    def create_example_tokens_file(self):
        """Create an example tokens file"""
        example_content = """# Discord Username Monitor - Account Tokens
# 
# Supported formats:
# 1. email:password:token
# 2. email:token
# 3. token (token only)
#
# Example entries:
# user@example.com:mypassword:MTAxNTExNjQyNzc4MzUyNjQxMA...
# user@example.com:MTAxNTExNjQyNzc4MzUyNjQxMA...
# MTAxNTExNjQyNzc4MzUyNjQxMA...

# Add your tokens below:

"""
        
        try:
            accounts_dir = Path("accounts")
            accounts_dir.mkdir(exist_ok=True)
            
            example_file = accounts_dir / "tokens.txt.example"
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(example_content)
                
            print(f"Example tokens file created: {example_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to create example file: {e}")