from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Chrome Options Setup
option = Options()
option.add_argument("--disable-blink-features=AutomationControlled")
option.add_experimental_option("useAutomationExtension", False)
option.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = webdriver.Chrome(options=option)

try:
    # Navigate to a sample search
    search_url = "https://www.google.com/search?q=coffee+shop+in+New+York&udm=1"
    print("Navigating to:", search_url)
    driver.get(search_url)
    time.sleep(8)  # Wait for results to load

    # Handle cookie consent if appears
    try:
        consent_button = driver.find_element(By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Reject all')]")
        consent_button.click()
        time.sleep(2)
    except:
        pass

    # Scroll to load more results
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    # Find business cards
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.VkpGBb')
    print(f"Found {len(cards)} business cards")

    if cards:
        card = cards[0]  # Test with the first card
        print("\nTesting selectors on the first business card...")

        # Test the specific selectors we identified
        selectors_to_test = {
            'Name': ['.dbg0pd', '[role="heading"] span'],
            'Rating': ['.YrbPuc:first-child', '.yi40Hd.YrbPuc'],
            'Reviews': ['.RDApEe.YrbPuc', '.YrbPuc:last-child'],
            'Address': ['.W4Efsd:nth-of-type(2) span', '.W4Efsd span', '.LrzXr'],
            'Phone': ['[data-dtld]', 'a[href^="tel:"]'],
            'Category': ['.W4Efsd span', '.YhemCb', '.rllt__desc']
        }

        for data_type, selectors in selectors_to_test.items():
            print(f"\n{data_type}:")
            for selector in selectors:
                try:
                    element = card.find_element(By.CSS_SELECTOR, selector)
                    text_content = element.text
                    href_content = element.get_attribute('href') if data_type in ['Phone', 'Website'] else None
                    print(f"  Selector '{selector}': '{text_content}'")
                    if href_content:
                        print(f"    href: {href_content}")
                    if text_content.strip():  # If we got content, break to next data type
                        break
                except Exception as e:
                    print(f"    Selector '{selector}' failed: {str(e)[:100]}")

        # Also test website separately
        print(f"\nWebsite:")
        website_selectors = ['a[data-ved]:not([href*="maps.google.com"]):not([href*="plus.google.com"])']
        for selector in website_selectors:
            try:
                element = card.find_element(By.CSS_SELECTOR, selector)
                href_content = element.get_attribute('href')
                print(f"  Selector '{selector}': {href_content}")
                if href_content and 'http' in href_content:
                    break
            except Exception as e:
                print(f"    Selector '{selector}' failed: {str(e)[:100]}")

finally:
    driver.quit()
    print("\nBrowser closed.")