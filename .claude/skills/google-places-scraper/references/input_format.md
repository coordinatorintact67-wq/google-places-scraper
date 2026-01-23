# Input Format for Google Places Scraper

## input.txt Format

Create a file named `input.txt` in the same directory as the scraper script.

Format: **One search query per line**

### Examples:

```
coffee shops in New York
restaurants in Manhattan
pizza places near Times Square
dentist offices within 10 miles of Brooklyn
auto repair shops in Queens
plumbers in Bronx
lawyers in Staten Island
hotels near Central Park
```

### Query Tips:

- Be specific with location (city, neighborhood, or "near [landmark]")
- Include location context ("in", "near", "within X miles of")
- Use natural language as you would search in Google
- One business type + location per line

The scraper will process each line as a separate Google Maps search query.
