import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(os.getcwd()) / 'backend'))

from scraper import scrape_google_search

print("Starting minimal scraper test...")
fieldnames = ['name', 'rating', 'total_reviews', 'category', 'address', 'phone', 'website', 'price_range', 'hours_status', 'google_maps_url']
results = scrape_google_search("test bakery", "London", "test_output.csv", fieldnames)

print(f"\nTest finished! Found {len(results)} results.")
if len(results) > 0:
    print(f"Sample: {results[0]['name']}")
else:
    print("No results found.")
