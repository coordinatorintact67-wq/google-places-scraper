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
import csv
import os
from datetime import datetime

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
        time.sleep(2)

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
            'span.RDApEe.YrbPuc',
            'span.RDApEe',
            'span.F7nice span:nth-child(2)',
            'div.F7nice span[aria-label*="reviews"]'
        ]

        for selector in review_selectors:
            try:
                reviews_elem = driver.find_element(By.CSS_SELECTOR, selector)
                reviews_text = reviews_elem.text.strip()
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
            'span.LrzXr',
            'button[data-item-id="address"]',
            'button[data-tooltip*="Address"]',
            'div.rogA2c[data-item-id="address"]',
            'div[data-item-id="address"]'
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
            'span.LrzXr'
        ]

        for selector in phone_selectors:
            try:
                phone_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for phone_elem in phone_elements:
                    phone = phone_elem.get_attribute('aria-label')
                    if not phone:
                        phone = phone_elem.text.strip()

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

        business_data['google_maps_url'] = driver.current_url

        return business_data

    except Exception as e:
        print(f"❌ Error extracting detail panel: {e}")
        return None


def scrape_current_page(driver, all_businesses):
    """Scrape listings from the current search results page"""
    wait = WebDriverWait(driver, 15)

    # Handle consent if appears
    try:
        consent = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")
        consent.click()
        time.sleep(2)
    except:
        pass

    # Find clickable listings
    clickable_selectors = [
        'a.vwVdIc',
        'div.VkpGBb a',
        'a[jsname]',
        'div[role="article"] a',
        'div.g a',
        'a.sVXRqc'  # Additional selector
    ]
    
    listings = []
    successful_selector = None
    
    for selector in clickable_selectors:
        try:
            listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            if len(listings) > 0:
                successful_selector = selector
                print(f"✓ Found {len(listings)} listings using: {selector}")
                break
        except:
            continue

    if not listings:
        print("⚠️ No clickable listings found on this page")
        return all_businesses

    total_to_scrape = len(listings)
    print(f"📊 Will scrape ALL {total_to_scrape} listings from current page")

    for i in range(total_to_scrape):
        try:
            print(f"\n[{len(all_businesses)+1}] Processing listing {i+1}...")

            # Re-find listings to avoid stale elements
            current_listings = driver.find_elements(By.CSS_SELECTOR, successful_selector)
            if i >= len(current_listings):
                print(f"⚠️ Ran out of listings at index {i}")
                break
            
            listing = current_listings[i]

            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", listing)
            time.sleep(randint(1, 2))

            # Click
            try:
                listing.click()
            except:
                driver.execute_script("arguments[0].click();", listing)
            
            time.sleep(randint(3, 5))

            # Extract data
            business_data = extract_detail_panel()

            if business_data and business_data.get('name') != "N/A":
                all_businesses.append(business_data)
                global csv_filepath, fieldnames
                with open(csv_filepath, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow(business_data)
                print(f"Saved to CSV: {business_data['name']}")
                print(f"✅ {business_data['name']}")
                print(f"   ⭐ {business_data['rating']} ({business_data['total_reviews']} reviews)")
                print(f"   📍 {business_data['address']}")
                print(f"   📞 {business_data['phone']}")
                print(f"   🌐 {business_data['website']}")
                print(f"   🏷️  {business_data['category']}")
                print("-" * 80)
            else:
                print("⚠️ Could not extract data")

            # Go back
            driver.back()
            time.sleep(randint(2, 4))
            
        except Exception as e:
            print(f"❌ Error on listing {i+1}: {e}")
            try:
                driver.back()
                time.sleep(2)
            except:
                pass
            continue

    return all_businesses


def click_next_page(driver):
    """Click next page button - IMPROVED VERSION"""
    
    # Scroll to bottom first
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
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
        try:
            print(f"🔍 Trying selector: {selector}")
            
            # Wait for element
            next_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Check if button is enabled (not greyed out)
            aria_label = next_button.get_attribute('aria-label')
            if aria_label and 'next' in aria_label.lower():
                print(f"✓ Found next button: {aria_label}")
            
            # Scroll to button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            
            # Try clicking
            try:
                next_button.click()
            except:
                driver.execute_script("arguments[0].click();", next_button)
            
            print("✅ Next button clicked successfully!")
            time.sleep(randint(4, 6))  # Wait for page load
            return True
            
        except Exception as e:
            continue
    
    print("❌ Could not find next button")
    return False


def scrape_google_search(search_query, location=""):
    """Main scraping with UNLIMITED pagination - Scrapes ALL available results"""

    if location:
        query = f"{search_query} in {location}"
    else:
        query = search_query

    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&udm=1"

    print(f"\n🔍 Searching: {query}")
    print(f"🌐 URL: {search_url}")
    print(f"♾️  Mode: UNLIMITED - Will scrape ALL available pages!\n")

    driver.get(search_url)
    time.sleep(5)

    # Handle consent
    try:
        consent = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")
        consent.click()
        time.sleep(2)
    except:
        pass

    all_businesses = []
    page_num = 1
    max_pages = 100  # Safety limit to prevent infinite loops

    while page_num <= max_pages:
        print("\n" + "=" * 80)
        print(f"📄 SCRAPING PAGE {page_num}")
        print(f"📊 Current total: {len(all_businesses)}")
        print("=" * 80 + "\n")

        # Scrape current page
        previous_count = len(all_businesses)
        all_businesses = scrape_current_page(driver, all_businesses)
        
        # Check if any new results were added
        new_results = len(all_businesses) - previous_count
        print(f"\n✅ Scraped {new_results} new businesses from page {page_num}")

        # Try to go to next page
        print(f"\n🔄 Attempting to navigate to page {page_num + 1}...")
        
        if click_next_page(driver):
            page_num += 1
            print(f"✅ Successfully moved to page {page_num}")
        else:
            print("⚠️ No more pages available")
            break

    print("\n" + "=" * 80)
    print(f"✅ Scraping completed!")
    print(f"📊 Total businesses scraped: {len(all_businesses)}")
    print(f"📄 Total pages scraped: {page_num}")
    print("=" * 80)
    
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
        
        MIN_RATING = 0.0
        REQUIRE_PHONE = False
        REQUIRE_WEBSITE = False
        # ====================================

        today = datetime.now().strftime("%Y-%m-%d")
        save_dir = os.path.join('GSearch Data', today)
        os.makedirs(save_dir, exist_ok=True)

        global csv_filepath, fieldnames, seen_businesses
        csv_filename = f"google_search_results_{SEARCH_QUERY.replace(' ', '_')}_{LOCATION.replace(' ', '_')}"
        csv_filepath = os.path.join(save_dir, f"{csv_filename}.csv")
        counter = 1
        while os.path.exists(csv_filepath):
            csv_filepath = os.path.join(save_dir, f"{csv_filename}_{counter}.csv")
            counter += 1

        fieldnames = ['name', 'rating', 'total_reviews', 'category', 'address', 'phone', 'website', 'price_range', 'hours_status', 'google_maps_url']

        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
        print("🚀 Google Search Multi-Page Business Scraper")
        print("=" * 80)
        print(f"🎯 Query: {SEARCH_QUERY}")
        print(f"📍 Location: {LOCATION}")
        print(f"♾️  Mode: UNLIMITED - Will scrape ALL available results!")
        print("=" * 80)
        
        # Scrape
        all_data = scrape_google_search(
            search_query=SEARCH_QUERY,
            location=LOCATION
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
        
        print(f"\n📄 CSV saved incrementally to: {csv_filepath}")
        print("\n" + "=" * 80)
        print("✅ DONE! Files saved:")
        print("   📄 google_search_results.json")
        if MIN_RATING > 0 or REQUIRE_PHONE or REQUIRE_WEBSITE:
            print("   📄 google_search_filtered.json")
        
        # Summary
        print(f"\n📊 FINAL SUMMARY:")
        print(f"   Total businesses: {len(all_data)}")
        if all_data:
            with_phone = sum(1 for b in all_data if b.get('phone') != 'N/A')
            with_website = sum(1 for b in all_data if b.get('website') != 'N/A')
            avg_rating = sum(float(b.get('rating', '0').replace(',', '.')) for b in all_data if b.get('rating') != 'N/A') / len(all_data)
            print(f"   With phone: {with_phone} ({with_phone/len(all_data)*100:.1f}%)")
            print(f"   With website: {with_website} ({with_website/len(all_data)*100:.1f}%)")
            print(f"   Average rating: {avg_rating:.2f}")
        
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