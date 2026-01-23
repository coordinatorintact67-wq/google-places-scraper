# Google Maps Scraper Usage Guide

This guide provides instructions for using the enhanced Google Maps scraper skill.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. For the enhanced scraper specifically:
```bash
pip install -r .claude/skills/google-maps-scraper/assets/requirements.txt
playwright install chromium
```

## Single Search Mode

To search for a specific business type in a location:

```bash
python .claude/skills/google-maps-scraper/scripts/enhanced_scraper.py -s="coffee shops in Seattle" -t=50
```

Parameters:
- `-s` or `--search`: The search query (required for single search)
- `-t` or `--total`: Number of results to scrape (default: 20)
- `--headless`: Run browser in headless mode (default: True)
- `--delay_min`: Minimum delay between requests (default: 2)
- `--delay_max`: Maximum delay between requests (default: 5)

## Batch Processing Mode

To process multiple searches from an input file:

1. Create an `input.txt` file with one search query per line:
```
coffee shops in Seattle
restaurants in Boston
dentists in Los Angeles
```

2. Run without the search parameter:
```bash
python .claude/skills/google-maps-scraper/scripts/enhanced_scraper.py -t=30
```

This will process all queries in `input.txt` and save results to separate CSV files.

## Output

Results are saved in timestamped directories under `GMaps Data/`:
```
GMaps Data/
└── 2023-12-01_14-30-45/
    ├── coffee_shops_in_Seattle.csv
    ├── restaurants_in_Boston.csv
    └── scraping_summary.txt
```

Each CSV file contains columns for:
- name: Business name
- address: Business address
- website: Business website
- phone: Phone number
- latitude, longitude: Geographic coordinates
- rating: Average rating
- review_count: Number of reviews
- category: Business category
- operating_hours: Operating hours (if available)
- price_range: Price range indicator
- image_url: URL of business image (if available)

## Enhanced Features

The enhanced scraper includes:

1. **Anti-detection measures**: Browser fingerprinting protection
2. **Smart retry logic**: Automatic recovery from timeouts and errors
3. **Duplicate detection**: Prevents duplicate entries based on name and contact info
4. **Rate limiting**: Configurable delays to avoid being blocked
5. **Data validation**: Cleans and validates extracted data
6. **Robust selectors**: Multiple fallback strategies for element detection
7. **Quality reporting**: Statistics on data completeness

## Best Practices

1. Respect Google's Terms of Service
2. Use reasonable delay settings to avoid being rate-limited
3. Keep searches specific to get better results
4. Monitor for any blocking or CAPTCHA challenges
5. Check the output quality reports to assess data completeness

## Troubleshooting

Common issues and solutions:

- **Element not found errors**: The enhanced scraper has multiple selector strategies to handle this
- **Rate limiting**: Increase delay values with `--delay_min` and `--delay_max`
- **Browser crashes**: Reduce concurrent operations (the current implementation is single-threaded)
- **Incomplete data**: Check the quality report to see which fields are missing

## Legal Notice

This tool is for educational purposes only. Always comply with Google's Terms of Service and applicable laws regarding web scraping. Respect robots.txt files and rate limits.