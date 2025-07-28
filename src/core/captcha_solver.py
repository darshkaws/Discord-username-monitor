"""
Discord Username Monitor - CAPTCHA Solver
Handles hCaptcha solving using external services
"""

import requests
import time
import asyncio
from utils.logger import get_logger


class CaptchaSolver:
    """Handles CAPTCHA solving"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Load from config
        self.service_url = config.get('captcha', {}).get('service_url', 'https://freecaptchabypass.com')
        self.client_key = config.get('captcha', {}).get('client_key', '')
        self.timeout = config.get('captcha', {}).get('timeout', 120)
        self.enabled = config.get('captcha', {}).get('enabled', False)
    
    async def solve_hcaptcha(self, sitekey, rqdata=None):
        """Solve hCaptcha using external service"""
        if not self.enabled or not self.client_key:
            self.logger.warning("CAPTCHA solver not configured")
            return None
            
        task_id = None
        try:
            # Create captcha task
            task_payload = {
                "clientKey": self.client_key,
                "task": {
                    "type": "HCaptchaEnterpriseTask",
                    "websiteURL": "https://discord.com",
                    "websitePublicKey": sitekey,
                    "data": rqdata
                }
            }
            
            response = requests.post(
                f"{self.service_url}/createTask",
                json=task_payload,
                timeout=10
            )
            self.logger.debug(f"createTask status={response.status_code}, body={response.text}")
            
            if response.status_code == 200:
                task_data = response.json()
                if task_data.get("errorId") == 0:
                    task_id = task_data["taskId"]
            
            if not task_id:
                return None

            # Poll for solution
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                await asyncio.sleep(5)
                
                result_payload = {"clientKey": self.client_key, "taskId": task_id}
                result_response = requests.post(
                    f"{self.service_url}/getTaskResult",
                    json=result_payload,
                    timeout=10
                )
                self.logger.debug(f"getTaskResult status={result_response.status_code}, body={result_response.text}")
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    if result_data.get("status") == "ready":
                        return result_data["solution"]["gRecaptchaResponse"]
        
        except Exception as e:
            self.logger.error(f"CAPTCHA solving failed: {str(e)}")
        return None