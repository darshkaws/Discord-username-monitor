"""
Discord Username Monitor - Webhook Management
Handles Discord webhook notifications with smart routing
"""

import requests
import asyncio
from datetime import datetime
from pystyle import Colors, Write
from utils.logger import get_logger


class WebhookManager:
    """Manages Discord webhook notifications"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        self.webhooks = {}
        
    async def configure(self):
        """Configure Discord webhooks interactively"""
        print(f"\n{Colors.cyan}━━━ Webhook Configuration ━━━{Colors.white}")
        print("Webhooks provide real-time notifications when usernames become available")
        
        use_webhooks = Write.Input(
            'Enable webhook notifications? (y/n): ',
            Colors.blue_to_cyan, interval=0.02
        ).lower()
        
        if use_webhooks != 'y':
            print("Webhook notifications disabled")
            return
        
        # Ask for webhook strategy
        use_multiple = Write.Input(
            'Use separate webhooks for different username types? (y/n): ',
            Colors.blue_to_cyan, interval=0.02
        ).lower() == 'y'
        
        if use_multiple:
            await self._configure_multiple_webhooks()
        else:
            await self._configure_single_webhook()
        
        # Send test notifications
        if self.webhooks:
            await self._send_test_notifications()
    
    async def _configure_single_webhook(self):
        """Configure single webhook for all notifications"""
        print(f"\n{Colors.cyan}Configuring single webhook:{Colors.white}")
        
        url = Write.Input(
            'Discord webhook URL: ',
            Colors.blue_to_cyan, interval=0.02
        ).strip()
        
        if url and await self._test_webhook(url):
            self.webhooks['all'] = url
            print(f"{Colors.green}✓ Webhook configured successfully{Colors.white}")
        elif url:
            print(f"{Colors.red}✗ Webhook test failed{Colors.white}")
        else:
            print("No webhook URL provided")
    
    async def _configure_multiple_webhooks(self):
        """Configure multiple webhooks for different categories"""
        print(f"\n{Colors.cyan}Configuring targeted webhooks:{Colors.white}")
        
        categories = {
            'rare': '3-character and shorter usernames (ultra rare)',
            '4char': '4-character usernames (rare)',
            'standard': 'All other usernames (5+ characters)'
        }
        
        for category, description in categories.items():
            url = Write.Input(
                f'[{category.upper()}] {description} - Webhook URL (or skip): ',
                Colors.blue_to_cyan, interval=0.02
            ).strip()
            
            if url and await self._test_webhook(url):
                self.webhooks[category] = url
                print(f"{Colors.green}✓ {category} webhook configured{Colors.white}")
            elif url:
                print(f"{Colors.red}✗ {category} webhook test failed{Colors.white}")
    
    async def _test_webhook(self, url):
        """Test webhook with a simple message"""
        try:
            test_payload = {
                "embeds": [{
                    "title": "✓ Discord Username Monitor",
                    "description": "Webhook test successful - Monitoring system ready",
                    "color": 0x00ff88,
                    "footer": {"text": "Discord Username Monitor v2.0"},
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            response = requests.post(url, json=test_payload, timeout=10)
            return response.status_code == 204
            
        except Exception as e:
            self.logger.error(f"Webhook test failed: {e}")
            return False
    
    async def _send_test_notifications(self):
        """Send test notifications to configured webhooks"""
        print(f"\n{Colors.cyan}Sending test notifications...{Colors.white}")
        
        for webhook_name, webhook_url in self.webhooks.items():
            try:
                await self._send_startup_notification(webhook_url, webhook_name)
                print(f"{Colors.green}✓ Test sent to {webhook_name} webhook{Colors.white}")
            except Exception as e:
                print(f"{Colors.red}✗ Failed to send test to {webhook_name}: {e}{Colors.white}")
                self.logger.error(f"Test notification failed for {webhook_name}: {e}")
    
    async def _send_startup_notification(self, webhook_url, webhook_name):
        """Send startup notification"""
        embed = {
            "title": "🚀 Discord Username Monitor Started",
            "description": f"Monitoring system initialized successfully\nWebhook: {webhook_name}",
            "color": 0x3498db,
            "fields": [
                {
                    "name": "Status",
                    "value": "✅ Active and monitoring",
                    "inline": True
                },
                {
                    "name": "Mode",
                    "value": "Real-time notifications",
                    "inline": True
                }
            ],
            "footer": {"text": "Discord Username Monitor v2.0"},
            "timestamp": datetime.now().isoformat()
        }
        
        payload = {"embeds": [embed]}
        requests.post(webhook_url, json=payload, timeout=10)
    
    def has_webhooks(self):
        """Check if any webhooks are configured"""
        return len(self.webhooks) > 0
    
    async def send_notification(self, username, account, claim_success=None):
        """Send notification for available username"""
        webhook_url = self._get_webhook_for_username(username)
        if not webhook_url:
            return
        
        try:
            embed = self._create_notification_embed(username, account, claim_success)
            
            # Create payload
            payload = {"embeds": [embed]}
            
            # Add mention for rare usernames
            if len(username) <= 3:
                payload["content"] = f"@everyone **ULTRA RARE ALERT ({len(username)} chars):** `{username}`"
            elif len(username) == 4:
                payload["content"] = f"@here **RARE USERNAME (4 chars):** `{username}`"
            
            # Add action buttons for available usernames
            if claim_success is None:  # Available, not claimed yet
                payload["components"] = [{
                    "type": 1,
                    "components": [{
                        "type": 2,
                        "style": 5,
                        "label": "Login to Discord",
                        "url": "https://discord.com/login"
                    }, {
                        "type": 2,
                        "style": 5,
                        "label": "Username Settings",
                        "url": "https://discord.com/channels/@me/settings/profile"
                    }]
                }]
            
            # Send notification
            response = requests.post(webhook_url, json=payload, timeout=15)
            
            if response.status_code == 204:
                self.logger.info(f"Notification sent: {username}")
            else:
                self.logger.error(f"Notification failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Notification error for {username}: {e}")
    
    def _create_notification_embed(self, username, account, claim_success):
        """Create Discord embed for notification"""
        username_len = len(username)
        
        # Determine embed properties based on status
        if claim_success is True:
            title = f"🎉 CLAIMED: {username}"
            color = 0x00ff88
            description = f"Successfully claimed **{username}**!"
        elif claim_success is False:
            title = f"❌ CLAIM FAILED: {username}"
            color = 0xff4444
            description = f"Failed to claim **{username}** - manual action needed"
        else:
            # Available username
            if username_len <= 3:
                title = f"🔥 ULTRA RARE USERNAME AVAILABLE ({username_len} chars)"
                color = 0xff6600
            elif username_len == 4:
                title = f"⭐ RARE USERNAME AVAILABLE (4 chars)"
                color = 0xff9900
            else:
                title = f"✨ Username Available"
                color = 0x4488ff
            
            description = f"**`{username}`** is ready for claiming!"
        
        # Create embed
        embed = {
            "title": title,
            "description": description,
            "color": color,
            "fields": [
                {
                    "name": "Account Credentials",
                    "value": f"```\nEmail: {account.email}\nPassword: {account.password or 'N/A'}\nToken: {account.token[:20]}...\n```",
                    "inline": False
                },
                {
                    "name": "Username Details",
                    "value": f"Length: {username_len} characters\nRarity: {self._get_rarity_text(username_len)}",
                    "inline": True
                }
            ],
            "footer": {"text": "Discord Username Monitor v2.0"},
            "timestamp": datetime.now().isoformat()
        }
        
        # Add thumbnail for rare usernames
        if username_len <= 4:
            embed["thumbnail"] = {
                "url": "https://cdn.discordapp.com/emojis/1128604593043546122.webp"
            }
        
        return embed
    
    def _get_webhook_for_username(self, username):
        """Get appropriate webhook URL for username"""
        if 'all' in self.webhooks:
            return self.webhooks['all']
        
        username_len = len(username)
        
        if username_len <= 3 and 'rare' in self.webhooks:
            return self.webhooks['rare']
        elif username_len == 4 and '4char' in self.webhooks:
            return self.webhooks['4char']
        elif 'standard' in self.webhooks:
            return self.webhooks['standard']
        
        # Fallback to first available webhook
        return next(iter(self.webhooks.values())) if self.webhooks else None
    
    def _get_rarity_text(self, length):
        """Get rarity description for username length"""
        if length <= 3:
            return "Ultra Rare"
        elif length == 4:
            return "Rare"
        elif length == 5:
            return "Uncommon"
        else:
            return "Common"
    
    async def send_periodic_stats(self, stats):
        """Send periodic statistics update"""
        if not self.webhooks:
            return
        
        try:
            embed = {
                "title": "📊 Periodic Statistics Update",
                "description": f"Monitoring session statistics",
                "color": 0x3498db,
                "fields": [
                    {"name": "Usernames Checked", "value": str(stats['checked_count']), "inline": True},
                    {"name": "Available Found", "value": str(stats['available_found']), "inline": True},
                    {"name": "Cycles Completed", "value": str(stats['cycles_completed']), "inline": True},
                    {"name": "Current Position", "value": f"{stats['current_position']}/{stats.get('total_usernames', 'N/A')}", "inline": True},
                    {"name": "Rate Limited", "value": str(stats['rate_limited_count']), "inline": True},
                    {"name": "Runtime", "value": self._format_runtime(stats.get('runtime_seconds', 0)), "inline": True}
                ],
                "footer": {"text": "Discord Username Monitor v2.0"},
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {"embeds": [embed]}
            
            # Send to first webhook only for stats
            webhook_url = next(iter(self.webhooks.values()))
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                self.logger.info("Periodic stats sent")
            
        except Exception as e:
            self.logger.error(f"Periodic stats error: {e}")
    
    def _format_runtime(self, seconds):
        """Format runtime in human readable format"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    async def send_shutdown_notification(self, final_stats):
        """Send notification when monitoring stops"""
        if not self.webhooks:
            return
        
        try:
            embed = {
                "title": "🛑 Discord Username Monitor Stopped",
                "description": "Monitoring session has ended",
                "color": 0xe74c3c,
                "fields": [
                    {"name": "Total Checked", "value": str(final_stats['checked_count']), "inline": True},
                    {"name": "Available Found", "value": str(final_stats['available_found']), "inline": True},
                    {"name": "Total Runtime", "value": self._format_runtime(final_stats.get('runtime_seconds', 0)), "inline": True}
                ],
                "footer": {"text": "Discord Username Monitor v2.0"},
                "timestamp": datetime.now().isoformat()
            }
            
            payload = {"embeds": [embed]}
            
            # Send to all webhooks
            for webhook_url in self.webhooks.values():
                requests.post(webhook_url, json=payload, timeout=10)
                
            self.logger.info("Shutdown notifications sent")
            
        except Exception as e:
            self.logger.error(f"Shutdown notification error: {e}")