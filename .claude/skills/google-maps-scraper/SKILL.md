---
name: google-maps-scraper
description: Comprehensive Google Maps business listing scraper with enhanced library code for improved performance. Use when Claude needs to extract business data (names, addresses, websites, phone numbers, ratings) from Google Maps. Handles single searches, batch processing, data export, and duplicate detection with optimized Playwright automation.
---

# Google Maps Scraper Skill

Enhanced Google Maps business listing scraper with improved performance and reliability. This skill provides comprehensive tools for extracting business data from Google Maps with optimized library code.

## Quick Start

For basic scraping:
```
python3 main.py -s="coffee shops in Seattle" -t=50
```

For batch processing:
```
python3 main.py -t=30  # Uses input.txt for multiple searches
```

## Core Functionality

### 1. Business Data Extraction
- Business name, address, phone, website
- Ratings and reviews data
- Geographic coordinates
- Operating hours and additional details

### 2. Enhanced Library Improvements
- Optimized Playwright automation with better error handling
- Improved rate limiting to avoid detection
- Enhanced data validation and cleaning
- Better duplicate detection algorithms
- More robust element selectors for dynamic Google Maps interface

### 3. Batch Processing
- Process multiple search queries from input.txt
- Configurable limits per search term
- Automatic retry mechanisms for failed attempts
- Progress tracking and logging

### 4. Data Export
- Export to CSV format with timestamped directories
- Customizable field selection
- Data deduplication before export
- Error reporting and validation

## Enhanced Library Features

### Rate Limiting & Anti-Detection
```python
# Built-in delays and randomization
import random
import time

def random_delay(min_seconds=1, max_seconds=3):
    time.sleep(random.uniform(min_seconds, max_seconds))
```

### Robust Element Detection
- Dynamic selector fallbacks
- Wait strategies for dynamic content
- Error recovery for missing elements
- Session persistence handling

### Data Validation Pipeline
- Real-time validation of extracted data
- Format standardization
- Quality scoring for results
- Automated cleanup of malformed entries

## Usage Examples

### Single Search with Custom Parameters
```
# Scrape 50 coffee shops in Seattle
python3 main.py -s="coffee shops in Seattle" -t=50

# Scrape with custom delay settings
python3 main.py -s="restaurants in New York" -t=100 --delay_min=2 --delay_max=5
```

### Batch Processing
Create an `input.txt` file with one search query per line:
```
dentists in Boston, MA
pizza restaurants in Chicago
car repair in Los Angeles
gyms in Miami
```

Then run without search parameter to process all queries:
```
python3 main.py -t=30
```

### Output Structure
Results are saved to:
```
GMaps Data/
└── YYYY-MM-DD_HH-MM-SS/
    ├── search_term_1.csv
    ├── search_term_2.csv
    └── scraping_log.txt
```

## Best Practices

1. **Respect Rate Limits**: Use appropriate delays to avoid being blocked
2. **Granular Queries**: Use specific search terms for better results
3. **Monitor Limits**: Google shows ~120 results per search, plan accordingly
4. **Check ToS**: Always comply with Google's Terms of Service
5. **Handle Failures**: Implement retry logic for network issues

## Troubleshooting

### Common Issues
- **Element not found**: Updated selectors in enhanced library handle this
- **Rate limited**: Built-in exponential backoff reduces occurrence
- **Incomplete data**: Validation pipeline catches and handles missing fields
- **Timeout errors**: Adjustable timeout settings in configuration

### Recovery Strategies
- Automatic retries with increasing delays
- Session state preservation
- Partial result saving during failures
- Detailed logging for debugging

## Configuration Options

### Command Line Parameters
- `-s`: Search query (e.g., "coffee shops in Seattle")
- `-t`: Total results to scrape
- `--delay_min`: Minimum delay between requests
- `--delay_max`: Maximum delay between requests
- `--headless`: Run browser in headless mode (true/false)

### Input File Format
- One search query per line in input.txt
- Format: "business type in location" (e.g., "dentists in Boston, MA")
- Comments supported with # prefix

## Advanced Features

### Smart Filtering
- Location-based filtering
- Rating thresholds
- Business type categorization
- Open now verification

### Data Enrichment
- Contact information validation
- Social media links extraction
- Additional business attributes
- Image URLs collection

## Performance Optimization

### Concurrency Controls
- Configurable concurrent requests
- Memory usage optimization
- Connection pooling
- Resource cleanup

### Error Resilience
- Graceful degradation on failures
- Automatic recovery mechanisms
- State checkpointing
- Progress persistence