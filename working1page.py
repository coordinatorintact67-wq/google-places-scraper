from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import re

# Chrome Options
option = webdriver.ChromeOptions()
# option.add_argument("--headless")
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_experimental_option("useAutomationExtension", False)
option.add_argument('--disable-infobars')
option.add_experimental_option("excludeSwitches", ["enable-automation"])
option.add_argument("--start-maximized")

driver = webdriver.Chrome(options=option)
wait = WebDriverWait(driver, 10)



def extract_detail_panel():
    """Extract data from the right side detail panel after clicking"""
    business_data = {}

    try:
        time.sleep(2)  # Wait for panel to load

        # Business Name
        name_selectors = [
            'h2.qrShPb',
            'h1.DUwDvf',
            '[role="heading"]',
            'div.SPZz6b h2',
            'div.SPZz6b h1'
        ]

        for selector in name_selectors:
            try:
                name_elem = driver.find_element(By.CSS_SELECTOR, selector)
                name = name_elem.text.strip()
                if name:
                    business_data['name'] = name
                    break
            except:
                continue

        if 'name' not in business_data:
            business_data['name'] = "N/A"

        # Rating
        rating_selectors = [
            'span.ceNzKf[aria-hidden="true"]',
            'div.F7nice span[aria-hidden="true"]',
            'span.Aq14fc'
        ]

        for selector in rating_selectors:
            try:
                rating = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if rating and rating.replace('.', '').isdigit():
                    business_data['rating'] = rating
                    break
            except:
                continue

        if 'rating' not in business_data:
            business_data['rating'] = "N/A"

        # Total Reviews
        review_selectors = [
            'span.RDApEe.YrbPuc',  # Specific selector from the HTML you provided
            'span.RDApEe',
            'span.F7nice span:nth-child(2)',
            'div.F7nice span[aria-label*="reviews"]'
        ]

        for selector in review_selectors:
            try:
                reviews_elem = driver.find_element(By.CSS_SELECTOR, selector)
                reviews_text = reviews_elem.text.strip()
                # Extract number from parentheses
                reviews = reviews_text.replace('(', '').replace(')', '').replace(',', '').strip()
                if reviews and (reviews.isdigit() or 'K' in reviews.upper()):
                    business_data['total_reviews'] = reviews
                    break
            except:
                continue

        if 'total_reviews' not in business_data:
            business_data['total_reviews'] = "N/A"

        # Category/Type
        category_selectors = [
            'button.DkEaL',
            'span.YhemCb',
            'div.LBgpqf button'
        ]

        for selector in category_selectors:
            try:
                category = driver.find_element(By.CSS_SELECTOR, selector).text.strip()
                if category:
                    business_data['category'] = category
                    break
            except:
                continue

        if 'category' not in business_data:
            business_data['category'] = "N/A"

        # Address
        address_selectors = [
            'span.LrzXr',  # Direct address element from inspection
            'button[data-item-id="address"]',
            'button[data-tooltip*="Address"]',
            'div.rogA2c[data-item-id="address"]',
            'div[data-item-id="address"]'  # Fallback selector
        ]

        for selector in address_selectors:
            try:
                addr_elem = driver.find_element(By.CSS_SELECTOR, selector)
                # Try aria-label first
                address = addr_elem.get_attribute('aria-label')
                if not address:
                    address = addr_elem.text.strip()

                # Clean up
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
            'a[data-dtype="d3ph"]',  # Specific selector for the HTML structure you showed
            'span.LrzXr.zdqRlf.kno-fv a',  # Another specific selector from your HTML
            'span.w8qArf.FoJoyf a.fl',  # Selector for the phone link element
            'span.LrzXr'  # Direct span with phone number
        ]

        for selector in phone_selectors:
            try:
                phone_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for phone_elem in phone_elements:
                    # Try aria-label
                    phone = phone_elem.get_attribute('aria-label')
                    if not phone:
                        phone = phone_elem.text.strip()

                    # Also check for phone number in nested spans or links
                    if not phone:
                        try:
                            nested_spans = phone_elem.find_elements(By.CSS_SELECTOR, 'span, a')
                            for nested in nested_spans:
                                nested_text = nested.text.strip()
                                if nested_text and ('+' in nested_text or sum(c.isdigit() for c in nested_text) >= 7):
                                    phone = nested_text
                                    break
                        except:
                            pass

                    # Clean up
                    if phone:
                        # Remove common prefixes
                        phone = phone.replace('Phone: ', '').replace('Copy phone number', '').strip()
                        phone = phone.replace('Call', '').replace('phone number', '').strip()

                        # Check if it looks like a phone number
                        if phone and ('+' in phone or sum(c.isdigit() for c in phone) >= 7):
                            # Further clean up to remove extra text
                            # Extract phone number pattern
                            phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,})', phone)
                            if phone_match:
                                business_data['phone'] = phone_match.group(1).strip()
                            else:
                                business_data['phone'] = phone
                            break

                if 'phone' in business_data:
                    break
            except Exception as e:
                continue

        # Additional attempt: Look for phone numbers in the entire page
        if business_data.get('phone', "N/A") == "N/A":
            try:
                # Look for common phone number patterns in the entire page
                page_text = driver.page_source
                # Regex to find phone numbers
                phone_patterns = [
                    r'\+\d{1,3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',  # +1 212-564-7444
                    r'\+?\d{1,3}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{4}',  # Various formats
                    r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # 123-456-7890
                ]

                for pattern in phone_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        # Take the first match that looks like a valid phone number
                        for match in matches:
                            if '+' in match or sum(c.isdigit() for c in match) >= 10:
                                business_data['phone'] = match.strip()
                                break
                        if business_data['phone'] != "N/A":
                            break
            except:
                pass

        if 'phone' not in business_data:
            business_data['phone'] = "N/A"

        # Website
        website_selectors = [
            'a.n1obkb.mI8Pwc',  # Specific selector from the HTML you provided
            'a[data-item-id="authority"]',
            'a[aria-label*="Website"]',
            'button[data-item-id="authority"]'
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
            'span.mgr77e'
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
            'div.MkXq9e'
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

        # Current URL (Google Maps Link)
        business_data['google_maps_url'] = driver.current_url

        return business_data

    except Exception as e:
        print(f"❌ Error extracting detail panel: {e}")
        return None


def extract_from_search_results(listing_element):
    """Extract data directly from search results page without clicking"""
    business_data = {}

    try:
        # Name
        name_selectors = [
            '.dbg0pd',  # Common name selector in search results
            '.LC20lb',  # Another common name selector
            '.s3v9rd',  # Another name selector
            'h3'
        ]

        for selector in name_selectors:
            try:
                name_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                name = name_elem.text.strip()
                if name:
                    business_data['name'] = name
                    break
            except:
                continue

        if 'name' not in business_data:
            business_data['name'] = "N/A"

        # Address
        address_selectors = [
            '.rllt__details .rllt__descriptor',  # Address in local results
            '.rllt__details div',  # Alternative address selector
            '.LrzXr'  # Direct address element
        ]

        for selector in address_selectors:
            try:
                addr_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                address = addr_elem.text.strip()
                if address and '·' in address:  # Google often puts address with rating separator
                    address = address.split('·')[0].strip()
                if address:
                    business_data['address'] = address
                    break
            except:
                continue

        if 'address' not in business_data:
            business_data['address'] = "N/A"

        # Phone Number - specifically targeting the structure you mentioned
        phone_selectors = [
            'a[data-dtype="d3ph"]',  # The specific selector from your HTML
            'span.LrzXr.zdqRlf.kno-fv a',  # Selector for phone link
            'span.w8qArf.FoJoyf a.fl',  # Phone link selector
            '.rllt__phone-number',  # Phone in local results
            'span.LrzXr'  # General span with phone
        ]

        for selector in phone_selectors:
            try:
                phone_elements = listing_element.find_elements(By.CSS_SELECTOR, selector)
                for phone_elem in phone_elements:
                    # Try aria-label
                    phone = phone_elem.get_attribute('aria-label')
                    if not phone:
                        phone = phone_elem.text.strip()

                    # Also check for phone number in nested spans or links
                    if not phone:
                        try:
                            nested_spans = phone_elem.find_elements(By.CSS_SELECTOR, 'span, a')
                            for nested in nested_spans:
                                nested_text = nested.text.strip()
                                if nested_text and ('+' in nested_text or sum(c.isdigit() for c in nested_text) >= 7):
                                    phone = nested_text
                                    break
                        except:
                            pass

                    # Clean up
                    if phone:
                        # Remove common prefixes
                        phone = phone.replace('Phone: ', '').replace('Copy phone number', '').strip()
                        phone = phone.replace('Call', '').replace('phone number', '').strip()

                        # Check if it looks like a phone number
                        if phone and ('+' in phone or sum(c.isdigit() for c in phone) >= 7):
                            # Further clean up to remove extra text
                            # Extract phone number pattern
                            phone_match = re.search(r'(\+?\d[\d\s\-\(\)]{7,})', phone)
                            if phone_match:
                                business_data['phone'] = phone_match.group(1).strip()
                            else:
                                business_data['phone'] = phone
                            break

                if 'phone' in business_data:
                    break
            except Exception as e:
                continue

        # If still no phone, try to find it in the HTML source of this element
        if business_data.get('phone', "N/A") == "N/A":
            try:
                element_html = listing_element.get_attribute('innerHTML')
                # Look for phone number patterns in the element's HTML
                phone_patterns = [
                    r'\+\d{1,3}[\s\-]?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}',  # +1 212-564-7444
                    r'\+?\d{1,3}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{4}',  # Various formats
                    r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # 123-456-7890
                ]

                for pattern in phone_patterns:
                    matches = re.findall(pattern, element_html)
                    if matches:
                        # Take the first match that looks like a valid phone number
                        for match in matches:
                            if '+' in match or sum(c.isdigit() for c in match) >= 10:
                                business_data['phone'] = match.strip()
                                break
                        if business_data['phone'] != "N/A":
                            break
            except:
                pass

        if 'phone' not in business_data:
            business_data['phone'] = "N/A"

        # Rating
        rating_selectors = [
            '.rllt__star-rating .rllt__rating',
            '.rllt__details .rllt__descriptor',
            '.rllt__bottom-line .rllt__rating'
        ]

        for selector in rating_selectors:
            try:
                rating_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                rating_text = rating_elem.text.strip()
                # Extract rating from text like "4.5 · 100 reviews"
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    business_data['rating'] = rating_match.group(1)
                    break
            except:
                continue

        if 'rating' not in business_data:
            business_data['rating'] = "N/A"

        # Total Reviews
        review_selectors = [
            'span.RDApEe.YrbPuc',  # Specific selector from the HTML you provided
            '.rllt__bottom-line .rllt__reviews',
            '.rllt__details .rllt__descriptor',
            'span[aria-label*="stars"]'
        ]

        for selector in review_selectors:
            try:
                review_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                review_text = review_elem.text.strip()
                # Extract number of reviews
                review_match = re.search(r'\(([\d,]+)\)|([\d,]+)\s+reviews?', review_text, re.IGNORECASE)
                if review_match:
                    # Get the first non-None group
                    groups = review_match.groups()
                    for group in groups:
                        if group:
                            business_data['total_reviews'] = group.replace(',', '').strip()
                            break
                    if 'total_reviews' in business_data:
                        break
            except:
                continue

        if 'total_reviews' not in business_data:
            business_data['total_reviews'] = "N/A"

        # Category
        category_selectors = [
            '.rllt__bottom-line .rllt__category',
            '.rllt__details .rllt__descriptor',
            '.rllt__category-button'
        ]

        for selector in category_selectors:
            try:
                category_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                category = category_elem.text.strip()
                if category and '·' in category:  # Split on separator if present
                    parts = category.split('·')
                    for part in parts:
                        part = part.strip()
                        if part and not re.match(r'^\d+\.?\d*$', part) and '(' not in part and ')' not in part:
                            business_data['category'] = part
                            break
                    if 'category' in business_data:
                        break
                elif category:
                    business_data['category'] = category
                    break
            except:
                continue

        if 'category' not in business_data:
            business_data['category'] = "N/A"

        # Website
        website_selectors = [
            'a.n1obkb.mI8Pwc',  # Specific selector from the HTML you provided
            'a[data-item-id="authority"]',
            'a[href*="http"]:not([data-item-id="phone"]):not([data-item-id="address"])'
        ]

        for selector in website_selectors:
            try:
                website_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
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

        # Price range
        price_selectors = [
            '.rllt__bottom-line .rllt__price'
        ]

        for selector in price_selectors:
            try:
                price_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                price = price_elem.text.strip()
                if price and '$' in price:
                    business_data['price_range'] = price
                    break
            except:
                continue

        if 'price_range' not in business_data:
            business_data['price_range'] = "N/A"

        # Hours status
        hours_selectors = [
            '.rllt__bottom-line .rllt__open-status'
        ]

        for selector in hours_selectors:
            try:
                hours_elem = listing_element.find_element(By.CSS_SELECTOR, selector)
                hours = hours_elem.text.strip()
                if hours:
                    business_data['hours_status'] = hours
                    break
            except:
                continue

        if 'hours_status' not in business_data:
            business_data['hours_status'] = "N/A"

        return business_data

    except Exception as e:
        print(f"❌ Error extracting from search results: {e}")
        return None


def scrape_current_page(driver, all_businesses, max_results):
    """Scrape listings from the current search results page"""
    wait = WebDriverWait(driver, 10)

    # Handle consent if appears on new pages
    try:
        consent = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")
        consent.click()
        time.sleep(2)
    except:
        pass

    # Find clickable listings
    clickable_selectors = ['a.vwVdIc', 'div.VkpGBb a', 'a[jsname]', 'div[role=\"article\"] a', 'div.g a']
    listings = []
    successful_selector = None
    for selector in clickable_selectors:
        try:
            listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            successful_selector = selector
            print(f"Found {len(listings)} listings using selector: {selector}")
            break
        except:
            continue

    if not listings:
        print("No clickable listings on this page.")
        return all_businesses

    total_to_scrape = min(len(listings), max_results - len(all_businesses))
    print(f"Will scrape {total_to_scrape} more listings from current page.")

    for i in range(total_to_scrape):
        try:
            print(f"\n[{i+1}/{total_to_scrape}] Clicking listing...")

            # Re-find to avoid stale elements
            current_listings = driver.find_elements(By.CSS_SELECTOR, successful_selector)
            if i >= len(current_listings):
                print(f"⚠️ Ran out of listings at {i}")
                break
            listing = current_listings[i]

            # Scroll to element
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listing)
            time.sleep(randint(1, 2))

            # Click the listing
            try:
                listing.click()
            except:
                driver.execute_script("arguments[0].click();", listing)
            time.sleep(randint(2, 4))

            # Extract from detail panel
            print("📊 Extracting data from detail panel...")
            business_data = extract_detail_panel()

            if business_data and business_data.get('name') != "N/A":
                all_businesses.append(business_data)

                print(f"✅ {business_data['name']}")
                print(f"   ⭐ {business_data['rating']} ({business_data['total_reviews']} reviews)")
                print(f"   📍 {business_data['address']}")
                print(f"   📞 {business_data['phone']}")
                print(f"   🌐 {business_data['website']}")
                print(f"   🏷️  {business_data['category']}")
                print(f"   💰 {business_data['price_range']}")
                print("-" * 80)

                # Save incrementally
                with open("google_search_results.json", "w", encoding="utf-8") as f:
                    json.dump(all_businesses, f, indent=2, ensure_ascii=False)

                with open("google_search_results.txt", "a", encoding="utf-8") as f:
                    f.write(str(business_data) + "\n")
            else:
                print("⚠️ Could not extract data from detail panel")

            # Go back to search results
            driver.back()
            time.sleep(randint(2, 3))
        except Exception as e:
            print(f"❌ Error on listing {i+1}: {e}")
            try:
                driver.back()
                time.sleep(2)
            except:
                pass
            continue
    return all_businesses


def scrape_google_search(search_query, location="", max_results=50):
    """Main scraping with pagination"""

    if location:
        query = f"{search_query} in {location}"
    else:
        query = search_query

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&udm=1"

    print(f"\n🔍 Searching: {query}")
    print(f"🌐 URL: {search_url}\n")

    driver.get(search_url)
    time.sleep(5)

    # Handle consent
    try:
        consent = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")

        consent.click()
        time.sleep(2)
    except:
        pass


    # Find clickable business listings
    print("\n📍 Finding business listings...")

    clickable_selectors = [
        'a.vwVdIc',  # Common clickable link in Google search
        'div.VkpGBb a',
        'a[jsname]',
        'div[role=\"article\"] a',
        'div.g a'
    ]

    clickable_listings = []
    for selector in clickable_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if len(elements) > 0:
                clickable_listings = elements
                print(f"✓ Found {len(elements)} clickable listings with: {selector}")
                break
        except:
            continue

    if not clickable_listings:
        print("❌ No clickable listings found! Trying alternative approach...")
        # Try to extract data directly from search results
        try:
            # Look for local business listings
            local_selectors = [
                '.rllt__details',  # Local results details
                '.rlfsb',  # Another local results container
                '[data-sokoban-container]'  # Container for local results
            ]

            for local_selector in local_selectors:
                try:
                    local_containers = driver.find_elements(By.CSS_SELECTOR, local_selector)
                    if local_containers:
                        print(f"Found {len(local_containers)} potential local result containers")
                        all_businesses = []

                        for idx, container in enumerate(local_containers[:max_results]):
                            try:
                                print(f"\n[{idx+1}/{min(len(local_containers), max_results)}] Processing local listing...")

                                # Extract directly from search results
                                business_data = extract_from_search_results(container)

                                if business_data and business_data.get('name') != "N/A":
                                    all_businesses.append(business_data)

                                    print(f"✅ {business_data['name']}")
                                    print(f"   ⭐ {business_data['rating']} ({business_data['total_reviews']} reviews)")
                                    print(f"   📍 {business_data['address']}")
                                    print(f"   📞 {business_data['phone']}")
                                    print(f"   🌐 {business_data['website']}")
                                    print(f"   🏷️  {business_data['category']}")
                                    print("-" * 80)

                                    # Save incrementally
                                    with open("google_search_results.json", "w", encoding="utf-8") as f:
                                        json.dump(all_businesses, f, indent=2, ensure_ascii=False)

                                    with open("google_search_results.txt", "a", encoding="utf-8") as f:
                                        f.write(str(business_data) + "\n")
                                else:
                                    print("⚠️ Could not extract data from search results")

                            except Exception as e:
                                print(f"❌ Error processing local listing {idx+1}: {e}")
                                continue

                        print("\n" + "=" * 80)
                        print(f"✅ Scraping completed! Total scraped: {len(all_businesses)}")
                        return all_businesses

                except:
                    continue

        except:
            print("❌ No local listings found either!")
            return []

    # First page
    print(f"\n🎯 Will scrape first page...\n")
    print("=" * 80)

    all_businesses = scrape_current_page(driver, [], max_results)
    print("✅ First page completed. Starting pagination...")

    page_num = 2
    while len(all_businesses) < max_results:
        time.sleep(3)
        next_button = None
        selectors = [
            'g-fab.sr9hec.OvQkSb.s3IB3',
            'button[aria-label*=\"Next\"]',
            'a[aria-label*=\"Next page\"]',
            '.Mii59c',
            '[jsname=\"Nav\"]'
        ]
        for selector in selectors:
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                next_button.click()
                break
            except:
                continue
        if not next_button:
            print("No more next button found. Stopping.")
            break

        print(f"✅ Clicked next button. Scraping page {page_num}...")
        time.sleep(5)  # Page load
        all_businesses = scrape_current_page(driver, all_businesses, max_results)
        page_num += 1

    print("\n" + "=" * 80)
    print(f"✅ Scraping completed! Total scraped: {len(all_businesses)}")
    return all_businesses


def filter_by_criteria(data, min_rating=0.0, has_phone=False, has_website=False):
    """Filter results"""
    filtered = []
    
    for business in data:
        try:
            rating = float(business.get('rating', '0').replace(',', '.'))
        except:
            rating = 0.0
        
        if rating < min_rating:
            continue
        
        if has_phone and business.get('phone') == "N/A":
            continue
        
        if has_website and business.get('website') == "N/A":
            continue
        
        filtered.append(business)
    
    return filtered


def main():
    """Main function"""
    try:
        # ============= SETTINGS =============
        SEARCH_QUERY = "restaurants"
        LOCATION = "New York"
        MAX_RESULTS = 20
        
        MIN_RATING = 0.0
        REQUIRE_PHONE = False
        REQUIRE_WEBSITE = False
        # ====================================
        
        print("🚀 Google Search Business Scraper with Click Logic")
        print("=" * 80)
        print(f"🎯 Query: {SEARCH_QUERY}")
        print(f"📍 Location: {LOCATION}")
        print(f"📊 Max Results: {MAX_RESULTS}")
        print("=" * 80)
        
        # Scrape
        all_data = scrape_google_search(
            search_query=SEARCH_QUERY,
            location=LOCATION,
            max_results=MAX_RESULTS
        )
        
        # Filter
        if MIN_RATING > 0 or REQUIRE_PHONE or REQUIRE_WEBSITE:
            print(f"\n🔍 Applying filters...")
            filtered_data = filter_by_criteria(
                all_data,
                min_rating=MIN_RATING,
                has_phone=REQUIRE_PHONE,
                has_website=REQUIRE_WEBSITE
            )
            
            print(f"✓ Filtered: {len(filtered_data)}/{len(all_data)}")
            
            with open("google_search_filtered.json", "w", encoding="utf-8") as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 80)
        print("✅ DONE! Files saved:")
        print("   📄 google_search_results.json")
        print("   📄 google_search_results.txt")
        if MIN_RATING > 0 or REQUIRE_PHONE or REQUIRE_WEBSITE:
            print("   📄 google_search_filtered.json")
        
        # Summary
        print(f"\n📊 SUMMARY:")
        print(f"   Total businesses scraped: {len(all_data)}")
        if all_data:
            with_phone = sum(1 for b in all_data if b.get('phone') != 'N/A')
            with_website = sum(1 for b in all_data if b.get('website') != 'N/A')
            print(f"   Businesses with phone: {with_phone}")
            print(f"   Businesses with website: {with_website}")
        
    except Exception as ex:
        print(f"❌ Error: {ex}")
        import traceback
        traceback.print_exc()
    
    finally:
        time.sleep(3)
        driver.quit()
        print("\n👋 Browser closed!")


if __name__ == '__main__':
    main()