from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import csv
from datetime import datetime
import threading
import uuid
from scraper import scrape_google_search
from pathlib import Path
import json
import time
import zipfile
import io

app = FastAPI(title="Google Places Scraper API")

print("\n" + "#"*50)
print("### VERSION 3.0 - DOWNLOAD-ALL ROUTE INCLUDED ###")
print("#"*50 + "\n")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Robust Path Configuration
BACKEND_DIR = Path(__file__).parent.absolute()
ROOT_DIR = BACKEND_DIR.parent
CSV_OUTPUT_DIR = ROOT_DIR / 'csv_outputs'
JOBS_FILE = ROOT_DIR / 'jobs.json'
STATE_FILE = ROOT_DIR / 'backend_state.json'

os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)

# Global State
job_status = {}
running_threads = {}  # Track running threads
termination_flags = {}  # Track jobs marked for termination
thread_drivers = {}  # Track WebDriver instances for each thread

def load_backend_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_backend_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Error saving backend state: {e}")

backend_state = load_backend_state()
last_created_job_id = backend_state.get('last_job_id')

def load_jobs():
    global job_status
    if JOBS_FILE.exists():
        try:
            with open(JOBS_FILE, 'r') as f:
                jobs = json.load(f)
                # Cleanup: mark any interrupted jobs as failed on startup
                for jid in jobs:
                    if jobs[jid].get('status') in ['processing', 'queued']:
                        jobs[jid]['status'] = 'failed'
                        jobs[jid]['error'] = 'Server restarted while job was active'
                job_status = jobs
                return jobs
        except Exception as e:
            print(f"Error loading jobs.json: {e}")
            return {}
    return {}

def save_jobs():
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump(job_status, f, indent=2)
        print(f"Successfully saved {len(job_status)} jobs to {JOBS_FILE}")
    except Exception as e:
        print(f"CRITICAL: Failed to save jobs.json: {e}")

# Initial Load
job_status = load_jobs()

# If we don't have a persisted last_job_id, initialize it from the most recent job in job_status
if not last_created_job_id and job_status:
    sorted_jobs = sorted(
        job_status.values(), 
        key=lambda x: x.get('created_at', ''), 
        reverse=True
    )
    if sorted_jobs:
        last_created_job_id = sorted_jobs[0].get('job_id')
        save_backend_state({'last_job_id': last_created_job_id})

print(f"Backend Initialized with {len(job_status)} jobs. Last job: {last_created_job_id}")

# Pydantic Models
class ScrapeRequest(BaseModel):
    queries: List[str]
    location: str = ""

class JobResponse(BaseModel):
    job_id: str
    message: str
    total_queries: int

class QueryResult(BaseModel):
    query: str
    csv_file: Optional[str] = None
    total_results: Optional[int] = None
    error: Optional[str] = None
    completed_at: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    total_queries: int
    completed_queries: int
    queries: List[str]
    location: str
    results: List[QueryResult]
    created_at: str
    started_at: Optional[str] = None
    current_query: Optional[str] = None
    current_query_index: Optional[int] = None
    current_csv_file: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

class FileInfo(BaseModel):
    filename: str
    size: int
    created: str
    completed: str
    status: str = "complete"

class HealthResponse(BaseModel):
    status: str

@app.get("/api/test-route")
async def test_route():
    return {"message": "Server is running the LATEST code version 3.0"}

@app.get("/api/download-all-csv")
async def download_all_merged_csv():
    """Download all results merged into a single CSV file"""
    print("DEBUG: download_all_merged_csv route triggered")
    try:
        # Get list of files currently being processed
        active_files = set()
        for job in job_status.values():
            if job.get('status') in ['processing', 'queued']:
                if job.get('current_csv_file'):
                    active_files.add(job.get('current_csv_file'))

        output = io.StringIO()
        fieldnames = ['name', 'rating', 'total_reviews', 'category', 'address',
                     'phone', 'website', 'price_range', 'hours_status', 'google_maps_url']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        files_added = 0
        for filename in os.listdir(CSV_OUTPUT_DIR):
            if filename.endswith('.csv') and filename not in active_files and not filename.endswith('_EMPTY.csv'):
                filepath = os.path.join(CSV_OUTPUT_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            writer.writerow(row)
                    files_added += 1
                except Exception as fe:
                    print(f"Error reading {filename}: {fe}")

        if files_added == 0:
            raise HTTPException(status_code=404, detail="No data available to merge. Generate some results first!")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=merged_results_{timestamp}.csv"}
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error merging CSVs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API Routes

@app.get("/api/active-job")
async def get_active_job():
    """Find the most recent active job, or the latest created job if it hasn't been cleared"""
    print(f"DEBUG: /api/active-job called. last_id: {last_created_job_id}")
    try:
        # 1. Look for a currently active job first (processing, queued, or terminating)
        for jid in job_status:
            job = job_status[jid]
            if job.get('status') in ['processing', 'queued', 'terminating']:
                return job
                
        # 2. If no active job, ONLY return the latest job ever created
        # but only if it exists in job_status (meaning it hasn't been cleared)
        if last_created_job_id and last_created_job_id in job_status:
            return job_status[last_created_job_id]
            
        return None
    except Exception as e:
        print(f"Error getting active job: {e}")
        return None

def process_multiple_queries(job_id: str, queries: List[str], location: str):
    """Process multiple queries one by one"""
    try:
        for idx, query in enumerate(queries):
            # Check if termination was requested for this job
            if termination_flags.get(job_id):
                print(f"Job {job_id} was terminated by user request")
                job_status[job_id]['status'] = 'terminated'
                job_status[job_id]['error'] = 'Job terminated by user'
                job_status[job_id]['completed_at'] = datetime.now().isoformat()
                job_status[job_id]['current_query'] = None
                job_status[job_id]['current_query_index'] = None
                save_jobs()
                return  # Exit the function early

            try:
                # Update status
                job_status[job_id]['status'] = 'processing'
                job_status[job_id]['current_query'] = query
                job_status[job_id]['current_query_index'] = idx + 1

                # Create CSV file with incremental numbering if file exists and use readable format with spaces
                # Clean the query and location strings to make them more readable
                # Replace non-alphanumeric characters with spaces for readability
                safe_query = "".join([c if c.isalnum() else " " for c in query.strip()])
                safe_location = "".join([c if c.isalnum() else " " for c in location.strip()])

                # Clean up multiple spaces and strip whitespace
                safe_query = " ".join(safe_query.split()).strip()
                safe_location = " ".join(safe_location.split()).strip()

                # Create base filename using spaces between words as requested
                base_parts = []
                if safe_query:
                    base_parts.append(safe_query)
                if safe_location:
                    base_parts.append(safe_location)

                base_filename = " ".join(base_parts).strip()

                # Find the next available number for this filename
                counter = 1
                csv_filename = f"{base_filename} {counter}.csv"
                csv_filepath = os.path.join(CSV_OUTPUT_DIR, csv_filename)

                while os.path.exists(csv_filepath):
                    counter += 1
                    csv_filename = f"{base_filename} {counter}.csv"
                    csv_filepath = os.path.join(CSV_OUTPUT_DIR, csv_filename)

                # IMPORTANT: Set active CSV file for frontend tracking
                job_status[job_id]['current_csv_file'] = csv_filename
                save_jobs()

                # Initialize CSV
                fieldnames = ['name', 'rating', 'total_reviews', 'category', 'address',
                             'phone', 'website', 'price_range', 'hours_status', 'google_maps_url', 'search_location']

                with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                
                # Mark the START TIME using access time (atime)
                # This ensures list_files can distinguish start from finish
                start_time = time.time()
                os.utime(csv_filepath, (start_time, start_time))

                # Scrape data
                print(f"DEBUG: Calling scraper for query: '{query.strip()}' in location: '{location}'")
                all_data = scrape_google_search(
                    search_query=query.strip(),
                    location=location,
                    csv_filepath=csv_filepath,
                    fieldnames=fieldnames,
                    termination_flag=lambda: termination_flags.get(job_id, False),
                    job_id=job_id,
                    thread_drivers=thread_drivers
                )

                if all_data is None:
                    all_data = []

                if not all_data:
                    # If no results found, tag the file as NO_RESULTS
                    # First, get the base filename without the counter
                    # For space-separated format: "barber in USA 1.csv" -> "barber in USA"
                    parts = csv_filename.rsplit(' ', 1)  # Split on the last space
                    if len(parts) > 1 and parts[1].replace('.csv', '').isdigit():
                        base_part = parts[0]  # "barber in USA"
                    else:
                        base_part = csv_filename.replace('.csv', '')  # Fallback

                    new_filename = f"{base_part} EMPTY.csv"

                    # If that name already exists, find the next available number
                    counter = 1
                    final_filename = new_filename
                    final_filepath = os.path.join(CSV_OUTPUT_DIR, final_filename)

                    while os.path.exists(final_filepath):
                        final_filename = f"{base_part} EMPTY {counter}.csv"
                        final_filepath = os.path.join(CSV_OUTPUT_DIR, final_filename)
                        counter += 1

                    try:
                        if os.path.exists(csv_filepath):
                            os.rename(csv_filepath, final_filepath)
                            csv_filename = final_filename
                    except Exception as re:
                        print(f"Error renaming empty CSV: {re}")
                        # If rename fails, keep the original filename
                        pass

                # Check again if termination was requested before saving results
                if termination_flags.get(job_id):
                    print(f"Job {job_id} was terminated by user request")
                    job_status[job_id]['status'] = 'terminated'
                    job_status[job_id]['error'] = 'Job terminated by user'
                    job_status[job_id]['completed_at'] = datetime.now().isoformat()
                    job_status[job_id]['current_query'] = None
                    job_status[job_id]['current_query_index'] = None
                    save_jobs()
                    return  # Exit the function early

                # Clear active CSV file and store result
                job_status[job_id]['current_csv_file'] = None
                result = {
                    'query': query,
                    'csv_file': csv_filename,
                    'total_results': len(all_data),
                    'completed_at': datetime.now().isoformat()
                }
                job_status[job_id]['results'].append(result)
                job_status[job_id]['completed_queries'] = idx + 1
                save_jobs()

                # Small delay between queries to avoid rate limiting
                # Check termination flag during the delay
                for _ in range(2):
                    if termination_flags.get(job_id):
                        print(f"Job {job_id} was terminated during delay between queries")
                        job_status[job_id]['status'] = 'terminated'
                        job_status[job_id]['error'] = 'Job terminated by user'
                        job_status[job_id]['completed_at'] = datetime.now().isoformat()
                        job_status[job_id]['current_query'] = None
                        job_status[job_id]['current_query_index'] = None
                        save_jobs()
                        return  # Exit the function early
                    time.sleep(1)

            except Exception as e:
                print(f"❌ Error processing query '{query}': {str(e)}")
                # Check termination flag before storing error
                if termination_flags.get(job_id):
                    print(f"Job {job_id} was terminated during error handling for query '{query}'")
                    job_status[job_id]['status'] = 'terminated'
                    job_status[job_id]['error'] = 'Job terminated by user'
                    job_status[job_id]['completed_at'] = datetime.now().isoformat()
                    job_status[job_id]['current_query'] = None
                    job_status[job_id]['current_query_index'] = None
                    save_jobs()
                    return  # Exit the function early
                # Store error but continue
                result = {
                    'query': query,
                    'error': str(e),
                    'csv_file': None,
                    'completed_at': datetime.now().isoformat()
                }
                job_status[job_id]['results'].append(result)
                job_status[job_id]['completed_queries'] = idx + 1
                save_jobs()

        # Mark job as completed (only if not terminated)
        if not termination_flags.get(job_id):
            job_status[job_id]['status'] = 'completed'
            job_status[job_id]['completed_at'] = datetime.now().isoformat()
            job_status[job_id]['current_query'] = None
            job_status[job_id]['current_query_index'] = None
            save_jobs()
    except Exception as e:
        print(f"🔥 Critical failure in background job {job_id}: {str(e)}")
        job_status[job_id]['status'] = 'failed'
        job_status[job_id]['error'] = str(e)
        save_jobs()
    finally:
        # Clean up the termination flag and thread tracking when job finishes
        if job_id in termination_flags:
            del termination_flags[job_id]
        if job_id in running_threads:
            del running_threads[job_id]
        if job_id in thread_drivers:
            # Close the driver if it's still active
            try:
                driver = thread_drivers[job_id]
                driver.quit()
                print(f"Closing driver for job {job_id} in finally block")
            except Exception as e:
                print(f"Error closing driver for job {job_id} in finally: {e}")
            finally:
                del thread_drivers[job_id]
        # Ensure job status is properly saved when the process ends
        if job_id in job_status and job_status[job_id]['status'] in ['processing', 'queued', 'terminating']:
            # If the job was still processing when the function ended, it was likely terminated
            if termination_flags.get(job_id, False):
                job_status[job_id]['status'] = 'terminated'
                if not job_status[job_id].get('error'):
                    job_status[job_id]['error'] = 'Job terminated by user'
                job_status[job_id]['completed_at'] = datetime.now().isoformat()
            elif job_status[job_id]['status'] != 'completed':
                job_status[job_id]['status'] = 'failed'
                if not job_status[job_id].get('error'):
                    job_status[job_id]['error'] = 'Job failed unexpectedly'
            save_jobs()

@app.post("/api/scrape", response_model=JobResponse, status_code=202)
async def scrape(request: ScrapeRequest):
    try:
        if not request.queries:
            raise HTTPException(status_code=400, detail="No queries provided")

        job_id = str(uuid.uuid4())
        
        # Update last_created_job_id persistently
        global last_created_job_id
        last_created_job_id = job_id
        save_backend_state({'last_job_id': last_created_job_id})

        job_status[job_id] = {
            'job_id': job_id,
            'status': 'queued',
            'total_queries': len(request.queries),
            'completed_queries': 0,
            'queries': request.queries,
            'location': request.location,
            'results': [],
            'created_at': datetime.now().isoformat(),
            'started_at': datetime.now().isoformat()
        }
        save_jobs()

        thread = threading.Thread(
            target=process_multiple_queries,
            args=(job_id, request.queries, request.location)
        )
        thread.daemon = True
        thread.start()

        # Track the running thread
        running_threads[job_id] = thread

        return JobResponse(
            job_id=job_id,
            message="Scraping started",
            total_queries=len(request.queries)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/terminate/{job_id}")
async def terminate_job(job_id: str):
    """Mark a job for termination"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    # Mark the job for termination
    termination_flags[job_id] = True

    # Close any active browser driver for this job
    if job_id in thread_drivers:
        try:
            driver = thread_drivers[job_id]
            driver.quit()
            print(f"Closed browser driver for job {job_id}")
            del thread_drivers[job_id]
        except Exception as e:
            print(f"Error closing driver for job {job_id}: {e}")

    # Update job status to indicate termination in progress
    if job_status[job_id]['status'] in ['queued', 'processing', 'terminating']:
        job_status[job_id]['status'] = 'terminating'
        # Clear current query info since we're terminating
        job_status[job_id]['current_query'] = None
        job_status[job_id]['current_query_index'] = None
        # Important: Sync global state
        save_jobs()

    return {"message": "Job termination requested", "job_id": job_id}


@app.get("/api/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if the job has been marked for termination and is currently running
    if (job_id in termination_flags and termination_flags[job_id] and
        job_status[job_id]['status'] in ['processing', 'queued']):
        # If termination was requested but status hasn't been updated yet,
        # return the status with 'terminating' to reflect the current state
        current_status = job_status[job_id].copy()
        if current_status['status'] in ['processing', 'queued']:
            current_status['status'] = 'terminating'
        return current_status

    return job_status[job_id]



@app.get("/api/download/{filename}")
async def download_csv(filename: str):
    try:
        filepath = os.path.join(CSV_OUTPUT_DIR, filename)
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(path=filepath, media_type='text/csv', filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files", response_model=List[FileInfo])
async def list_files():
    try:
        files = []
        if not os.path.exists(CSV_OUTPUT_DIR): return []
            
        active_files = []
        for job in job_status.values():
            if job.get('status') in ['processing', 'queued']:
                if job.get('current_csv_file'):
                    active_files.append(job.get('current_csv_file'))
                    
        for filename in os.listdir(CSV_OUTPUT_DIR):
            if filename.endswith('.csv'):
                filepath = os.path.join(CSV_OUTPUT_DIR, filename)
                stat = os.stat(filepath)
                status = "processing" if filename in active_files else "complete"

                files.append(FileInfo(
                    filename=filename,
                    size=stat.st_size,
                    created=datetime.fromtimestamp(stat.st_ctime).isoformat(),  # Use CTIME for Creation/Start
                    completed=datetime.fromtimestamp(stat.st_mtime).isoformat(), # Use MTIME for Completion/Last Modified
                    status=status
                ))

        # Sort files by creation/modification time (newest first)
        files.sort(key=lambda x: x.created, reverse=True)

        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/delete/{filename}")
async def delete_file(filename: str):
    try:
        filepath = os.path.join(CSV_OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"message": "Deleted"}
        raise HTTPException(status_code=404, detail="Not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/clear-status/{job_id}")
async def clear_job_status(job_id: str):
    """Clear job status from the server - this doesn't terminate the job, just removes it from active tracking"""
    global last_created_job_id
    
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    # If the job being cleared is the last_created_job_id, clear that too
    if job_id == last_created_job_id:
        print(f"DEBUG: Clearing last_created_job_id: {job_id}")
        last_created_job_id = None
        save_backend_state({'last_job_id': None})

    # Remove the job from active tracking
    del job_status[job_id]

    # Also remove from the JSON file to prevent reloading on refresh
    if JOBS_FILE.exists():
        try:
            with open(JOBS_FILE, 'r') as f:
                jobs = json.load(f)

            # Remove the specific job
            if job_id in jobs:
                del jobs[job_id]

            # Save the updated jobs back to file
            with open(JOBS_FILE, 'w') as f:
                json.dump(jobs, f, indent=2)

        except Exception as e:
            print(f"Error updating jobs.json: {e}")
            # Continue anyway, as the in-memory removal worked

    return {"message": "Job status cleared", "job_id": job_id}


@app.get("/api/download-all")
async def download_all_zip():
    """Download all CSV files as a ZIP archive"""
    try:
        # Get list of files currently being processed
        active_files = set()
        for job in job_status.values():
            if job.get('status') in ['processing', 'queued']:
                if job.get('current_csv_file'):
                    active_files.add(job.get('current_csv_file'))

        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            files_added = 0
            for filename in os.listdir(CSV_OUTPUT_DIR):
                if filename.endswith('.csv') and filename not in active_files:
                    filepath = os.path.join(CSV_OUTPUT_DIR, filename)
                    zip_file.write(filepath, filename)
                    files_added += 1
        
        if files_added == 0:
            raise HTTPException(status_code=404, detail="No files to download")

        zip_buffer.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": f"attachment; filename=all_results_{timestamp}.zip"}
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        print(f"Error creating zip: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@app.delete("/api/delete-all-csv")
async def delete_all_csv():
    try:
        # Get list of files currently being processed
        active_files = set()
        for job in job_status.values():
            if job.get('status') in ['processing', 'queued']:
                if job.get('current_csv_file'):
                    active_files.add(job.get('current_csv_file'))

        deleted_files = []
        for filename in os.listdir(CSV_OUTPUT_DIR):
            if filename.endswith('.csv') and filename not in active_files:
                filepath = os.path.join(CSV_OUTPUT_DIR, filename)
                os.remove(filepath)
                deleted_files.append(filename)

        return {"message": f"Deleted {len(deleted_files)} CSV files", "deleted_files": deleted_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
