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

    # Find and print the HTML structure of business cards
    print("\n=== INSPECTING BUSINESS CARDS ===")

    # Try various selectors for business cards
    card_selectors = [
        'div.VkpGBb',  # Original selector
        'div[role="listitem"]',  # Common list item
        '[data-sokoban-container]',  # Google's container
        '.g',  # General result
        'div[style*="display: inline-block"]',  # Results with inline styles
        'div[jsaction]'  # Interactive elements
    ]

    for i, selector in enumerate(card_selectors):
        try:
            cards = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"\nSelector '{selector}' found {len(cards)} elements")

            if cards:
                # Inspect the first card
                card = cards[0]
                print(f"HTML of first card with selector '{selector}':")
                print(card.get_attribute('outerHTML')[:1000] + "..." if len(card.get_attribute('outerHTML')) > 1000 else card.get_attribute('outerHTML'))
                print("-" * 50)
                break
        except Exception as e:
            print(f"Error with selector '{selector}': {e}")

    # Also try to find elements by common classes for specific data
    print("\n=== INSPECTING SPECIFIC DATA ELEMENTS ===")

    # Common selectors for different data types
    data_selectors = {
        'name': ['.dbg0pd', '[role="heading"] span', 'h3 span'],
        'rating': ['.YrbPuc:first-child', '.yi40Hd.YrbPuc', '.F7nice span'],
        'reviews': ['.RDApEe.YrbPuc', '.YrbPuc:last-child', '.UGMiZe'],
        'address': ['.W4Efsd:nth-of-type(2) span', '.W4Efsd span', '.LrzXr'],
        'phone': ['[data-dtld]', 'a[href^="tel:"]', '.rllt__tel'],
        'website': ['a[data-ved]:not([href*="maps.google.com"]):not([href*="plus.google.com"])'],
        'category': ['.W4Efsd span', '.YhemCb', '.rllt__desc']
    }

    for data_type, selectors in data_selectors.items():
        print(f"\nSearching for {data_type}:")
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Selector '{selector}' found {len(elements)} elements:")
                    for j, elem in enumerate(elements[:3]):  # Show first 3
                        print(f"    Element {j+1}: '{elem.text}'")
                        if elem.get_attribute('href'):
                            print(f"      href: {elem.get_attribute('href')}")
            except Exception as e:
                print(f"  Error with selector '{selector}': {e}")

    input("\nPress Enter to close the browser...")

finally:
    driver.quit()
    print("Browser closed.")