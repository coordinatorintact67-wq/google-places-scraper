# Google Places Scraper - FastAPI Backend

A powerful web scraper for extracting business data from Google Places, now powered by FastAPI.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
# Option 1: Using uvicorn directly
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python server.py
```

### 3. Open the Frontend

Simply open `frontend/index.html` in your browser, or use a local server:

```bash
cd frontend
python -m http.server 3000
```

Then visit: `http://localhost:3000`

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🎯 Features

- ✅ **FastAPI Backend** - Modern, fast, and type-safe
- ✅ **Automatic API Docs** - Interactive documentation at `/docs`
- ✅ **Background Jobs** - Non-blocking scraping with status tracking
- ✅ **Multiple Queries** - Process multiple search queries in one job
- ✅ **CSV Export** - Download results as CSV files
- ✅ **Error Handling** - Comprehensive error handling and user feedback
- ✅ **CORS Enabled** - Works with any frontend

## 📡 API Endpoints

### Start Scraping Job
```http
POST /api/scrape
Content-Type: application/json

{
  "queries": ["restaurants", "coffee shops"],
  "location": "New York"
}
```

### Check Job Status
```http
GET /api/status/{job_id}
```

### List CSV Files
```http
GET /api/files
```

### Download CSV
```http
GET /api/download/{filename}
```

### Health Check
```http
GET /health
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Uvicorn, Pydantic
- **Scraping**: Selenium WebDriver
- **Frontend**: Vanilla HTML/CSS/JavaScript

## ⚠️ Error Handling

The frontend automatically detects if the backend is not running and displays helpful error messages:

- Connection errors show instructions to start the server
- Network failures during scraping are handled gracefully
- Status polling stops if backend becomes unreachable

## 📝 Notes

- The server runs on port **8000** by default
- CSV files are saved in `backend/csv_outputs/`
- Job status is stored in memory (use Redis/Database for production)

## 🔧 Development

To run in development mode with auto-reload:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## 📄 License

This project is for educational purposes.
