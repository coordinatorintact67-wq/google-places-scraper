"""
Google Places Scraper using Playwright
Reads queries from input.txt and scrapes business information from Google Maps/Places
"""

import csv
import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def setup_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    headers = [
        'search_query', 'business_name', 'address', 'phone', 'rating',
        'review_count', 'business_hours', 'website', 'category', 'timestamp'
    ]

    single_file = Path('google_places_single_results.csv')
    batch_file = Path('google_places_batch_results.csv')

    for file in [single_file, batch_file]:
        if not file.exists():
            with open(file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)

    return single_file, batch_file


def extract_business_data(page, query):
    """Extract business information from Google Maps/Places results"""
    results = []

    try:
        # Wait for results to load
        page.wait_for_selector('[role="main"]', timeout=30000)
        time.sleep(2)  # Additional wait for dynamic content

        # Try to get business listings
        business_elements = page.locator('div.Nv2PK')
        count = business_elements.count()

        for i in range(min(count, 20)):  # Limit to 20 results per query
            try:
                # Click on business to get details
                business_elements.nth(i).click()
                time.sleep(1.5)

                # Extract business details
                business_name = page.locator('h1.DUwDvf').text_content(timeout=2000)

                # Get address
                address = ""
                try:
                    address_elem = page.locator('button[aria-label*="Address"]')
                    if address_elem.count() > 0:
                        address = address_elem.text_content(timeout=1000)
                except:
                    pass

                # Get phone
                phone = ""
                try:
                    phone_elem = page.locator('button[aria-label*="Phone"]')
                    if phone_elem.count() > 0:
                        phone = phone_elem.text_content(timeout=1000)
                except:
                    pass

                # Get website
                website = ""
                try:
                    website_elem = page.locator('a[aria-label*="Website"]')
                    if website_elem.count() > 0:
                        website = website_elem.get_attribute('href', timeout=1000)
                except:
                    pass

                # Get rating
                rating = ""
                review_count = ""
                try:
                    rating_elem = page.locator('span.ceNzKf')
                    if rating_elem.count() > 0:
                        rating_text = rating_elem.get_attribute('aria-label', timeout=1000)
                        if rating_text:
                            # Extract numeric rating
                            import re
                            rating_match = re.search(r'([\d.]+)\s+stars', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)

                            # Extract review count
                            review_match = re.search(r'([\d,]+)\s+reviews', rating_text)
                            if review_match:
                                review_count = review_match.group(1).replace(',', '')
                except:
                    pass

                # Get business hours
                business_hours = ""
                try:
                    hours_elem = page.locator('div.OqCZI')
                    if hours_elem.count() > 0:
                        business_hours = hours_elem.text_content(timeout=1000)
                except:
                    pass

                # Get category
                category = ""
                try:
                    category_elem = page.locator('button[jsaction=\"pane.rating.category\"]')
                    if category_elem.count() > 0:
                        category = category_elem.text_content(timeout=1000)
                except:
                    pass

                results.append({
                    'search_query': query,
                    'business_name': business_name.strip(),
                    'address': address.strip(),
                    'phone': phone.strip(),
                    'rating': rating,
                    'review_count': review_count,
                    'business_hours': business_hours.strip(),
                    'website': website,
                    'category': category.strip(),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })

                # Go back to results
                try:
                    back_btn = page.locator('button[aria-label="Back"]')
                    if back_btn.count() > 0:
                        back_btn.click()
                        time.sleep(1)
                except:
                    page.go_back()
                    time.sleep(1)

            except Exception as e:
                print(f"Error extracting data for result {i}: {str(e)}")
                continue

    except Exception as e:
        print(f"Error loading results for query '{query}': {str(e)}")

    return results


def write_to_csv(data, csv_file, single_run=False):
    """Write results to CSV file in streaming fashion"""
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for result in data:
            writer.writerow([
                result['search_query'],
                result['business_name'],
                result['address'],
                result['phone'],
                result['rating'],
                result['review_count'],
                result['business_hours'],
                result['website'],
                result['category'],
                result['timestamp']
            ])

    file_type = "single" if single_run else "batch"
    print(f"✓ Written {len(data)} records to {file_type} results file")


def scrape_places():
    """Main function to scrape Google Places"""
    # Check for input file
    input_file = Path('input.txt')
    if not input_file.exists():
        print("Error: input.txt not found. Please create input.txt with search queries.")
        print("Format: One query per line (e.g., 'coffee shops in New York')")
        sys.exit(1)

    # Setup CSV files
    single_csv, batch_csv = setup_csv_files()

    # Read queries
    with open(input_file, 'r', encoding='utf-8') as f:
        queries = [line.strip() for line in f if line.strip()]

    if not queries:
        print("Error: input.txt is empty. Please add search queries.")
        sys.exit(1)

    print(f"Found {len(queries)} queries to process")

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        try:
            batch_results = []

            for idx, query in enumerate(queries, 1):
                print(f"\n[{idx}/{len(queries)}] Processing: {query}")

                # Construct Google Maps search URL
                search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

                try:
                    page.goto(search_url, wait_until='networkidle', timeout=30000)
                    time.sleep(3)  # Wait for page to fully load

                    # Extract business data
                    results = extract_business_data(page, query)

                    if results:
                        # Write to single results file (streaming)
                        write_to_csv(results, single_csv, single_run=True)

                        # Collect for batch results
                        batch_results.extend(results)

                        print(f"  ✓ Found {len(results)} businesses")
                    else:
                        print(f"  ✗ No results found")

                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
                    continue

                # Random delay to avoid rate limiting
                time.sleep(5)

            # Write all batch results at the end
            if batch_results:
                write_to_csv(batch_results, batch_csv)

        finally:
            browser.close()

    print(f"\nScraping complete!")
    print(f"- Individual results saved to: {single_csv}")
    print(f"- Batch results saved to: {batch_csv}")


if __name__ == "__main__":
    scrape_places()
