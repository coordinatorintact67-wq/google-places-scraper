# import datetime
# from playwright.sync_api import sync_playwright
# from dataclasses import dataclass, asdict, field
# import argparse
# import os
# import csv
# import time
# from random import randint

# @dataclass
# class Business:
#     """holds business data"""
#     name: str = None
#     address: str = None
#     website: str = None
#     phone_number: str = None
#     rating: str = None
#     reviews: str = None
#     category: str = None
#     location: str = None
#     url: str = None
#     business_hours: str = None
#     timestamp: str = None

#     def __hash__(self):
#         """Make Business hashable for duplicate detection"""
#         name_normalized = (self.name or "").strip().lower()
#         url_normalized = (self.url or "").strip().lower()
#         return hash((name_normalized, url_normalized))

# @dataclass
# class BusinessList:
#     """holds list of Business objects and saves to CSV"""
#     business_list: list[Business] = field(default_factory=list)
#     _seen_businesses: set = field(default_factory=set, init=False)
#     today = datetime.datetime.now().strftime("%Y-%m-%d")
#     save_at = os.path.join('GSearch Data', today)
#     os.makedirs(save_at, exist_ok=True)

#     def add_business(self, business: Business):
#         """Add a business to the list if it's not a duplicate"""
#         business_hash = hash(business)
#         if business_hash not in self._seen_businesses:
#             self.business_list.append(business)
#             self._seen_businesses.add(business_hash)
#             return True
#         return False

#     def initialize_csv_stream(self, filename: str):
#         """Initialize CSV file with headers for streaming"""
#         filepath = os.path.join(self.save_at, f"{filename}.csv")

#         counter = 1
#         while os.path.exists(filepath):
#             filepath = os.path.join(self.save_at, f"{filename}{counter}.csv")
#             counter += 1

#         self._csv_filepath = filepath

#         with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
#             fieldnames = ['name', 'address', 'website', 'phone_number', 'rating', 'reviews', 'category', 'location', 'url', 'business_hours', 'timestamp']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writeheader()

#         return filepath

#     def write_business_to_csv(self, business):
#         """Write a single business to CSV file"""
#         business_dict = asdict(business)
#         # Sanitize any problematic characters in the data before writing
#         sanitized_dict = {}
#         for key, value in business_dict.items():
#             if isinstance(value, str):
#                 # Replace problematic characters with safe alternatives
#                 sanitized_dict[key] = value.encode('utf-8', errors='replace').decode('utf-8')
#             else:
#                 sanitized_dict[key] = value

#         with open(self._csv_filepath, 'a', newline='', encoding='utf-8-sig') as csvfile:
#             fieldnames = ['name', 'address', 'website', 'phone_number', 'rating', 'reviews', 'category', 'location', 'url', 'business_hours', 'timestamp']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerow(sanitized_dict)

# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-s", "--search", type=str, help="Search query (e.g., 'coffee shop')")
#     parser.add_argument("-t", "--total", type=int, help="Maximum number of results to scrape")
#     parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (default: False)")
#     args = parser.parse_args()

#     search_list = []
#     total = args.total if args.total else 1_000_000

#     if args.search:
#         search_list = [args.search]
#     else:
#         input_file_path = os.path.join(os.getcwd(), 'input.txt')
#         if os.path.exists(input_file_path):
#             with open(input_file_path, 'r') as file:
#                 search_list = [line.strip() for line in file.readlines() if line.strip()]

#     if len(search_list) == 0:
#         print('WARNING: No search queries found!')
#         print('Please either:')
#         print('  1. Add queries to input.txt (one per line)')
#         print('  2. Run with: python google_places_scraper.py -s "coffee shop"')
#         print('  3. Run with: python google_places_scraper.py --headless (for headless mode)')
#         return

#     browser = None
#     page = None

#     try:
#         print(f"Starting scraper with {len(search_list)} search queries...")

#         with sync_playwright() as p:
#             # Define user agents to rotate and launch browser with anti-detection measures
#             user_agents = [
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#                 "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
#             ]

#             # Randomly select a user agent
#             import random
#             selected_user_agent = random.choice(user_agents)

#             browser = p.chromium.launch(
#                 headless=args.headless,  # Use headless mode based on argument
#                 args=[
#                     '--disable-blink-features=AutomationControlled',
#                     '--disable-dev-shm-usage',
#                     '--no-sandbox',
#                     '--disable-setuid-sandbox',
#                     f'--user-agent={selected_user_agent}'
#                 ]
#             )
#             page = browser.new_page()

#             for search_for_index, search_for in enumerate(search_list):
#                 search_for = search_for.strip()
#                 print(f"\n{'='*60}")
#                 print(f"Query {search_for_index + 1}/{len(search_list)}: {search_for}")
#                 print(f"{'='*60}")

#                 # Add a random delay before each search to avoid being blocked
#                 delay = randint(2, 5)
#                 print(f"Waiting {delay} seconds before next search...")
#                 time.sleep(delay)

#                 # Navigate to Google Local Search (udm=1) - proper format for local results
#                 search_query = search_for.replace(' ', '+')
#                 search_url = f"https://www.google.com/search?q={search_query}&udm=1"  # udm=1 for local results
#                 print(f"Navigating to: {search_url}")

#                 page.goto(search_url, timeout=30000)
#                 page.wait_for_timeout(5000)  # Increased wait time to ensure page loads

#                 # Wait for listings to load with multiple possible selectors for Google search results
#                 listing_containers = []

#                 # Try multiple selectors that are commonly used for local results
#                 selectors_to_try = [
#                     'a.rllt__link',
#                     '[data-sokoban-container] a',
#                     '.rlfl__tls a',
#                     '[jsaction*="mouseenter"] a',
#                     '.dURPMd a'
#                 ]

#                 for selector in selectors_to_try:
#                     try:
#                         print(f"Trying selector: {selector}")
#                         page.wait_for_selector(selector, timeout=5000)
#                         listing_containers = page.locator(selector).all()
#                         print(f"Selector {selector} found {len(listing_containers)} elements")
#                         if len(listing_containers) > 0:
#                             print(f"Found {len(listing_containers)} listings using selector: {selector}")
#                             break
#                     except Exception as e:
#                         print(f"Selector {selector} failed: {str(e)[:100]}")
#                         continue

#                 if len(listing_containers) == 0:
#                     print("No listings found on page after trying all selectors")
#                     # Let's also check what's on the page
#                     print(f"Page title: {page.title()}")
#                     print("Taking screenshot for debugging...")
#                     screenshot_path = f"debug_{search_for.replace(' ', '_')}_error.png"
#                     page.screenshot(path=screenshot_path)
#                     print(f"Screenshot saved as {screenshot_path}")
#                     continue

#                 # Skip scrolling to load more results - just use initial results
#                 print("Using initial results without scrolling...")

#                 # Find all business listing containers
#                 print("Finding business listings...")

#                 if total and len(listing_containers) > total:
#                     listing_containers = listing_containers[:total]
#                     print(f"Limited to {total} listings")

#                 business_list = BusinessList()
#                 csv_filename = search_for.replace(' ', '_').replace('/', '_').replace('\\', '_')
#                 csv_path = business_list.initialize_csv_stream(csv_filename)
#                 print(f"CSV file: {csv_path}\n")

#                 processed_names = set()
#                 saved_count = 0

#                 # First pass: Collect basic information for all listings
#                 basic_businesses = []
#                 for idx, listing_container in enumerate(listing_containers):
#                     try:
#                         business = Business()

#                         # Get the anchor tag for URL
#                         try:
#                             # Try to get href from the listing container
#                             href = listing_container.get_attribute('href')
#                             if href and href.strip():
#                                 business.url = href if href.startswith('http') else f"https://www.google.com{href}"
#                                 # Sanitize URL to remove any newlines
#                                 business.url = business.url.replace('\n', '').replace('\r', '').strip()
#                             else:
#                                 business.url = ""
#                         except:
#                             business.url = ""

#                         # Get business name from the link
#                         # From our test, we know .OSrXXb and .dbg0pd contain business names
#                         try:
#                             # Primary selector based on our test (OSrXXb found 46 elements)
#                             name_elem = listing_container.locator('div.OSrXXb').first
#                             business.name = name_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                         except:
#                             try:
#                                 # Alternative: .dbg0pd selector (found 22 elements)
#                                 name_elem = listing_container.locator('.dbg0pd').first
#                                 business.name = name_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                             except:
#                                 try:
#                                     # Fallback to any heading span
#                                     name_elem = listing_container.locator('span[role="heading"]').first
#                                     business.name = name_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                                 except:
#                                     business.name = "Unknown Business"

#                         if not business.name or business.name == "Unknown Business":
#                             continue

#                         if business.name.lower() in processed_names:
#                             continue

#                         # Get address from the listing container
#                         try:
#                             # Look for address text within the container, avoiding the name
#                             # Address is often in a div element that's not the name
#                             all_divs = listing_container.locator('div').all()
#                             for div in all_divs:
#                                 text = div.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                                 # Look for text that appears to be an address (contains letters/numbers but not just the business name)
#                                 if text and len(text) > 5 and text != business.name and not text.startswith(business.name) and len(text.split()) >= 2:
#                                     # Check if it looks like an address (contains numbers, commas, common street words)
#                                     if any(char.isdigit() for char in text) or ',' in text or ' st' in text.lower() or ' ave' in text.lower() or ' rd' in text.lower() or ' ln' in text.lower() or ' dr' in text.lower():
#                                         business.address = text
#                                         break
#                         except:
#                             business.address = ""

#                         # Get rating and reviews
#                         try:
#                             # From our test, we know these selectors exist
#                             # Rating is in span with specific class
#                             rating_elem = listing_container.locator('span.yi40Hd').first
#                             business.rating = rating_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                         except:
#                             try:
#                                 # Alternative rating selector
#                                 rating_elem = listing_container.locator('.yi40Hd').first
#                                 business.rating = rating_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                             except:
#                                 business.rating = ""

#                         try:
#                             # Reviews count
#                             reviews_elem = listing_container.locator('span.RDApEe').first
#                             business.reviews = reviews_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                         except:
#                             try:
#                                 # Alternative reviews selector
#                                 reviews_elem = listing_container.locator('.RDApEe').first
#                                 business.reviews = reviews_elem.inner_text().strip().replace('\n', ' ').replace('\r', ' ')
#                             except:
#                                 business.reviews = ""

#                         # Set category and location from search query
#                         business.category = search_for.split(' in ')[0].strip() if ' in ' in search_for else search_for
#                         business.location = search_for.split(' in ')[-1].strip() if ' in ' in search_for else ""

#                         # Set timestamp
#                         business.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#                         # Add to list for second pass - store the URL separately to avoid detached element issues
#                         business_url_stored = business.url  # Store URL separately to avoid detached element issues later
#                         basic_businesses.append((idx, business, business_url_stored))

#                         print(f"  [Basic Info {idx+1}/{len(listing_containers)}] - {business.name[:40]}")

#                     except Exception as e:
#                         print(f"  [Error at {idx+1} basic]: {str(e)[:100]}")
#                         continue

#                 # Second pass: Get detailed information for each business using a single reusable page
#                 # With time-bound operations and streaming writes
#                 temp_page = None
#                 try:
#                     for idx, business, business_url_stored in basic_businesses:
#                         try:
#                             # Use the stored URL instead of accessing the potentially detached element
#                             business_url = business_url_stored

#                             if business_url and business_url.strip():
#                                 # Add a short random delay before navigating to the business page
#                                 page_delay = randint(1, 3)
#                                 time.sleep(page_delay)

#                                 # Reuse a single temporary page for multiple businesses
#                                 if temp_page is None:
#                                     temp_page = browser.new_page()

#                                 # Navigate to the business page with timeout
#                                 try:
#                                     # Set navigation timeout to 8 seconds to prevent hanging
#                                     temp_page.set_default_timeout(8000)
#                                     temp_page.goto(business_url, timeout=8000)
#                                     temp_page.wait_for_timeout(1500)  # Reduced wait time

#                                     # Extract phone number from the detailed page with timeout
#                                     try:
#                                         # Wait for phone element with timeout, but don't fail if not found
#                                         phone_locator = temp_page.locator('button[data-tooltip*="Phone"], [data-tooltip*="Copy phone number"], [aria-label*="Phone"], button[jsaction*="copy"]')
#                                         # Just try to get the element if it exists, don't wait too long
#                                         if phone_locator.count() > 0:
#                                             phone_element = phone_locator.first
#                                             try:
#                                                 # Set a shorter timeout for getting text
#                                                 phone_text = phone_element.inner_text(timeout=3000).strip().replace('\n', ' ').replace('\r', ' ')
#                                                 if not phone_text:
#                                                     phone_text = phone_element.get_attribute('aria-label', timeout=3000) or phone_element.get_attribute('data-tooltip', timeout=3000) or ""
#                                                 business.phone_number = phone_text
#                                             except:
#                                                 business.phone_number = ""
#                                         else:
#                                             business.phone_number = ""
#                                     except Exception:
#                                         business.phone_number = ""

#                                     # Extract website from the detailed page with timeout
#                                     try:
#                                         website_locator = temp_page.locator('a[data-tooltip="Open website"], [aria-label*="Website"] a, a[href*="http"]:not([href*="google.com"])')
#                                         if website_locator.count() > 0:
#                                             website_element = website_locator.first
#                                             try:
#                                                 website_href = website_element.get_attribute('href', timeout=3000)
#                                                 business.website = website_href.strip().replace('\n', ' ').replace('\r', ' ') if website_href else ""
#                                             except:
#                                                 business.website = ""
#                                         else:
#                                             business.website = ""
#                                     except Exception:
#                                         business.website = ""

#                                     # Extract business hours from the detailed page with timeout
#                                     try:
#                                         hours_locator = temp_page.locator('div[role="text"] span:has-text("Closed"), div[role="text"]:has-text("Open"), div[role="text"]:has-text("Closes"), div[role="text"]:has-text("Opens")')
#                                         if hours_locator.count() > 0:
#                                             try:
#                                                 hours_element = hours_locator.first
#                                                 business.business_hours = hours_element.inner_text(timeout=3000).strip().replace('\n', ' ').replace('\r', ' ')
#                                             except:
#                                                 business.business_hours = ""
#                                         else:
#                                             business.business_hours = ""
#                                     except Exception:
#                                         business.business_hours = ""

#                                 except Exception as page_error:
#                                     print(f"  [Page navigation error at {idx+1}]: {str(page_error)[:100]}")
#                                     # Continue without detailed info

#                             # Reset timeout to default after navigation (only if temp_page exists)
#                             if temp_page:
#                                 try:
#                                     temp_page.set_default_timeout(30000)
#                                 except:
#                                     pass  # Ignore if page is already closed

#                             # Add to business list and save to CSV immediately (streaming write)
#                             if business_list.add_business(business):
#                                 business_list.write_business_to_csv(business)
#                                 saved_count += 1
#                                 status = f"  [Saved {saved_count}/{len(basic_businesses)}] - {business.name[:40]}"
#                                 if business.rating:
#                                     status += f" - {business.rating} stars"
#                                 print(status)
#                                 processed_names.add(business.name.lower())

#                         except Exception as e:
#                             print(f"  [Error at {idx+1} detailed]: {str(e)[:100]}")
#                             # Even if detailed info fails, save the basic info with streaming write
#                             if business_list.add_business(business):
#                                 business_list.write_business_to_csv(business)
#                                 saved_count += 1
#                             continue

#                 finally:
#                     # Close the temporary page safely at the end
#                     if temp_page:
#                         try:
#                             temp_page.close()
#                         except:
#                             pass  # Page might already be closed

#                 print(f"\n{'='*60}")
#                 print(f"Completed: {search_for}")
#                 print(f"  Total saved: {saved_count} businesses")
#                 print(f"{'='*60}")

#     except Exception as e:
#         print(f"\nError: {e}")
#         import traceback
#         traceback.print_exc()

#     finally:
#         if page:
#             try:
#                 page.close()
#             except:
#                 pass
#         if browser:
#             try:
#                 browser.close()
#                 print("\nBrowser closed")
#             except:
#                 pass

#     print("\n" + "="*60)
#     print("SCRAPING COMPLETED!")
#     print(f"Results saved in: {BusinessList.save_at}")
#     print("="*60)

# if __name__ == "__main__":
#     main()