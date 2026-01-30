# Quick Start Guide - Google Places Scraper

## ✅ System Status

**Backend Server**: ✅ Running on `http://localhost:5000`  
**Frontend**: ✅ Loaded at `file:///d:/Hamza coding/google places scraper/frontend/index.html`  
**Dependencies**: ✅ Installed

---

## 🚀 How to Use

### Option 1: Single Query

1. **Enter Location**: Type a location (e.g., "New York", "London")
2. **Enter Single Query**: Type one search term (e.g., "restaurants")
3. **Click**: "Start Single Query" button
4. **Monitor**: Watch the status section appear with real-time progress
5. **Download**: Click download button when complete

**Example**:
- Location: `New York`
- Single Query: `restaurants`

---

### Option 2: Multiple Queries (Batch Processing)

1. **Enter Location**: Type a location (e.g., "New York")
2. **Enter Multiple Queries**: Type queries, one per line:
   ```
   restaurants
   coffee shops
   gyms
   hotels
   spas
   ```
3. **Click**: "Start Multiple Queries" button
4. **Monitor**: Queries will be processed **one by one** sequentially
5. **Download**: Each query generates a separate CSV file

**Example**:
- Location: `London`
- Multiple Queries:
  ```
  italian restaurants
  sushi restaurants
  pizza places
  burger joints
  vegan cafes
  ```

---

## 📊 What Happens During Processing

### Sequential Processing Flow:
```
Query 1: restaurants
  ├─ Open browser
  ├─ Search Google Places
  ├─ Extract data (name, rating, phone, etc.)
  ├─ Save to: restaurants_New_York_20260128_204500.csv
  └─ Close browser

Query 2: coffee shops
  ├─ Open browser
  ├─ Search Google Places
  ├─ Extract data
  ├─ Save to: coffee_shops_New_York_20260128_204730.csv
  └─ Close browser

... and so on
```

### Status Updates:
- **Queued**: Job created, waiting to start
- **Processing**: Currently scraping data
- **Completed**: All queries finished successfully
- **Failed**: Error occurred (check error message)

---

## 📁 CSV File Location

All CSV files are saved to:
```
d:\Hamza coding\google places scraper\backend\csv_outputs\
```

**File Naming Format**:
```
{query}_{location}_{timestamp}.csv
```

**Examples**:
- `restaurants_New_York_20260128_204530.csv`
- `coffee_shops_London_20260128_205012.csv`
- `gyms_Tokyo_20260128_210245.csv`

---

## 📋 CSV File Contents

Each CSV file contains these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `name` | Business name | "Joe's Pizza" |
| `rating` | Star rating | "4.5" |
| `total_reviews` | Number of reviews | "1234" |
| `category` | Business type | "Pizza restaurant" |
| `address` | Full address | "123 Main St, New York, NY" |
| `phone` | Phone number | "+1 212-555-0123" |
| `website` | Website URL | "https://joespizza.com" |
| `price_range` | Price level | "$$" |
| `hours_status` | Open/closed status | "Open ⋅ Closes 10 PM" |
| `google_maps_url` | Google Maps link | "https://maps.google.com/..." |

---

## 🎯 Testing Recommendations

### Quick Test (Single Query)
```
Location: New York
Query: pizza
Expected: 1 CSV file with pizza places in New York
Time: ~2-5 minutes
```

### Batch Test (Multiple Queries)
```
Location: New York
Queries:
  pizza
  sushi
  burgers
Expected: 3 separate CSV files
Time: ~6-15 minutes (2-5 min per query)
```

### Large Batch Test (50+ Queries)
```
Location: New York
Queries: (paste 50+ queries, one per line)
Expected: 50+ CSV files processed sequentially
Time: ~2-4 hours
```

---

## 🔍 Monitoring Progress

### Real-Time Status Display:
1. **Status Badge**: Shows current state (queued/processing/completed)
2. **Progress Bar**: Visual progress (e.g., 3/10 queries)
3. **Current Query**: Shows which query is being processed
4. **Results List**: Shows completed queries with download buttons

### Example Status:
```
Status: Processing
Progress: 3/10 queries
Current Query: coffee shops
Results:
  ✅ restaurants - 150 results - Download
  ✅ pizza - 87 results - Download
  ✅ sushi - 62 results - Download
```

---

## 💡 Tips & Best Practices

### 1. **Location Specificity**
- ✅ Good: "Manhattan, New York"
- ✅ Good: "Downtown Los Angeles"
- ⚠️ Okay: "New York"
- ❌ Too broad: "USA"

### 2. **Query Specificity**
- ✅ Good: "italian restaurants"
- ✅ Good: "24 hour gyms"
- ⚠️ Okay: "restaurants"
- ❌ Too vague: "food"

### 3. **Batch Size**
- Small batch (1-10 queries): ~10-50 minutes
- Medium batch (10-30 queries): ~30-150 minutes
- Large batch (50+ queries): ~2-5 hours

### 4. **Browser Behavior**
- Headless mode is enabled (browser runs in background)
- Each query opens/closes browser independently
- No manual intervention needed

### 5. **Error Handling**
- If one query fails, others continue processing
- Failed queries show error message in results
- CSV file still created (may be empty or partial)

---

## 🐛 Troubleshooting

### Issue: "Failed to start scraping"
**Solution**: 
- Check if backend server is running
- Refresh the frontend page
- Check browser console for errors

### Issue: "No results found"
**Solution**:
- Try more specific query terms
- Verify location is correct
- Check if Google has results for that query

### Issue: "ChromeDriver error"
**Solution**:
- Ensure Chrome browser is installed
- Update ChromeDriver to match Chrome version
- Download from: https://chromedriver.chromium.org/

### Issue: "CSV file is empty"
**Solution**:
- Google may have blocked the request (rate limiting)
- Try again after a few minutes
- Check if query/location combination has results

### Issue: "Status not updating"
**Solution**:
- Refresh the page
- Check if backend server is still running
- Look at backend console for errors

---

## 🎨 UI Features

### Input Section
- **Gradient buttons** with hover effects
- **Auto-focus** on input fields
- **Placeholder text** for guidance
- **Validation** for empty inputs

### Status Section
- **Animated progress bar**
- **Real-time updates** every 2 seconds
- **Color-coded status** badges
- **Individual download buttons** per result

### Files Section
- **Grid layout** of all CSV files
- **File metadata** (size, date)
- **Auto-refresh** on job completion
- **Empty state** when no files exist

---

## 📞 Support

### Check Backend Logs
Look at the terminal running `python app.py` for:
- Request logs
- Scraping progress
- Error messages

### Check Browser Console
Press `F12` in browser and check Console tab for:
- API errors
- JavaScript errors
- Network issues

### Common Log Messages
```
✓ Found 20 listings using: a.vwVdIc
✅ Saved to CSV: Joe's Pizza
📊 Current total: 15
✅ Scraping completed!
```

---

## 🚀 Next Steps

1. **Test with single query** to verify everything works
2. **Try batch processing** with 3-5 queries
3. **Scale up** to larger batches as needed
4. **Download and analyze** CSV files
5. **Customize** queries for your specific needs

---

## 📝 Example Use Cases

### Restaurant Research
```
Location: Manhattan, New York
Queries:
  italian restaurants
  french restaurants
  japanese restaurants
  mexican restaurants
  indian restaurants
```

### Fitness Centers
```
Location: Los Angeles
Queries:
  24 hour gyms
  yoga studios
  crossfit gyms
  pilates studios
  boxing gyms
```

### Hotels & Accommodation
```
Location: Paris
Queries:
  luxury hotels
  budget hotels
  boutique hotels
  hostels
  bed and breakfast
```

### Coffee Shops
```
Location: Seattle
Queries:
  coffee shops
  specialty coffee
  coffee roasters
  cafes with wifi
  24 hour coffee
```

---

## ✅ System Ready!

Your Google Places Scraper is now fully operational:
- ✅ Backend running on port 5000
- ✅ Frontend loaded and ready
- ✅ CSV output folder created
- ✅ All dependencies installed

**Start scraping by entering your location and queries in the frontend!**
