#!/usr/bin/env python3
import asyncio
import random
import time
import argparse
import logging
from playwright.async_api import async_playwright
from proxy_config import get_proxies
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrafficGenerator:
    def __init__(self, target_url, visits_per_hour=12, proxy_type='free'):
        self.target_url = target_url
        self.visits_per_hour = visits_per_hour
        self.proxy_type = proxy_type
        self.delay_between_visits = 3600 / visits_per_hour  # seconds
        self.proxies = get_proxies(proxy_type)
        self.used_fingerprints = set()
        
        # User agents (70% mobile, 30% desktop)
        self.mobile_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36'
        ]
        
        self.desktop_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15'
        ]

    def get_random_user_agent(self):
        """Get random user agent (70% mobile, 30% desktop)"""
        if random.random() < 0.7:
            return random.choice(self.mobile_agents)
        return random.choice(self.desktop_agents)

    def get_random_proxy(self):
        """Get random proxy from available list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def generate_fingerprint(self, user_agent, proxy):
        """Generate unique fingerprint to avoid repetition"""
        proxy_str = f"{proxy['server']}:{proxy['port']}" if proxy else "no-proxy"
        return f"{user_agent[:50]}_{proxy_str}"

    async def simulate_human_behavior(self, page):
        """Simulate realistic human behavior on the page"""
        try:
            # Wait for page to load
            await asyncio.sleep(random.uniform(2, 5))
            
            # Get page dimensions
            viewport = await page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")
            
            # Scroll down randomly (simulate reading)
            scroll_times = random.randint(2, 6)
            for _ in range(scroll_times):
                scroll_distance = random.randint(200, 800)
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
                await asyncio.sleep(random.uniform(1, 3))
            
            # Scroll back up sometimes
            if random.random() < 0.3:
                await page.evaluate("window.scrollTo(0, 0)")
                await asyncio.sleep(random.uniform(1, 2))
            
            # Click on ads/links 10% of the time
            if random.random() < 0.1:
                try:
                    # Look for common ad/link selectors
                    selectors = [
                        'a[href*="ad"]', 'a[href*="click"]', '.ad', '.advertisement',
                        'a[target="_blank"]', 'button', 'a[href^="http"]'
                    ]
                    
                    for selector in selectors:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            element = random.choice(elements[:3])  # Click on first 3 found
                            try:
                                await element.click(timeout=5000)
                                await asyncio.sleep(random.uniform(1, 3))
                                break
                            except:
                                continue
                except Exception as e:
                    logger.debug(f"Click simulation failed: {e}")
            
            # Stay on page for realistic time (30-180 seconds)
            stay_time = random.uniform(30, 180)
            logger.info(f"Staying on page for {stay_time:.1f} seconds")
            await asyncio.sleep(stay_time)
            
        except Exception as e:
            logger.error(f"Error in human behavior simulation: {e}")

    async def visit_page(self):
        """Visit the target page with random configuration"""
        user_agent = self.get_random_user_agent()
        proxy = self.get_random_proxy()
        
        # Check if this fingerprint was used before
        fingerprint = self.generate_fingerprint(user_agent, proxy)
        if fingerprint in self.used_fingerprints:
            logger.info("Fingerprint already used, generating new configuration")
            return await self.visit_page()  # Recursive call for new config
        
        self.used_fingerprints.add(fingerprint)
        
        async with async_playwright() as p:
            try:
                # Browser options
                browser_options = {
                    'headless': True,
                    'args': [
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                }
                
                # Add proxy if available
                if proxy:
                    browser_options['proxy'] = {
                        'server': f"{proxy['server']}:{proxy['port']}",
                        'username': proxy.get('username'),
                        'password': proxy.get('password')
                    }
                    logger.info(f"Using proxy: {proxy['server']}:{proxy['port']}")
                
                browser = await p.chromium.launch(**browser_options)
                
                # Create context with user agent
                context = await browser.new_context(
                    user_agent=user_agent,
                    viewport={'width': 1366, 'height': 768}
                )
                
                page = await context.new_page()
                
                # Visit the target URL
                logger.info(f"Visiting: {self.target_url} with UA: {user_agent[:50]}...")
                await page.goto(self.target_url, wait_until='networkidle', timeout=30000)
                
                # Simulate human behavior
                await self.simulate_human_behavior(page)
                
                await context.close()
                await browser.close()
                
                logger.info(f"Visit completed successfully")
                
            except Exception as e:
                logger.error(f"Error during page visit: {e}")

    async def run(self):
        """Main loop to generate traffic"""
        logger.info(f"Starting traffic generation for {self.target_url}")
        logger.info(f"Rate: {self.visits_per_hour} visits/hour ({self.delay_between_visits:.1f}s interval)")
        logger.info(f"Proxy type: {self.proxy_type} ({len(self.proxies)} available)")
        
        visit_count = 0
        
        while True:
            try:
                visit_count += 1
                logger.info(f"Starting visit #{visit_count}")
                
                await self.visit_page()
                
                # Wait before next visit
                logger.info(f"Waiting {self.delay_between_visits:.1f} seconds before next visit")
                await asyncio.sleep(self.delay_between_visits)
                
            except KeyboardInterrupt:
                logger.info("Traffic generation stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                # Wait a bit before retrying
                await asyncio.sleep(30)

def main():
    parser = argparse.ArgumentParser(description='Real Traffic Generator')
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--visits-per-hour', type=int, default=12, help='Visits per hour')
    parser.add_argument('--proxy-type', choices=['free', 'premium', 'datacenter'], 
                       default='free', help='Proxy type')
    
    args = parser.parse_args()
    
    generator = TrafficGenerator(
        target_url=args.url,
        visits_per_hour=args.visits_per_hour,
        proxy_type=args.proxy_type
    )
    
    try:
        asyncio.run(generator.run())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
    except Exception as e:
        logger.error(f"Program error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
