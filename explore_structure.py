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
        print("\n=== FULL HTML OF FIRST CARD (truncated) ===")
        html_content = card.get_attribute('outerHTML')
        print(html_content[:2000] + "..." if len(html_content) > 2000 else html_content)

        print("\n=== EXPLORING NESTED ELEMENTS ===")
        # Look for all spans and divs within the card
        spans = card.find_elements(By.TAG_NAME, 'span')
        print(f"Found {len(spans)} span elements in the card")
        for i, span in enumerate(spans[:10]):  # Print first 10
            text = span.text
            if text.strip():
                print(f"  Span {i}: '{text}'")

        divs = card.find_elements(By.TAG_NAME, 'div')
        print(f"Found {len(divs)} div elements in the card")
        for i, div in enumerate(divs[:15]):  # Print first 15
            text = div.text
            if text.strip():
                print(f"  Div {i}: '{text}'")

        # Look for anchor tags
        anchors = card.find_elements(By.TAG_NAME, 'a')
        print(f"Found {len(anchors)} anchor elements in the card")
        for i, anchor in enumerate(anchors[:5]):  # Print first 5
            text = anchor.text
            href = anchor.get_attribute('href')
            print(f"  Anchor {i}: text='{text}', href='{href}'")

finally:
    driver.quit()
    print("\nBrowser closed.")