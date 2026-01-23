---
name: google-places-scraper
description: Comprehensive Google Places scraper using Playwright for browser automation. Extracts business information including names, addresses, phone numbers, ratings, review counts, business hours, and website URLs. Supports batch processing from input file and saves to CSV files in streaming fashion. Use when you need to scrape Google Maps/Places data for multiple business types and locations.
---

# Google Places Scraper

This skill scrapes business information from Google Maps/Places using Playwright browser automation.

## Quick Start

1. Install Playwright:
```bash
pip install playwright
playwright install chromium
```

2. Create `input.txt` with search queries (one per line):
```
coffee shops in New York
restaurants in Manhattan
pizza places near Times Square
```

3. Run the scraper:
```bash
python scripts/scrape_places.py
```

4. View results:
- `google_places_single_results.csv` - Results from individual searches
- `google_places_batch_results.csv` - All results combined

## What Gets Extracted

For each business found:
- **Business Name**
- **Address**
- **Phone Number**
- **Rating** (stars out of 5)
- **Review Count**
- **Business Hours**
- **Website URL**
- **Category/Type**
- **Search Query** (for reference)
- **Timestamp** (when scraped)

## Input Format

Create `input.txt` in the project root directory:

```
coffee shops in New York City
restaurants in Brooklyn
plumbers within 5 miles of Queens
dentist offices near Manhattan
```

See [references/input_format.md](references/input_format.md) for detailed examples and tips.

## Output Files

The scraper creates two CSV files:

### 1. google_places_single_results.csv
- Contains results grouped by individual search queries
- Updated streaming-style as each query completes
- Good for tracking progress

### 2. google_places_batch_results.csv
- Contains all results from entire batch
- Written after all queries complete
- Good for consolidated analysis

Both files have identical formats with columns:
```csv
search_query,business_name,address,phone,rating,review_count,business_hours,website,category,timestamp
```

## Features

- **Streaming output** - Writes to CSV files in real-time
- **Dual output** - Separate files for single and batch results
- **Rate limiting** - Built-in delays to avoid detection
- **Error handling** - Continues on errors, logs issues
- **Headless browser** - Runs in background without GUI
- **Retry logic** - Handles temporary issues automatically

## Troubleshooting

### Playwright not installed
```bash
pip install playwright
playwright install chromium
```

### No input.txt found
Create `input.txt` with your search queries (one per line).

### Empty results
- Check your queries are specific enough
- Try simpler queries first
- Ensure internet connection is stable
- Google may have rate-limited you (wait and retry)

### Browser crashes
- Increase `timeout` values in the script
- Reduce number of concurrent operations
- Check system resources

## Modifying the Scraper

To adjust:
- **Number of results per query**: Edit `min(count, 20)` in `scrape_places.py`
- **Delay between queries**: Change `time.sleep(5)` value
- **Timeout settings**: Modify `page.goto()` and `page.wait_for_selector()` timeouts

## Important Notes

- Respects Google's terms of service limits
- Uses realistic delays to avoid rate limiting
- Creates new browser context for clean sessions
- Handles JavaScript-rendered content dynamically
