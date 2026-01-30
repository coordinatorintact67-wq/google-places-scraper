import time
import csv
import re
import os
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def extract_detail_panel(driver, listing_data=None):
    """Extract data from the right side detail panel after clicking"""
    business_data = listing_data.copy() if listing_data else {}
    if 'name' not in business_data: business_data['name'] = "N/A"

    try:
        # Define selectors
        name_selectors = [
            'h2.qrShPb',
            'h1.DUwDvf',
            'div.SPZz6b h2',
            'div.SPZz6b h1',
            'div.x0H67.r9fE8',
            'div.v93No.H7V2N.fEByN',
            '[role="heading"]',
            '.rG09U',
            '.H07f0c',
            'div.PZPZ1c h2',
            'div.PZPZ1c h1'
        ]

        # Wait for any name selector to appear
        wait = WebDriverWait(driver, 7) # Shorter wait if we already have listing_data
        nameFound = business_data.get('name') != "N/A"
        
        if not nameFound:
            for selector in name_selectors:
                try:
                    name_elem = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                    name = name_elem.text.strip()
                    if name:
                        business_data['name'] = name
                        nameFound = True
                        break
                except:
                    continue

        if not nameFound:
            # Fallback: check all headings immediately
            try:
                headings = driver.find_elements(By.CSS_SELECTOR, 'h1, h2, [role="heading"]')
                for h in headings:
                    if h.is_displayed():
                        t = h.text.strip()
                        if t and len(t) > 2:
                            business_data['name'] = t
                            nameFound = True
                            break
            except:
                pass
            
        if not nameFound:
            business_data['name'] = "N/A"
            print("   DEBUG: Name not found in panel")

        # Rating
        rating_selectors = [
            'span.ceNzKf[aria-hidden="true"]',
            'div.F7nice span[aria-hidden="true"]',
            'span.Aq14fc',
            'span.gsrt.By079',
            'div.PZPZ1c span[aria-hidden="true"]'
        ]

        for selector in rating_selectors:
            try:
                rating_elem = driver.find_element(By.CSS_SELECTOR, selector)
                rating = rating_elem.text.strip()
                if rating and (rating.replace('.', '').replace(',', '').isdigit()):
                    business_data['rating'] = rating
                    break
            except:
                continue

        if 'rating' not in business_data:
            business_data['rating'] = "N/A"

        # Total Reviews
        review_selectors = [
            'span.RDApEe.YrbPuc',
            'span.RDApEe',
            'span.F7nice span:nth-child(2)',
            'div.F7nice span[aria-label*="reviews"]',
            'span.z3vRcc'
        ]

        for selector in review_selectors:
            try:
                reviews_elem = driver.find_element(By.CSS_SELECTOR, selector)
                reviews_text = reviews_elem.text.strip()
                # Extract number using regex as it could be "1.2K reviews" or "(45)"
                match = re.search(r'([\d\.,]+[Kk]?)', reviews_text)
                if match:
                    business_data['total_reviews'] = match.group(1).replace('(', '').replace(')', '').strip()
                    break
            except:
                continue

        if 'total_reviews' not in business_data:
            business_data['total_reviews'] = "N/A"

        # Category/Type
        category_selectors = [
            'button.DkEaL',
            'span.YhemCb',
            'div.LBgpqf button',
            'div.PZPZ1c span:nth-of-type(1)'
        ]

        for selector in category_selectors:
            try:
                category = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if category and len(category) < 50:
                    business_data['category'] = category
                    break
            except:
                continue

        if 'category' not in business_data:
            business_data['category'] = "N/A"

        # Address
        address_selectors = [
            'span.LrzXr',
            'button[data-item-id="address"]',
            'button[data-tooltip*="Address"]',
            'div.rogA2c[data-item-id="address"]',
            'div[data-item-id="address"]',
            'span.fMghS'
        ]

        for selector in address_selectors:
            try:
                addr_elem = driver.find_element(By.CSS_SELECTOR, selector)
                address = addr_elem.get_attribute('aria-label')
                if not address:
                    address = addr_elem.text.strip()

                if address:
                    address = address.replace('Address: ', '').replace('Copy address', '').strip()
                    if address:
                        business_data['address'] = address
                        break
            except:
                continue

        if 'address' not in business_data:
            business_data['address'] = "N/A"

        # Phone Number
        phone_selectors = [
            'button[data-item-id*="phone"]',
            'button[aria-label*="Phone"]',
            'a[data-item-id*="phone"]',
            'a[data-dtype="d3ph"]',
            'span.LrzXr.zdqRlf.kno-fv a',
            'span.w8qArf.FoJoyf a.fl',
            'span.LrzXr',
            'span[data-dtype="d3ph"]'
        ]

        for selector in phone_selectors:
            try:
                phone_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for phone_elem in phone_elements:
                    phone = phone_elem.get_attribute('aria-label')
                    if not phone:
                        phone = phone_elem.text.strip()

                    if phone:
                        phone = phone.replace('Phone: ', '').replace('Copy phone number', '').strip()
                        phone = phone.replace('Call', '').replace('phone number', '').strip()

                        if phone and ('+' in phone or sum(c.isdigit() for c in phone) >= 7):
                            phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,})', phone)
                            if phone_match:
                                business_data['phone'] = phone_match.group(1).strip()
                            else:
                                business_data['phone'] = phone
                            break

                if 'phone' in business_data:
                    break
            except:
                continue

        if 'phone' not in business_data:
            business_data['phone'] = "N/A"

        # Website
        website_selectors = [
            'a.n1obkb.mI8Pwc',
            'a[data-item-id="authority"]',
            'a[aria-label*="Website"]',
            'button[data-item-id="authority"]',
            'a.ab_button[href*="http"]'
        ]

        for selector in website_selectors:
            try:
                website_elem = driver.find_element(By.CSS_SELECTOR, selector)
                website = website_elem.get_attribute('href')
                if not website:
                    website = website_elem.text.strip()

                if website and 'http' in website and 'google' not in website.lower():
                    business_data['website'] = website
                    break
            except:
                continue

        if 'website' not in business_data:
            business_data['website'] = "N/A"

        # Price Range
        price_selectors = [
            'span[aria-label*="Price"]',
            'span.mgr77e',
            'span.YhemCb'
        ]

        for selector in price_selectors:
            try:
                price = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if price and '$' in price:
                    business_data['price_range'] = price
                    break
            except:
                continue

        if 'price_range' not in business_data:
            business_data['price_range'] = "N/A"

        # Hours Status
        hours_selectors = [
            'div.OqCZI',
            'span[aria-label*="Hours"]',
            'div.MkXq9e',
            'div.J77u9c'
        ]

        for selector in hours_selectors:
            try:
                hours = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if hours:
                    business_data['hours_status'] = hours
                    break
            except:
                continue

        if 'hours_status' not in business_data:
            business_data['hours_status'] = "N/A"

        business_data['google_maps_url'] = driver.current_url

        return business_data

    except Exception as e:
        print(f"[ERROR] Error extracting detail panel: {e}")
        return None


def scrape_current_page(driver, all_businesses, csv_filepath, fieldnames, termination_flag=None):
    """Scrape listings from the current search results page"""
    wait = WebDriverWait(driver, 15)

    # Check termination before starting
    if termination_flag and termination_flag():
        return all_businesses

    # Handle consent if appears
    try:
        # Check termination before handling consent
        if termination_flag and termination_flag():
            return all_businesses
        consent = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")
        consent.click()
        time.sleep(2)
    except:
        pass

    # Find clickable listings (Order matched to test.py)
    clickable_selectors = [
        'a.vwVdIc',
        'div.VkpGBb a',
        'a[jsname]',
        'div[role="article"] a',
        'div.g a',
        'a.sVXRqc',
        'a[data-cid]',
        'div.tF2Cxc a',
    ]

    listings = []
    successful_selector = None

    for selector in clickable_selectors:
        # Check termination before trying each selector
        if termination_flag and termination_flag():
            return all_businesses
        try:
            listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            if len(listings) > 0:
                successful_selector = selector
                print(f"Found {len(listings)} listings using: {selector}")
                break
        except:
            continue

    if not listings:
        print("[WARNING] DEBUG: No clickable listings found on this page")
        return all_businesses
    else:
        print(f"DEBUG: Found {len(listings)} listings using {successful_selector}")

    total_to_scrape = len(listings)
    print(f"Will scrape ALL {total_to_scrape} listings from current page")

    for i in range(total_to_scrape):
        # Check termination at the beginning of each listing iteration
        if termination_flag and termination_flag():
            print(f"[TERMINATION] Terminating during scraping of listing {i+1}")
            return all_businesses

        try:
            print(f"\n[{len(all_businesses)+1}] Processing listing {i+1}...")

            # Re-find listings to avoid stale elements
            current_listings = driver.find_elements(By.CSS_SELECTOR, successful_selector)
            if i >= len(current_listings):
                print(f"[WARNING] Ran out of listings at index {i}")
                break

            listing = current_listings[i]

            # CLICK AND EXTRACT
            # 1. Capture basic info from listing first (fallback)
            listing_data = {'name': 'N/A', 'address': 'N/A', 'rating': 'N/A', 'total_reviews': 'N/A'}
            try:
                # Try to find name/address in the result card before clicking
                card_text = listing.text
                if card_text:
                    lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                    if lines:
                        listing_data['name'] = lines[0] # Often the first line is the name
            except:
                pass

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listing)
            time.sleep(randint(1, 2))

            # Check termination before clicking
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Terminating before clicking listing {i+1}")
                return all_businesses

            # Click
            try:
                # Try clicking the parent or the link
                listing.click()
            except:
                try:
                    driver.execute_script("arguments[0].click();", listing)
                except:
                    pass

            # Wait for content or panel to load
            # Use shorter wait times and check termination periodically
            wait_time = 3
            for _ in range(wait_time):
                if termination_flag and termination_flag():
                    print(f"[TERMINATION] Terminating during wait for panel load")
                    return all_businesses
                time.sleep(1)

            # Extract detailed data
            business_data = extract_detail_panel(driver, listing_data)

            if business_data and business_data.get('name') != "N/A":
                all_businesses.append(business_data)

                # Save to CSV immediately and flush to disk
                with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(business_data)
                    csvfile.flush()

                print(f"[INFO] Scraped: {business_data['name']}")
                print("-" * 40)
            else:
                print("[WARNING] Could not extract data for this item")

            # Check termination before going back
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Terminating before going back from listing {i+1}")
                return all_businesses

            # Go back
            driver.back()

            # Check termination after going back
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Terminating after going back from listing {i+1}")
                return all_businesses

            time.sleep(randint(2, 4))

        except Exception as e:
            print(f"[ERROR] Error on listing {i+1}: {e}")
            try:
                # Check termination before going back on error
                if termination_flag and termination_flag():
                    print(f"[TERMINATION] Terminating during error recovery for listing {i+1}")
                    return all_businesses
                driver.back()
                time.sleep(2)
            except:
                pass
            continue

    return all_businesses


def click_next_page_with_termination(driver, termination_flag):
    """Click next page button with termination check - IMPROVED VERSION from test.py"""

    # Check termination before starting
    if termination_flag and termination_flag():
        return False

    # Scroll to bottom first
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # Check termination after scrolling
    if termination_flag and termination_flag():
        return False

    # Try multiple next button selectors
    next_selectors = [
        'a#pnnext',  # Standard Google next button
        'a[aria-label*="Next"]',
        'a[aria-label*="next"]',
        'td.b a',  # Pagination table cell
        'span.SJajHc.NVbCr a',  # Google pagination
        'a.nBDE1b.G5eFlf',  # Another pagination selector
        '#pnnext',
        'span[style*="background:url"] a',  # Next arrow image
        'table#nav td:last-child a',  # Last pagination cell
    ]

    for selector in next_selectors:
        # Check termination before trying each selector
        if termination_flag and termination_flag():
            return False

        try:
            print(f"🔍 Trying selector: {selector}")

            # Wait for element with shorter timeout
            wait = WebDriverWait(driver, 5)
            next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

            # Check termination after finding element
            if termination_flag and termination_flag():
                return False

            # Check if button is enabled (not greyed out)
            aria_label = next_button.get_attribute('aria-label')
            if aria_label and 'next' in aria_label.lower():
                print(f"✓ Found next button: {aria_label}")

            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)

            # Check termination after scrolling to button
            if termination_flag and termination_flag():
                return False

            time.sleep(1)

            # Try clicking
            try:
                next_button.click()
            except:
                driver.execute_script("arguments[0].click();", next_button)

            print("✅ Next button clicked successfully!")
            time.sleep(randint(4, 6))  # Wait for page load

            # Check termination after clicking
            if termination_flag and termination_flag():
                return False

            return True

        except Exception as e:
            continue

    print("❌ Could not find next button")
    return False


def scrape_google_search(search_query, location="", csv_filepath="", fieldnames=None, termination_flag=None, job_id=None, thread_drivers=None):
    """Main scraping with UNLIMITED pagination - Scrapes ALL available results from test.py"""

    import urllib.parse
    driver = None
    try:
        # Check termination flag before starting
        if termination_flag and termination_flag():
            print(f"[TERMINATION] Job terminated before starting for query: {search_query}")
            return []

        # Chrome Options from test.py
        option = webdriver.ChromeOptions()
        # option.add_argument("--headless")
        option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        option.add_argument("--disable-blink-features=AutomationControlled")
        option.add_experimental_option("useAutomationExtension", False)
        option.add_argument('--disable-infobars')
        option.add_experimental_option("excludeSwitches", ["enable-automation"])
        option.add_argument("--start-maximized")
        option.add_argument("--disable-search-engine-choice-screen")
        option.add_argument("--disable-dev-shm-usage")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-gpu")
        option.add_argument("--disable-features=IsolateOrigins,site-per-process")
        # Suppress Errors and Noise
        option.add_argument("--log-level=3")
        option.add_argument("--silent")
        option.add_argument("--disable-logging")
        option.add_argument("--disable-background-networking")
        option.add_argument("--disable-sync")
        option.add_argument("--no-first-run")
        option.add_argument("--ignore-certificate-errors")
        option.add_argument("--ignore-ssl-errors")
        option.add_argument("--allow-running-insecure-content")

        print(f"DEBUG: Starting Chrome...")
        try:
            driver = webdriver.Chrome(options=option)
            driver.set_page_load_timeout(10)  # Reduced timeout to allow faster interruption
            # Hide automation flag from test.py
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            print(f"DEBUG: Browser opened successfully")

            # Register the driver with the job_id if provided
            if job_id and thread_drivers is not None:
                thread_drivers[job_id] = driver
        except Exception as e:
            print(f"[CRITICAL] Failed to initialize Chrome: {e}")
            return []

        if location:
            query = f"{search_query} in {location}"
        else:
            query = search_query

        search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}&udm=1"

        print(f"\n🔍 Searching: {query}")
        print(f"🌐 URL: {search_url}")
        print(f"♾️  Mode: UNLIMITED - Will scrape ALL available pages!\n")

        # Check termination flag before navigating
        if termination_flag and termination_flag():
            print(f"[TERMINATION] Job terminated before navigation for query: {search_query}")
            return []

        driver.get(search_url)

        # Check termination flag after navigation
        if termination_flag and termination_flag():
            print(f"[TERMINATION] Job terminated after navigation for query: {search_query}")
            return []

        time.sleep(5)

        # Handle consent - Improved from test.py
        print(f"DEBUG: Checking for consent/popups...")
        consent_button_locators = [
            (By.XPATH, "//button[contains(., 'Accept all')]"),
            (By.XPATH, "//button[contains(., 'Reject all')]"),
            (By.XPATH, "//button[contains(., 'I agree')]"),
            (By.ID, "L2AGLb"),
        ]

        for by, val in consent_button_locators:
            try:
                # Check termination flag before clicking consent
                if termination_flag and termination_flag():
                    print(f"[TERMINATION] Job terminated during consent for query: {search_query}")
                    return []

                btn = driver.find_element(by, val)
                if btn.is_displayed():
                    btn.click()
                    print(f"DEBUG: Clicked consent button: {val}")
                    time.sleep(2)
                    break
            except:
                continue

        all_businesses = []
        page_num = 1
        max_pages = 100  # Safety limit to prevent infinite loops

        while page_num <= max_pages:
            # Check termination flag at the beginning of each page iteration
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Job terminated during page {page_num} for query: {search_query}")
                return all_businesses

            print("\n" + "=" * 80)
            print(f"📄 SCRAPING PAGE {page_num}")
            print(f"📊 Current total: {len(all_businesses)}")
            print("=" * 80 + "\n")

            # Scrape current page with termination check
            previous_count = len(all_businesses)
            all_businesses = scrape_current_page(driver, all_businesses, csv_filepath, fieldnames, termination_flag)

            # Check if any new results were added
            new_results = len(all_businesses) - previous_count
            print(f"\n✅ Scraped {new_results} new businesses from page {page_num}")

            # Check termination flag before moving to next page
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Job terminated before moving to next page {page_num + 1} for query: {search_query}")
                return all_businesses

            # Try to go to next page
            print(f"\n🔄 Attempting to navigate to page {page_num + 1}...")

            if click_next_page_with_termination(driver, termination_flag):
                page_num += 1
                print(f"✅ Successfully moved to page {page_num}")

                # Check termination flag after moving to next page
                if termination_flag and termination_flag():
                    print(f"[TERMINATION] Job terminated after moving to page {page_num} for query: {search_query}")
                    return all_businesses
            else:
                print("⚠️ No more pages available")
                break

        print("\n" + "=" * 80)
        print(f"✅ Scraping completed!")
        print(f"📊 Total businesses scraped: {len(all_businesses)}")
        print(f"📄 Total pages scraped: {page_num}")
        print("=" * 80)

        return all_businesses

    except Exception as e:
        print(f"[ERROR] ERROR in scrape_google_search: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if driver:
            print(f"DEBUG: Closing browser...")
            try:
                driver.quit()
            except:
                print(f"DEBUG: Browser already closed or error occurred while closing")
        # Remove the driver from thread_drivers if it was registered
        if job_id and thread_drivers is not None and job_id in thread_drivers:
            try:
                del thread_drivers[job_id]
                print(f"Removed driver for job {job_id} from thread_drivers")
            except KeyError:
                pass  # Already removed


