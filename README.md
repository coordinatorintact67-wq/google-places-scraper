# Google Places Scraper - Full Stack Application

A professional web application for scraping business data from Google Places with a modern frontend and stateless backend API.

## 🌟 Features

- **Single Query Processing**: Scrape data for one search query at a time
- **Batch Processing**: Process multiple queries sequentially (one by one)
- **Stateless Backend**: Each request is independent and processed separately
- **Real-time Status Updates**: Monitor scraping progress in real-time
- **CSV Export**: Automatic CSV file generation for each query
- **File Management**: Download and manage generated CSV files
- **Modern UI**: Beautiful, responsive interface with dark theme and animations

## 📁 Project Structure

```
google places scraper/
├── backend/
│   ├── app.py              # Flask API server
│   ├── scraper.py          # Scraping logic
│   ├── requirements.txt    # Python dependencies
│   └── csv_outputs/        # Generated CSV files (auto-created)
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── styles.css          # Styling
│   └── script.js           # Frontend logic
└── test.py                 # Original scraper (standalone)
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd "d:\Hamza coding\google places scraper\backend"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server**:
   ```bash
   python app.py
   ```

   The backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd "d:\Hamza coding\google places scraper\frontend"
   ```

2. **Open in browser**:
   - Simply open `index.html` in your web browser
   - Or use a local server:
     ```bash
     python -m http.server 8000
     ```
   - Then visit `http://localhost:8000`

## 📖 How to Use

### Single Query Mode

1. Enter a location (e.g., "New York")
2. Enter a single search query (e.g., "restaurants")
3. Click "Start Single Query"
4. Monitor the progress in the status section
5. Download the CSV file when complete

### Multiple Queries Mode

1. Enter a location (e.g., "New York")
2. Enter multiple queries (one per line):
   ```
   restaurants
   coffee shops
   gyms
   hotels
   ```
3. Click "Start Multiple Queries"
4. The system will process each query **one by one**
5. Download individual CSV files as they complete

## 🔧 API Endpoints

### POST `/api/scrape`
Start a scraping job

**Request Body**:
```json
{
  "queries": ["restaurants", "coffee shops"],
  "location": "New York"
}
```

**Response**:
```json
{
  "job_id": "uuid-here",
  "message": "Scraping started",
  "total_queries": 2
}
```

### GET `/api/status/<job_id>`
Get job status

**Response**:
```json
{
  "job_id": "uuid-here",
  "status": "processing",
  "total_queries": 2,
  "completed_queries": 1,
  "current_query": "coffee shops",
  "results": [
    {
      "query": "restaurants",
      "csv_file": "restaurants_New_York_20260128_203000.csv",
      "total_results": 150,
      "completed_at": "2026-01-28T20:30:00"
    }
  ]
}
```

### GET `/api/download/<filename>`
Download a CSV file

### GET `/api/files`
List all generated CSV files

## 📊 CSV Output Format

Each CSV file contains the following columns:

- `name` - Business name
- `rating` - Star rating
- `total_reviews` - Number of reviews
- `category` - Business category
- `address` - Full address
- `phone` - Phone number
- `website` - Website URL
- `price_range` - Price range ($, $$, $$$, $$$$)
- `hours_status` - Current open/closed status
- `google_maps_url` - Google Maps URL

## ⚙️ Configuration

### Backend Configuration

Edit `backend/app.py`:

```python
# CSV output directory
CSV_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'csv_outputs')

# Server settings
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Scraper Configuration

Edit `backend/scraper.py`:

```python
# Chrome options
option.add_argument("--headless")  # Run in headless mode
option.add_argument("--start-maximized")

# Pagination limit
max_pages = 100  # Maximum pages to scrape per query
```

### Frontend Configuration

Edit `frontend/script.js`:

```javascript
// API base URL
const API_BASE_URL = 'http://localhost:5000';

// Status polling interval (milliseconds)
statusCheckInterval = setInterval(checkStatus, 2000);
```

## 🔍 How It Works

1. **User submits queries** through the frontend
2. **Backend creates a job** with unique ID
3. **Scraper processes queries** one by one:
   - Opens Chrome browser
   - Searches Google Places
   - Extracts business data
   - Saves to CSV file
   - Closes browser
4. **Frontend polls status** every 2 seconds
5. **User downloads CSV files** when complete

## 🎯 Key Features Explained

### Stateless Processing
- Each query is processed independently
- No session state maintained between requests
- Browser opens and closes for each query
- Safe for concurrent users (in production, use job queue)

### Sequential Processing
- Queries are processed **one by one**, not in parallel
- Ensures stable scraping and avoids rate limits
- Each query gets its own CSV file
- Progress tracked individually

### CSV File Naming
Format: `{query}_{location}_{timestamp}.csv`

Example: `restaurants_New_York_20260128_203000.csv`

## 🐛 Troubleshooting

### ChromeDriver Issues
- Ensure ChromeDriver version matches your Chrome browser
- Download from: https://chromedriver.chromium.org/

### CORS Errors
- Backend uses `flask-cors` to allow cross-origin requests
- Ensure backend is running on port 5000

### Scraping Fails
- Check if Google has changed their HTML structure
- Update CSS selectors in `scraper.py`
- Disable headless mode for debugging

### Port Already in Use
```bash
# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 📝 Notes

- **Rate Limiting**: Google may block excessive requests. Use delays between queries.
- **Headless Mode**: Enabled by default. Disable for debugging.
- **Data Accuracy**: Scraped data depends on Google's HTML structure.
- **Legal**: Ensure compliance with Google's Terms of Service.

## 🚀 Future Enhancements

- [ ] Add authentication
- [ ] Implement job queue (Redis/Celery)
- [ ] Add filters (rating, reviews, etc.)
- [ ] Export to JSON/Excel
- [ ] Scheduled scraping
- [ ] Email notifications
- [ ] Database storage
- [ ] API rate limiting

## 📄 License

This project is for educational purposes only.

## 👨‍💻 Author

Created for efficient Google Places data extraction.
