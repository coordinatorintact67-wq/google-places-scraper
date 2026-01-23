#!/usr/bin/env python3
"""
Enhanced Google Maps Scraper with improved performance and reliability
"""

import argparse
import asyncio
import csv
import os
import random
import sys
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List
import logging

from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class EnhancedBusiness:
    """Enhanced business data structure with validation"""
    name: str = ""
    address: str = ""
    website: str = ""
    phone: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    rating: float = 0.0
    review_count: int = 0
    category: str = ""
    operating_hours: str = ""
    price_range: str = ""
    image_url: str = ""

    def is_complete(self) -> bool:
        """Check if business has essential data"""
        return bool(self.name and (self.address or self.phone or self.website))

    def normalize_phone(self):
        """Normalize phone number format"""
        if self.phone:
            # Remove non-numeric characters except +
            import re
            self.phone = re.sub(r'[^\d+]', '', self.phone)

    def clean_data(self):
        """Clean and validate all data fields"""
        if self.name:
            self.name = self.name.strip()
        if self.address:
            self.address = self.address.strip()
        if self.website:
            self.website = self.website.strip()
        if self.category:
            self.category = self.category.strip()
        if self.operating_hours:
            self.operating_hours = self.operating_hours.strip()

        self.normalize_phone()


class EnhancedPlaywrightController:
    def __init__(self, headless=True, slow_mo=0):
        self.headless = headless
        self.slow_mo = slow_mo
        self.browser = None
        self.context = None
        self.page = None

    async def setup_browser(self):
        """Initialize browser with anti-detection measures"""
        self.playwright = await async_playwright().start()

        # Use stealth configuration to avoid detection
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--allow-running-insecure-content'
            ]
        )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )

        # Add navigator.webdriver property removal script
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)

        self.page = await self.context.new_page()

    async def safe_goto(self, url, wait_for_selector=None):
        """Navigate to URL with error handling and waiting"""
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)

            if wait_for_selector:
                await self.page.wait_for_selector(wait_for_selector, timeout=10000)

            # Random delay after navigation
            await self.random_delay(1, 3)

        except Exception as e:
            logging.warning(f"Navigation error: {str(e)}")
            # Retry with exponential backoff
            await self.random_delay(3, 6)
            await self.page.goto(url, wait_until="networkidle", timeout=30000)

    async def random_delay(self, min_seconds=1, max_seconds=3):
        """Random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)

    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


class SmartScrapingEngine:
    def __init__(self, controller: EnhancedPlaywrightController):
        self.controller = controller
        self.scraped_businesses = []
        self.failed_urls = []

    async def search_and_extract(self, search_query: str, max_results: int = 20) -> List[EnhancedBusiness]:
        """Perform search and extract business data with smart retry logic"""

        # Navigate to Google Maps
        await self.controller.safe_goto("https://www.google.com/maps", "#searchboxinput")

        # Perform search
        search_box = await self.controller.page.wait_for_selector("#searchboxinput")
        await search_box.fill(search_query)
        await search_box.press("Enter")

        # Wait for results to load
        await self.controller.page.wait_for_selector('div[data-result-index]', timeout=15000)

        businesses = []
        attempts = 0
        max_attempts = max_results * 2  # Allow for some failed attempts

        while len(businesses) < max_results and attempts < max_attempts:
            try:
                # Find all business listings
                business_elements = await self.controller.page.query_selector_all('div[data-result-index]')

                for element in business_elements:
                    if len(businesses) >= max_results:
                        break

                    try:
                        business = await self.extract_business_data(element)
                        if business and business.is_complete():
                            # Check for duplicates before adding
                            if not self.is_duplicate(business, businesses):
                                businesses.append(business)

                        # Scroll to next element to load more content
                        await element.scroll_into_view_if_needed()

                    except Exception as e:
                        logging.warning(f"Failed to extract business data: {str(e)}")
                        continue

                # Scroll down to load more results
                await self.controller.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")

                # Random delay between scrolls
                await self.controller.random_delay(2, 4)

                attempts += 1

            except Exception as e:
                logging.error(f"Search error: {str(e)}")
                await self.controller.random_delay(5, 10)
                break

        return businesses

    async def extract_business_data(self, element) -> Optional[EnhancedBusiness]:
        """Extract business data from a single listing element"""
        business = EnhancedBusiness()

        try:
            # Extract name
            name_element = await element.query_selector('.fontHeadlineSmall, .qBF1Pd, .NrDZN')
            if name_element:
                business.name = await name_element.text_content()

            # Extract other details using multiple selector strategies
            # Address
            address_selectors = ['.Io6YTe, .fontBodyMedium, .rogA2c, .RcCsl']
            for selector in address_selectors:
                addr_elem = await element.query_selector(selector)
                if addr_elem:
                    addr_text = await addr_elem.text_content()
                    if addr_text and len(addr_text) > 5:  # Likely an actual address
                        business.address = addr_text
                        break

            # Rating and review count
            rating_element = await element.query_selector('.MW4etd, .UY7F9')
            if rating_element:
                rating_text = await rating_element.text_content()
                try:
                    business.rating = float(rating_text)
                except ValueError:
                    pass

            review_element = await element.query_selector('.UY7F9, .RfnDt')
            if review_element:
                review_text = await review_element.text_content()
                import re
                review_match = re.search(r'\((\d+)\)', review_text)
                if review_match:
                    business.review_count = int(review_match.group(1))

            # Category
            category_element = await element.query_selector('.DkEaL, .W4Efsd')
            if category_element:
                category_text = await category_element.text_content()
                business.category = category_text

            # Phone and website - need to click into detail page
            # This would require clicking the element and extracting from the detail page
            await self.extract_from_detail_page(element, business)

            business.clean_data()

            return business if business.is_complete() else None

        except Exception as e:
            logging.warning(f"Error extracting business data: {str(e)}")
            return None

    async def extract_from_detail_page(self, element, business: EnhancedBusiness):
        """Extract additional details by navigating to business detail page"""
        try:
            # Click on the business to open details
            await element.click(timeout=5000)

            # Wait for detail panel to load
            await self.controller.page.wait_for_selector('.lIMUZd', timeout=8000)

            # Extract phone number
            phone_selectors = ['[data-tooltip="Copy phone number"]', '.CsEnBe', '[jsaction*="phone"]']
            for selector in phone_selectors:
                phone_elem = await self.controller.page.query_selector(selector)
                if phone_elem:
                    phone_text = await phone_elem.get_attribute('data-tooltip') or await phone_elem.text_content()
                    if phone_text and any(c.isdigit() for c in phone_text):
                        business.phone = phone_text
                        break

            # Extract website
            website_selectors = ['[data-tooltip="Open website"]', '[href^="http"]', '.Io6YTe.fontBodyMedium']
            for selector in website_selectors:
                website_elems = await self.controller.page.query_selector_all(selector)
                for website_elem in website_elems:
                    href = await website_elem.get_attribute('href')
                    if href and ('http' in href and 'google' not in href):
                        business.website = href
                        break
                if business.website:
                    break

            # Extract coordinates from URL if available
            current_url = self.controller.page.url
            import re
            coord_match = re.search(r'@(-?\d+\.?\d*),(-?\d+\.?\d*)', current_url)
            if coord_match:
                business.latitude = float(coord_match.group(1))
                business.longitude = float(coord_match.group(2))

            # Close the detail panel by clicking outside or pressing Escape
            await self.controller.page.keyboard.press('Escape')
            await self.controller.random_delay(1, 2)

        except Exception as e:
            logging.warning(f"Error extracting from detail page: {str(e)}")

    def is_duplicate(self, business: EnhancedBusiness, existing_businesses: List[EnhancedBusiness]) -> bool:
        """Check if business already exists in the list"""
        for existing in existing_businesses:
            # Compare by name and address, or name and phone, or name and website
            if (business.name.lower() == existing.name.lower() and
                ((business.address and existing.address and
                  business.address.lower() == existing.address.lower()) or
                 (business.phone and existing.phone and
                  business.phone == existing.phone) or
                 (business.website and existing.website and
                  business.website == existing.website))):
                return True
        return False


class BatchProcessingManager:
    def __init__(self, max_concurrent=1, delay_range=(2, 5)):
        self.max_concurrent = max_concurrent
        self.delay_range = delay_range
        self.processed_queries = []
        self.failed_queries = []

    async def process_batch(self, search_queries: List[str], max_results_per_query: int = 20) -> dict:
        """Process multiple search queries with concurrency control"""
        results = {}

        for i, query in enumerate(search_queries):
            try:
                print(f"Processing query {i+1}/{len(search_queries)}: {query}")

                # Setup controller for this query
                controller = EnhancedPlaywrightController(headless=True)
                await controller.setup_browser()

                # Create scraping engine
                engine = SmartScrapingEngine(controller)

                # Perform scraping
                businesses = await engine.search_and_extract(query, max_results_per_query)

                results[query] = businesses
                self.processed_queries.append(query)

                print(f"Successfully scraped {len(businesses)} businesses for '{query}'")

                # Delay between queries
                if i < len(search_queries) - 1:  # Don't delay after the last query
                    delay = random.uniform(*self.delay_range)
                    print(f"Waiting {delay:.1f}s before next query...")
                    await asyncio.sleep(delay)

                # Close browser for this query
                await controller.close()

            except Exception as e:
                logging.error(f"Failed to process query '{query}': {str(e)}")
                self.failed_queries.append((query, str(e)))
                results[query] = []

        return results


class DataExportUtils:
    @staticmethod
    def export_to_csv(businesses: List[EnhancedBusiness], filename: str, directory: str = None):
        """Export business data to CSV file"""
        if not directory:
            directory = f"GMaps Data/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            os.makedirs(directory, exist_ok=True)

        filepath = os.path.join(directory, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'name', 'address', 'website', 'phone', 'latitude', 'longitude',
                'rating', 'review_count', 'category', 'operating_hours', 'price_range', 'image_url'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for business in businesses:
                writer.writerow({
                    'name': business.name,
                    'address': business.address,
                    'website': business.website,
                    'phone': business.phone,
                    'latitude': business.latitude,
                    'longitude': business.longitude,
                    'rating': business.rating,
                    'review_count': business.review_count,
                    'category': business.category,
                    'operating_hours': business.operating_hours,
                    'price_range': business.price_range,
                    'image_url': business.image_url
                })

        return filepath

    @staticmethod
    def validate_data_quality(businesses: List[EnhancedBusiness]) -> dict:
        """Analyze data quality and provide statistics"""
        total = len(businesses)
        complete = sum(1 for b in businesses if b.is_complete())
        with_phone = sum(1 for b in businesses if b.phone)
        with_website = sum(1 for b in businesses if b.website)
        with_address = sum(1 for b in businesses if b.address)

        return {
            'total_businesses': total,
            'complete_records': complete,
            'records_with_phone': with_phone,
            'records_with_website': with_website,
            'records_with_address': with_address,
            'completeness_percentage': (complete / total * 100) if total > 0 else 0
        }


async def main():
    parser = argparse.ArgumentParser(description='Enhanced Google Maps Business Scraper')
    parser.add_argument('-s', '--search', type=str, help='Search query (e.g., "coffee shops in Seattle")')
    parser.add_argument('-t', '--total', type=int, default=20, help='Total number of results to scrape')
    parser.add_argument('--headless', type=bool, default=True, help='Run browser in headless mode')
    parser.add_argument('--delay_min', type=float, default=2, help='Minimum delay between requests')
    parser.add_argument('--delay_max', type=float, default=5, help='Maximum delay between requests')

    args = parser.parse_args()

    # Create output directory
    output_dir = f"GMaps Data/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(output_dir, exist_ok=True)

    # Determine search queries
    search_queries = []

    if args.search:
        # Single search
        search_queries = [args.search]
    else:
        # Batch search from input.txt
        if os.path.exists('input.txt'):
            with open('input.txt', 'r', encoding='utf-8') as f:
                search_queries = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        else:
            print("No search query provided and input.txt not found.")
            print("Usage:")
            print("  Single search: python enhanced_scraper.py -s='coffee shops in Seattle' -t=50")
            print("  Batch search: python enhanced_scraper.py -t=30 (reads from input.txt)")
            return

    print(f"Starting to process {len(search_queries)} search queries...")

    # Process queries
    manager = BatchProcessingManager(delay_range=(args.delay_min, args.delay_max))
    all_results = await manager.process_batch(search_queries, args.total)

    # Export results
    total_businesses = 0
    for query, businesses in all_results.items():
        if businesses:
            # Clean query for filename
            clean_query = "".join(c if c.isalnum() else "_" for c in query[:50])
            filename = f"{clean_query}.csv"

            filepath = DataExportUtils.export_to_csv(businesses, filename, output_dir)
            quality_report = DataExportUtils.validate_data_quality(businesses)

            print(f"Exported {len(businesses)} businesses for '{query}' to {filepath}")
            print(f"Quality report for '{query}': {quality_report}")

            total_businesses += len(businesses)

    print(f"\nScraping completed! Total businesses scraped: {total_businesses}")
    print(f"Results saved in: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())