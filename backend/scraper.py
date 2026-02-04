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


def extract_detail_panel(driver, listing_data=None, search_location=""):
    """Extract data from the right side detail panel after clicking"""
    business_data = listing_data.copy() if listing_data else {}
    if 'name' not in business_data: business_data['name'] = "N/A"

    # Add search location to the data
    business_data['search_location'] = search_location or "N/A"

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
        wait = WebDriverWait(driver, 4) # Further reduced wait time
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

        # Rating and Reviews - Extract from the same area/box as the name to ensure they belong to the same business
        # BUT: If rating/reviews were already extracted from the listing card, preserve them!
        rating_already_extracted = (
            business_data.get('rating') != "N/A" and 
            business_data.get('total_reviews') != "N/A"
        )
            
        if rating_already_extracted:
            print(f"DEBUG: Rating/reviews already extracted from listing card: {business_data['rating']}({business_data['total_reviews']}), SKIPPING detail panel extraction")
            rating_found = True  # Mark as found to skip all extraction attempts
        else:
            # Only extract from detail panel if NOT already extracted from listing card
            business_data['rating'] = "N/A"
            business_data['total_reviews'] = "N/A"
            rating_found = False

            # Add a small wait to ensure page is fully loaded after click
            time.sleep(0.5)

            # First, let's try to find the business name element and then look for rating/reviews nearby
            # This ensures we get data from the same business box
            name_element = None
            name_selectors = [
                'h1.DUwDvf',  # Main business name
                'h2.qrShPb',
                'div.SPZz6b h1',
                'div.SPZz6b h2',
                '[role="banner"] h1',
                '.rG09U',
                '.H07f0c'
            ]

            # Find the name element first
            for selector in name_selectors:
                try:
                    name_element = driver.find_element(By.CSS_SELECTOR, selector)
                    name_text = name_element.text.strip()
                    if name_text and name_text != "N/A":
                        print(f"DEBUG: Found business name element with text: {name_text}")
                        break
                except:
                    continue

            # Now look for rating and reviews in the same general area/parent as the name
            if name_element and not rating_found:
                try:
                    # Start from the name element and look in its vicinity
                    name_parent = name_element.find_element(By.XPATH, './..')  # Immediate parent
                    nearby_text = name_parent.text.strip()

                    print(f"DEBUG: Text near name element: {nearby_text[:100]}...")  # First 100 chars

                    # Look for rating (review_count) pattern in the same area as the name
                    pattern = r'(\d+\.?\d*)\s*\(\s*(\d+\.?\d*\s*[KMB]?|\d{1,3}(?:,\d{3})*)\s*\)'
                    match = re.search(pattern, nearby_text, re.IGNORECASE)

                    if match:
                        rating_val = match.group(1)
                        reviews_val = match.group(2).replace(',', '').strip()

                        try:
                            rating_float = float(rating_val)
                            if 0.0 <= rating_float <= 5.0:
                                business_data['rating'] = str(rating_float)
                                business_data['total_reviews'] = reviews_val
                                rating_found = True
                                print(f"DEBUG: SUCCESS - Found paired rating and reviews near name: {rating_val} ({reviews_val})")
                        except ValueError:
                            print(f"DEBUG: Rating {rating_val} is not a valid float")
                    else:
                        print(f"DEBUG: No rating(review) pattern found near name element")

                except Exception as e:
                    print(f"DEBUG: Error looking near name element: {e}")

            # If the name-area approach didn't work, try the specific element approach you provided
            if not rating_found:
                try:
                    # Look for the Y0A0hc container which should be near the name
                    wait = WebDriverWait(driver, 3)
                    rating_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.Y0A0hc')))

                    # Verify this container is in the same area as the name by checking proximity
                    container_text = rating_container.text.strip()
                    print(f"DEBUG: Found Y0A0hc container text: {container_text}")

                    # Look for the pattern "rating (review_count)" like "5.0 (478)" in the same container
                    pattern = r'(\d+\.?\d*)\s*\(\s*(\d+\.?\d*\s*[KMB]?|\d{1,3}(?:,\d{3})*)\s*\)'
                    match = re.search(pattern, container_text, re.IGNORECASE)

                    if match:
                        rating_val = match.group(1)
                        reviews_val = match.group(2).replace(',', '').strip()

                        try:
                            rating_float = float(rating_val)
                            if 0.0 <= rating_float <= 5.0:
                                business_data['rating'] = str(rating_float)
                                business_data['total_reviews'] = reviews_val
                                rating_found = True
                                print(f"DEBUG: SUCCESS - Found paired rating and reviews from Y0A0hc: {rating_val} ({reviews_val})")
                        except ValueError:
                            print(f"DEBUG: Rating {rating_val} is not a valid float")
                    else:
                        print(f"DEBUG: No rating(review) pattern found in Y0A0hc container")

                except TimeoutException:
                    print("DEBUG: Y0A0hc container not found or not loaded in time")
                except:
                    print("DEBUG: Could not find span.Y0A0hc container")

            # Fallback to F7nice container
            if not rating_found:
                try:
                    wait = WebDriverWait(driver, 3)
                    rating_container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.F7nice')))
                    container_text = rating_container.text.strip()

                    print(f"DEBUG: Found F7nice container text: {container_text}")

                    # Look for the exact pattern "rating (review_count)" like "4.9 (855)"
                    pattern = r'(\d+\.?\d*)\s*\(\s*(\d+\.?\d*\s*[KMB]?|\d{1,3}(?:,\d{3})*)\s*\)'
                    match = re.search(pattern, container_text, re.IGNORECASE)

                    if match:
                        rating_val = match.group(1)
                        reviews_val = match.group(2).replace(',', '').strip()

                        try:
                            rating_float = float(rating_val)
                            if 0.0 <= rating_float <= 5.0:
                                business_data['rating'] = str(rating_float)
                                business_data['total_reviews'] = reviews_val
                                rating_found = True
                                print(f"DEBUG: SUCCESS - Found paired rating and reviews from F7nice: {rating_val} ({reviews_val})")
                        except ValueError:
                            print(f"DEBUG: Rating {rating_val} is not a valid float")
                    else:
                        print(f"DEBUG: No rating(review) pattern found in F7nice container")

                except TimeoutException:
                    print("DEBUG: F7nice container not found or not loaded in time")
                except:
                    print("DEBUG: Could not find div.F7nice container")

            # Final fallback
            if not rating_found:
                print("DEBUG: Falling back to general selectors")

                # Try to find rating with waits
                rating_selectors = [
                    'span.Aq14fc',
                    'span.ceNzKf[aria-hidden="true"]',
                    'span.gsrt.By079',
                    'div.F7nice span[aria-hidden="true"]',
                    'span.yi40Hd.YrbPuc[aria-hidden="true"]'
                ]

                for selector in rating_selectors:
                    try:
                        wait = WebDriverWait(driver, 2)
                        rating_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                        rating_text = rating_elem.text.strip()

                        if rating_text and rating_text.replace('.', '').isdigit():
                            try:
                                rating_float = float(rating_text)
                                if 0.0 <= rating_float <= 5.0:
                                    business_data['rating'] = str(rating_float)
                                    print(f"DEBUG: Found rating separately: {rating_text}")
                                    break
                            except ValueError:
                                continue
                    except TimeoutException:
                        continue
                    except:
                        continue

                # Try to find reviews
                try:
                    wait = WebDriverWait(driver, 2)
                    review_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.RDApEe.YrbPuc[role="text"]')))
                    review_text = review_elem.text.strip()

                    # Extract the number from parentheses like "(478)"
                    paren_match = re.search(r'\((\d+\.?\d*\s*[KMB]?|\d{1,3}(?:,\d{3})*)\)', review_text, re.IGNORECASE)
                    if paren_match:
                        reviews_val = paren_match.group(1).replace(',', '').strip()
                        business_data['total_reviews'] = reviews_val
                        print(f"DEBUG: Found reviews from specific element: {reviews_val}")
                except TimeoutException:
                    print("DEBUG: Review element not found or not loaded in time")
                except:
                    print("DEBUG: Could not find review element")

        # Ensure both rating and reviews are properly set
        if business_data['rating'] == "N/A":
            print("DEBUG: No rating found, setting to N/A")
        else:
            print(f"DEBUG: Rating successfully extracted: {business_data['rating']}")

        if business_data['total_reviews'] == "N/A":
            print("DEBUG: No reviews found, setting to N/A")
        else:
            print(f"DEBUG: Reviews successfully extracted: {business_data['total_reviews']}")


        # Category/Type - ALWAYS extract from detail panel (after clicking)
        # Do NOT preserve from listing card - we want the accurate category from detail page
        
        # Priority order - span.YhemCb is most common for categories
        category_selectors = [
            'div.zloOqf span.YhemCb',  # Specific parent from user example
            'div.MaBy9 span.YhemCb',   # Another common parent
            'span.YhemCb',             # Generic fallback
            'button.DkEaL',
            'div.LBgpqf button',
            'div.PZPZ1c span:nth-of-type(1)',
            'span[class*="YhemCb"]',
            'button[jsaction*="category"]',
            'span.mgr77e',
            'div.fontBodyMedium button',
            'span[class*="fontBody"]',
            'div.RWPxGd button',
            'button[class*="DkEaL"]',
            'div[jsaction*="category"] button',
            'div.LBgpqf span',
            '[aria-label*="Categories"]',
            'div > button:first-of-type'
        ]

        for selector in category_selectors:
            try:
                # Use find_elements to catch ALL matches
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                found_valid_category = False
                
                # Check up to 5 elements
                for category_elem in elements[:5]:
                    raw_text = category_elem.text.strip()
                    # Also try aria-label if text is empty
                    if not raw_text:
                        raw_text = category_elem.get_attribute('aria-label') or ''
                        raw_text = raw_text.strip()
                    
                    if not raw_text:
                        continue

                    # CHECK 1: Is it just a price, rating, or number? (e.g. "$50-100", "4.8", "(500)")
                    # If it contains NO letters, it's not a category. (Categories names have letters)
                    if not any(c.isalpha() for c in raw_text):
                        continue
                        
                    # CHECK 2: Is it a common functional button?
                    if any(x in raw_text.lower() for x in ['phone', 'website', 'address', 'open', 'close', 'menu', 'copy', 'send to']):
                         if len(raw_text) < 20: # Long text might contain these words legitimately
                             continue

                    # CLEANING: Remove ratings, prices, etc.
                    category = raw_text
                    
                    # Remove rating patterns "4.0(1K)"
                    category = re.sub(r'\d+\.?\d*\s*\(\s*\d+\.?\d*\s*[KMB]?\s*\)', '', category)
                    # Remove price patterns "$$", "$50-100"
                    category = re.sub(r'\$+\s*\d*[-–—]?\s*\d*\+?', '', category)
                    category = re.sub(r'\$+', '', category)
                    # Remove separators
                    category = re.sub(r'[·•]|Â·|â€¢', ' ', category)
                    
                    # Clean up spaces
                    category = ' '.join(category.split())
                    
                    # If cleaning left us with nothing (or just symbols), skip
                    if not category or len(category) < 2:
                        continue

                    # If we survived, this is likely the category
                    # Take the last part if leftovers exist (e.g. "Restaurant")
                    parts = category.split()
                    # But don't split if it looks like a multi-word category "French restaurant"
                    # Just keep the cleaned string.
                    
                    business_data['category'] = category
                    print(f"DEBUG: Extracted category from detail panel using '{selector}': {category}")
                    found_valid_category = True
                    break
                
                if found_valid_category:
                    break
                    
            except Exception as e:
                continue

        if 'category' not in business_data or business_data['category'] == "N/A":
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

        # Phone Number - Enhanced extraction with better debugging
        phone_selectors = [
            'button[data-item-id*="phone"]',
            'button[aria-label*="Phone"]',
            'a[data-item-id*="phone"]',
            'a[data-dtype="d3ph"]',
            'span[data-dtype="d3ph"]',
            'span.LrzXr.zdqRlf.kno-fv a',
            'span.w8qArf.FoJoyf a.fl',
            'span.LrzXr'
        ]

        phone_found = False
        for selector in phone_selectors:
            try:
                phone_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"DEBUG: Found {len(phone_elements)} elements for selector: {selector}")

                for phone_elem in phone_elements:
                    # Try aria-label first
                    phone = phone_elem.get_attribute('aria-label')
                    if phone:
                        print(f"DEBUG: Found phone in aria-label: {phone}")

                    if not phone:
                        phone = phone_elem.text.strip()
                        if phone:
                            print(f"DEBUG: Found phone in text: {phone}")

                    # Also check for phone number in nested spans or links
                    if not phone:
                        try:
                            nested_spans = phone_elem.find_elements(By.CSS_SELECTOR, 'span, a')
                            for nested in nested_spans:
                                nested_text = nested.text.strip()
                                if nested_text and ('+' in nested_text or sum(c.isdigit() for c in nested_text) >= 7):
                                    phone = nested_text
                                    print(f"DEBUG: Found phone in nested element: {phone}")
                                    break
                        except:
                            pass

                    # Clean up
                    if phone and phone != "N/A":
                        # Remove common prefixes
                        original_phone = phone
                        phone = phone.replace('Phone: ', '').replace('Copy phone number', '').strip()
                        phone = phone.replace('Call', '').replace('phone number', '').strip()
                        phone = phone.replace('Tel:', '').replace('T:', '').strip()

                        print(f"DEBUG: Processing phone '{original_phone}' -> '{phone}'")

                        # Check if it looks like a phone number (has enough digits and not an address)
                        digit_count = sum(c.isdigit() for c in phone)
                        is_address_like = any(word in phone.lower() for word in ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'blvd', 'boulevard', 'circle', 'cir', 'court', 'ct', 'place', 'pl', 'park', 'square', 'sq'])

                        if digit_count >= 7 and not is_address_like:  # At least 7 digits for a valid phone number and not address-like
                            business_data['phone'] = phone
                            phone_found = True
                            print(f"DEBUG: Valid phone number found: {phone}")
                            break
                        else:
                            if is_address_like:
                                print(f"DEBUG: Skipping phone (appears to be address): {phone}")
                            else:
                                print(f"DEBUG: Skipping phone (not enough digits): {phone}, digit count: {digit_count}")

                if phone_found:
                    break
            except:
                continue  # Element not found or stale, try next selector

        if not phone_found:
            business_data['phone'] = "N/A"
            print("DEBUG: No phone number found, setting to N/A")
        else:
            print(f"DEBUG: Phone number successfully extracted: {business_data['phone']}")

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


def scrape_current_page(driver, all_businesses, csv_filepath, fieldnames, location, termination_flag=None):
    """Scrape listings from the current search results page"""
    wait = WebDriverWait(driver, 5)  # Reduced from 8 to 5 seconds for faster failure
    
    # Check termination before starting
    if termination_flag and termination_flag():
        return all_businesses
    
    # Validate URL - check if we're still on a valid search page
    current_url = driver.current_url
    invalid_urls = [
        'support.google.com',
        'accounts.google.com', 
        'policies.google.com',
        'google.com/sorry',
        'google.com/webhp'
    ]
    
    if any(invalid in current_url for invalid in invalid_urls):
        print(f"[ERROR] Detected invalid page during scraping: {current_url}")
        print(f"[ERROR] Stopping scrape - may be redirected or blocked")
        return all_businesses

    # Handle consent if appears
    try:
        # Check termination before handling consent
        if termination_flag and termination_flag():
            return all_businesses
        consent = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")
        consent.click()
        time.sleep(0.5)  # Reduced from 1 to 0.5 second
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
            print(f"DEBUG: Found {len(current_listings)} listings on page, attempting index {i}")
            if i >= len(current_listings):
                print(f"[WARNING] Ran out of listings at index {i}, only {len(current_listings)} available")
                break

            listing = current_listings[i]
            # Print text content of the listing to verify it's different
            listing_preview = listing.text[:30] if listing.text else "NO TEXT"
            print(f"DEBUG: Selected listing {i+1} for processing, content preview: '{listing_preview}...'")

            # CLICK AND EXTRACT
            # 1. Capture basic info from listing first (fallback)
            listing_data = {'name': 'N/A', 'address': 'N/A', 'rating': 'N/A', 'total_reviews': 'N/A', 'category': 'N/A'}
            try:
                # Try to find name/address/rating/reviews/category in the result card before clicking
                card_text = listing.text
                if card_text:
                    lines = [line.strip() for line in card_text.split('\n') if line.strip()]
                    if lines:
                        listing_data['name'] = lines[0] # Often the first line is the name
                    
                    # Extract rating and reviews from the card text (e.g., "4.8(312)")
                    pattern = r'(\d+\.?\d*)\s*\(\s*(\d+\.?\d*\s*[KMB]?|\d{1,3}(?:,\d{3})*)\s*\)'
                    match = re.search(pattern, card_text, re.IGNORECASE)
                    if match:
                        rating_val = match.group(1)
                        reviews_val = match.group(2).replace(',', '').strip()
                        try:
                            rating_float = float(rating_val)
                            if 0.0 <= rating_float <= 5.0:
                                listing_data['rating'] = str(rating_float)
                                listing_data['total_reviews'] = reviews_val
                                print(f"DEBUG: Extracted from listing card - Rating: {rating_val}, Reviews: {reviews_val}")
                        except ValueError:
                            pass
                    
                    # CATEGORY EXTRACTION DISABLED FROM LISTING CARD
                    # We only want category from the DETAIL PANEL after clicking
                    # Not from the listing preview (which may show generic terms like "Dentist")
                    
                    # Pattern 2: DISABLED - If not found, try looking at lines directly
                    # if listing_data['category'] == 'N/A' and len(lines) > 1:
                    #     for line in lines[1:4]:  # Check lines 2-4
                    #         # Common category keywords
                    #         category_indicators = ['shop', 'store', 'restaurant', 'bar', 'cafe', 'salon', 'service', 
                    #                               'center', 'clinic', 'hospital', 'hotel', 'gym', 'studio', 'office',
                    #                               'company', 'agency', 'firm', 'market', 'bakery', 'lounge', 'club']
                    #         if any(indicator in line.lower() for indicator in category_indicators):
                    #             # Make sure it's not an address or other data
                    #             if not any(x in line.lower() for x in ['street', 'st,', 'ave', 'road', 'rd,', 'blvd', 'united states', 'open', 'close', '+1 ', 'http']):
                    #                 if len(line) < 50:
                    #                     listing_data['category'] = line
                    #                     print(f"DEBUG: Extracted category from listing card (pattern 2): {line}")
                    #                     break
            except Exception as e:
                print(f"DEBUG: Error extracting from listing card: {e}")
                pass
            
            # Pattern 3: DISABLED - Try to find category element directly in the listing
            # We only want category from detail panel, not from listing preview


            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listing)
            time.sleep(randint(0, 1))  # Reduced from randint(1, 2) to randint(0, 1)

            # Check termination before clicking
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Terminating before clicking listing {i+1}")
                return all_businesses

            # Get listing information before clicking
            listing_text = listing.text[:50] if listing.text else "NO TEXT"
            print(f"DEBUG: About to click listing {i+1}, text preview: '{listing_text}...'")

            # Click
            try:
                # Try clicking the parent or the link
                listing.click()
            except:
                try:
                    driver.execute_script("arguments[0].click();", listing)
                except Exception as click_error:
                    print(f"DEBUG: Click failed for listing {i+1}, error: {click_error}")
                    pass

            # Wait for content or panel to load with dynamic checking
            print(f"DEBUG: Waiting for detail page to load after click {i+1}")
            wait = WebDriverWait(driver, 8)  # Reduced timeout
            try:
                # Wait for the main content to be present instead of fixed time
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf, h2.qrShPb, [role='heading']")))
            except TimeoutException:
                # If main elements don't load, wait a bit more but check termination
                for _ in range(3):
                    if termination_flag and termination_flag():
                        print(f"[TERMINATION] Terminating during wait for panel load")
                        return all_businesses
                    time.sleep(0.5)

            # Extract detailed data
            current_page_url = driver.current_url
            print(f"DEBUG: About to extract detail panel for listing {i+1}, current URL: {current_page_url[-50:]}")
            business_data = extract_detail_panel(driver, listing_data)

            # Add search location to the data
            if business_data:
                business_data['search_location'] = location or "N/A"

            if business_data and business_data.get('name') != "N/A":
                all_businesses.append(business_data)

                # Ensure all expected fields are present in business_data
                for field in fieldnames:
                    if field not in business_data:
                        business_data[field] = "N/A"

                # Save to CSV immediately and flush to disk
                with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(business_data)
                    csvfile.flush()

                # Display comprehensive information
                name = business_data.get('name', 'N/A')
                rating = business_data.get('rating', 'N/A')
                reviews = business_data.get('total_reviews', 'N/A')
                category = business_data.get('category', 'N/A')
                address = business_data.get('address', 'N/A')
                search_location = business_data.get('search_location', 'N/A')

                print(f"[INFO] Scraped: {name}")
                print(f"   Rating: {rating} - Reviews: {reviews}")
                print(f"   Category: {category}")
                print(f"   Address: {address}")
                print(f"   Search Location: {search_location}")
                print("-" * 80)

                # Verify data integrity
                print(f"DEBUG: Full business data keys: {list(business_data.keys())}")
                print(f"DEBUG: Rating value: '{rating}', Reviews value: '{reviews}', Search Location: '{search_location}'")
            else:
                print("[WARNING] Could not extract data for this item")
                print(f"DEBUG: business_data was: {business_data}")

            # Check termination after processing the listing
            if termination_flag and termination_flag():
                print(f"[TERMINATION] Terminating after processing listing {i+1}")
                return all_businesses

            time.sleep(randint(0, 1))  # Reduced wait time

        except Exception as e:
            print(f"[ERROR] Error on listing {i+1}: {e}")
            try:
                # Check termination before error recovery
                if termination_flag and termination_flag():
                    print(f"[TERMINATION] Terminating during error recovery for listing {i+1}")
                    return all_businesses
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
    time.sleep(1)  # Reduced from 2 to 1 second

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

            time.sleep(0.5)  # Reduced from 1 to 0.5 seconds

            # Try clicking
            try:
                next_button.click()
            except:
                driver.execute_script("arguments[0].click();", next_button)

            print("✅ Next button clicked successfully!")
            time.sleep(randint(2, 4))  # Reduced wait for page load

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

        # If fieldnames is not provided, use default with search_location
        if fieldnames is None:
            fieldnames = ['name', 'rating', 'total_reviews', 'category', 'address',
                         'phone', 'website', 'price_range', 'hours_status', 'google_maps_url', 'search_location']

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

        print(f"DEBUG: Starting Chrome for query: {search_query}")
        try:
            driver = webdriver.Chrome(options=option)
            driver.set_page_load_timeout(8)  # Further reduced timeout to allow faster interruption
            # Hide automation flag from test.py
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            print(f"DEBUG: Browser opened successfully for query: {search_query}")

            # Register the driver with the job_id if provided and thread_drivers is not None
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

        time.sleep(2)  # Reduced from 3 to 2 seconds
        
        # Validate URL - check if we're on a valid search page
        current_url = driver.current_url
        invalid_urls = [
            'support.google.com',
            'accounts.google.com',
            'policies.google.com',
            'google.com/sorry',
            'google.com/webhp',
            'google.com/preferences'
        ]
        
        if any(invalid in current_url for invalid in invalid_urls):
            print(f"[ERROR] Redirected to invalid page: {current_url}")
            print(f"[ERROR] Google may have blocked the request or there are no results")
            return []
        
        # Check for "no results" message
        try:
            no_results_indicators = [
                "did not match any documents",
                "No results found",
                "Try different keywords",
                "did not match any places"
            ]
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            if any(indicator in page_text for indicator in no_results_indicators):
                print(f"[WARNING] No results found for query: {query}")
                return []
        except:
            pass

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
                    time.sleep(1)  # Reduced from 2 to 1 second
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
            all_businesses = scrape_current_page(driver, all_businesses, csv_filepath, fieldnames, location, termination_flag)

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
            print(f"DEBUG: Closing browser for query...")
            try:
                driver.quit()
                print(f"Browser closed successfully for query")
            except Exception as e:
                print(f"DEBUG: Browser already closed or error occurred while closing: {e}")
        # Remove the driver from thread_drivers if it was registered
        if job_id and thread_drivers is not None and job_id in thread_drivers:
            try:
                del thread_drivers[job_id]
                print(f"Removed driver for job {job_id} from thread_drivers")
            except KeyError:
                print(f"Driver for job {job_id} was already removed from thread_drivers")
            except Exception as e:
                print(f"Error removing driver for job {job_id} from thread_drivers: {e}")