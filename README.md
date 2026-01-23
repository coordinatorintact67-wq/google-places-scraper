# Google Places Scraper

Scrape business information from Google Maps/Places with Playwright automation.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Search Queries

Edit `input.txt` and add your search queries (one per line):

```
coffee shops in New York
restaurants in Manhattan
pizza places near Times Square
```

Example queries:
- `coffee shops in New York City`
- `restaurants in Brooklyn`
- `pizza places near Times Square`
- `dentist offices within 10 miles of Brooklyn`

### 3. Run the Scraper

**Option 1 - Using the runner script:**
```bash
python run_scraper.py
```

**Option 2 - Direct execution:**
```bash
python scrape_places.py
```

### 4. View Results

Two CSV files will be created:
- `google_places_single_results.csv` - Results from individual searches (streaming)
- `google_places_batch_results.csv` - All results combined

## Extracted Data

For each business:
- Business Name
- Address
- Phone Number
- Rating (out of 5 stars)
- Review Count
- Business Hours
- Website URL
- Category
- Search Query (for reference)
- Timestamp

## Features

✓ Streaming CSV output (writes in real-time)
✓ Dual output files (single & batch)
✓ Rate limiting to avoid detection
✓ Error handling and recovery
✓ Extracts all available business details
✓ Batch processing from file
✓ Headless browser (runs in background)

## Troubleshooting

**Playwright not found:**
```bash
pip install playwright
playwright install chromium
```

**No input.txt:** Create the file with search queries

**No results:** Make queries more specific or check internet connection

## Requirements

- Python 3.7+
- Playwright
- Chromium browser (auto-installed with `playwright install chromium`)
- Internet connection
- Windows/Linux/macOS

## Files

- `scrape_places.py` - Main scraper script
- `run_scraper.py` - Helper script with dependency checks
- `input.txt` - Search queries (one per line)
- `requirements.txt` - Python dependencies
- `google_places_single_results.csv` - Output file (streaming)
- `google_places_batch_results.csv` - Output file (batch)

## Usage Example

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Add queries to input.txt
echo "coffee shops in New York" > input.txt
echo "restaurants in Manhattan" >> input.txt

# 3. Run scraper
python run_scraper.py

# 4. View results
cat google_places_batch_results.csv
```

## Note

This scraper is designed for legitimate data collection purposes. Please respect Google's Terms of Service and avoid aggressive scraping that could get your IP blocked.

## Advanced Usage

To modify the scraper:
- Change number of results: Edit `min(count, 20)` in `scrape_places.py`
- Adjust delays: Change `time.sleep()` values
- Add more fields: Modify `extract_business_data()` function

## License

Use at your own risk for educational and legitimate business purposes.
