# ML Job Scraper - Questions & Answers

Answers to all your specific questions about the application architecture and implementation.

---

## Table of Contents

1. [Add-1: Storing Metadata in DB](#add-1-storing-metadata-in-db)
2. [Sync or Async Job?](#sync-or-async-job)
3. [The Website That Can Be Scraped Without Auth](#the-website-that-can-be-scraped-without-auth)
4. [List of APIs Required](#list-of-apis-required)
5. [In Which Flow, What Will Be The Request Method](#in-which-flow-what-will-be-the-request-method)

---

## Add-1: Storing Metadata in DB

### What Metadata Is Stored?

The application stores comprehensive metadata in the `scraping_metadata` table for every scraping operation.

### ScrapingMetadata Model Fields

```python
class ScrapingMetadata(models.Model):
    id: UUIDField                    # Unique operation ID
    scrape_type: CharField           # 'bulk' or 'realtime'
    status: CharField                # 'pending', 'in_progress', 'completed', 'failed'
    source_portal: CharField         # Portal name or 'multi' for bulk
    
    # Timing metadata
    started_at: DateTimeField        # When operation started
    completed_at: DateTimeField      # When operation completed
    duration_seconds: IntegerField   # Total execution time
    
    # Statistics
    jobs_scraped: IntegerField       # Total jobs found on portals
    jobs_stored: IntegerField        # Jobs successfully stored in DB
    ai_ml_jobs_found: IntegerField  # AI/ML jobs identified
    errors_count: IntegerField       # Number of errors encountered
    
    # Error tracking
    error_message: TextField         # Human-readable error description
    error_details: JSONField         # Detailed error information
    
    # Request tracking
    request_params: JSONField        # Original API request parameters
    metadata: JSONField              # Additional tracking information
```

### Job Model Metadata Fields

```python
class Job(models.Model):
    # ... other fields ...
    
    # Metadata storage
    metadata: JSONField              # Additional scraping data
    scraped_at: DateTimeField        # When job was scraped
    ai_ml_score: FloatField          # Confidence score (0-100)
    is_ai_ml_job: BooleanField       # Classification flag
```

### Example Stored Metadata

#### Scraping Operation Metadata
```json
{
  "scraping_id": "550e8400-e29b-41d4-a716-446655440000",
  "scrape_type": "bulk",
  "status": "completed",
  "started_at": "2026-01-17T08:00:00Z",
  "completed_at": "2026-01-17T08:00:14Z",
  "duration_seconds": 14,
  "jobs_scraped": 312,
  "jobs_stored": 82,
  "ai_ml_jobs_found": 87,
  "errors_count": 0,
  "request_params": {
    "max_age_hours": 48,
    "include_portals": ["guru", "truelancer", "twine", "remotework"],
    "filter_ai_ml": true
  }
}
```

#### Job Metadata
```json
{
  "job_id": "guru_12345",
  "title": "Senior Machine Learning Engineer",
  "source_portal": "guru",
  "ai_ml_score": 95.5,
  "is_ai_ml_job": true,
  "scraped_at": "2026-01-17T08:00:05Z",
  "metadata": {
    "job_type": "Full-time",
    "experience_level": "Senior",
    "skills": ["Python", "TensorFlow", "PyTorch"],
    "salary_range": "$120k - $180k USD"
  }
}
```

### Database Queries for Metadata

```python
# Get all scraping operations
from jobs.models import ScrapingMetadata

all_scrapings = ScrapingMetadata.objects.all()

# Get completed operations
completed = ScrapingMetadata.objects.filter(status='completed')

# Get failed operations with errors
failed = ScrapingMetadata.objects.filter(status='failed')

# Get statistics for a scraping operation
scrape = ScrapingMetadata.objects.get(id='550e8400-e29b-41d4-a716-446655440000')
print(f"Jobs scraped: {scrape.jobs_scraped}")
print(f"Jobs stored: {scrape.jobs_stored}")
print(f"Duration: {scrape.duration_seconds}s")

# Get AI/ML classification statistics
ai_ml_count = Job.objects.filter(is_ai_ml_job=True).count()
total_count = Job.objects.count()
print(f"AI/ML percentage: {(ai_ml_count/total_count)*100}%")
```

---

## Sync or Async Job?

### Current Implementation: SYNC with Threading

The application uses **synchronous** operations with **ThreadPoolExecutor** for concurrent execution.

### Why Synchronous with Threading?

**Advantages**:
- ✅ Simple implementation
- ✅ No external message queue needed
- ✅ Good for 4 concurrent tasks
- ✅ Easy debugging
- ✅ Lightweight

**When to Use**: Development, single-server deployment, small concurrent load

### Architecture

```python
# scraper/scraper.py
from concurrent.futures import ThreadPoolExecutor, as_completed

class JobScraperService:
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
    
    def scrape_all_portals(self, max_age_hours=48) -> Dict:
        """Synchronous method using threads for concurrency"""
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit 4 tasks to thread pool
            future_to_portal = {
                executor.submit(self._scrape_portal, portal): portal
                for portal in self.SCRAPER_CLASSES.keys()
            }
            
            # Collect results as threads complete
            for future in as_completed(future_to_portal):
                portal = future_to_portal[future]
                jobs, ai_ml_count, error = future.result()
                # Process results
        
        return results
```

### Execution Timeline

```
Request arrives
    ↓
Create ScrapingMetadata (status: in_progress)
    ↓
ThreadPoolExecutor.submit(4 tasks)
    ├─ Thread 1: Guru scraper (runs concurrently)
    ├─ Thread 2: Truelancer scraper (runs concurrently)
    ├─ Thread 3: Twine scraper (runs concurrently)
    └─ Thread 4: RemoteWork scraper (runs concurrently)
    ↓
Wait for all threads to complete (with timeout)
    ↓
Store results in database
    ↓
Update ScrapingMetadata (status: completed)
    ↓
Return response
```

### Time Comparison

**Sequential (No Threading)**:
- Guru: 1 sec
- Truelancer: 1 sec
- Twine: 1 sec
- RemoteWork: 1 sec
- **Total: 4 seconds** ⏱️

**Threaded (Current Implementation)**:
- All 4 run in parallel
- **Total: ~1 second** ⏱️ (4x faster)

### Future: True Async (Celery)

For production with heavy load, upgrade to:

```python
# Using Celery + Redis
from celery import shared_task

@shared_task
def async_scrape_all_portals(max_age_hours=48):
    """Truly asynchronous task"""
    scraper_service = JobScraperService()
    results = scraper_service.scrape_all_portals(max_age_hours)
    return results

# In views.py
from celery_app import async_scrape_all_portals
task = async_scrape_all_portals.delay(max_age_hours=48)
scraping_id = task.id
```

**Advantages of Celery**:
- True asynchronous execution
- Distributed processing
- Better for high load
- Built-in retry logic
- Job persistence

---

## The Website That Can Be Scraped Without Auth

### Analysis of Each Portal

#### 1. ✅ Guru.com (Can Scrape Without Auth)

**Status**: Public access, no authentication required
```
URL: https://www.guru.com/jobs
Method: GET
Authentication: None
Bot Protection: Moderate (rotating IPs recommended)
Data: HTML with job listings
```

#### 2. ✅ Truelancer.com (Can Scrape Without Auth)

**Status**: Public access, no authentication required
```
URL: https://www.truelancer.com/projects
Method: GET
Authentication: None
Bot Protection: Light
Data: HTML with project listings
```

#### 3. ✅ Twine.com (Can Scrape Without Auth)

**Status**: Public access, no authentication required
```
URL: https://www.twine.com/jobs
Method: GET
Authentication: None
Bot Protection: Light
Data: HTML with job cards
```

#### 4. ✅ RemoteWork.com (Can Scrape Without Auth)

**Status**: Public access, no authentication required
```
URL: https://www.remotework.com/remote-jobs
Method: GET
Authentication: None
Bot Protection: Light
Data: HTML with job listings
```

### Additional Websites That Can Be Scraped (Without Auth)

**Recommended additions**:

```
LinkedIn Jobs (Public Profile)
  URL: linkedin.com/jobs/
  Method: GET
  Auth: Not required for public listings
  Note: Robot.txt restrictions

Indeed.com
  URL: indeed.com/jobs?q=machine+learning
  Method: GET
  Auth: Not required
  Protection: Strong - has scraping protection

Stack Overflow Jobs
  URL: stackoverflow.com/jobs
  Method: GET
  Auth: Not required for public listings
  Protection: Moderate

GitHub Jobs
  URL: github.com/jobs
  Method: GET
  Auth: Not required
  Protection: Light

Kaggle Competitions (Data Science)
  URL: kaggle.com
  Method: GET (with API key for better access)
  Auth: Optional API key
  Protection: Moderate

AngelList (Startups)
  URL: angel.co/jobs
  Method: GET
  Auth: Optional for better access
  Protection: Light
```

### How to Add a New Portal

```python
# In scraper/scraper.py

class GitHubJobsScraper(BaseScraper):
    """Scraper for GitHub Jobs"""
    
    BASE_URL = "https://www.github.com"
    
    def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from GitHub"""
        try:
            logger.info("Starting GitHub Jobs scraping...")
            jobs = []
            
            url = f"{self.BASE_URL}/jobs"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            job_elements = soup.find_all('div', class_='job-listing')
            
            for element in job_elements:
                try:
                    job = self._parse_job(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from GitHub")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping GitHub: {e}")
            return []
    
    def _parse_job(self, element) -> Dict:
        """Parse job details"""
        # Implementation
        pass

# Add to SCRAPER_CLASSES
JobScraperService.SCRAPER_CLASSES['github'] = GitHubJobsScraper
```

---

## List of APIs Required

### Implemented APIs (4 APIs)

#### 1. **Bulk Scraping API** (POST)
```
POST /api/jobs/bulk-scrape/
Purpose: Scrape all portals concurrently
Input: max_age_hours, include_portals, filter_ai_ml
Output: scraping_id, statistics, results
Status Code: 200 (success) or 500 (error)
```

#### 2. **Real-time Guru API** (POST)
```
POST /api/jobs/realtime-guru/
Purpose: Real-time scraping from Guru.com
Input: (optional) job_id
Output: scraping_id, statistics
Status Code: 200 (success) or 500 (error)
```

#### 3. **Get Jobs API** (GET)
```
GET /api/jobs/list/
Purpose: Retrieve stored jobs with filtering
Parameters: ai_ml_only, portal, company_id, limit, offset
Output: jobs list, pagination info
Status Code: 200 (success) or 500 (error)
```

#### 4. **Scraping Status API** (GET)
```
GET /api/jobs/scraping-status/{scraping_id}/
Purpose: Check status of a scraping operation
Output: operation status, statistics, errors
Status Code: 200 (success) or 404 (not found) or 500 (error)
```

### Optional APIs (For Future Enhancement)

#### 5. **Company API** (GET)
```
GET /api/companies/{company_id}/
Purpose: Get company details
```

#### 6. **Statistics API** (GET)
```
GET /api/jobs/statistics/
Purpose: Get aggregated statistics
Parameters: time_period, portal, ai_ml_only
```

#### 7. **Advanced Search API** (POST)
```
POST /api/jobs/search/
Purpose: Advanced search with multiple filters
Input: keywords, salary_range, location, experience_level
```

#### 8. **Batch Scraping API** (POST)
```
POST /api/jobs/batch-scrape/
Purpose: Schedule multiple scraping tasks
Input: portal_list, schedules
Output: batch_id with multiple scraping_ids
```

---

## In Which Flow, What Will Be The Request Method

### API Flow & Request Methods

#### Flow 1: Bulk Scraping Workflow

```
User Action                    HTTP Method    URL
──────────────────────────────────────────────────────────
1. Initiate Bulk Scrape   →    POST         /api/jobs/bulk-scrape/
2. Get Scraping ID        ←    200 Response (immediate)
3. Check Status           →    GET          /api/jobs/scraping-status/{id}/
4. Retrieve Results       →    GET          /api/jobs/list/?ai_ml_only=true
5. Export Jobs            ←    200 Response (JSON)
```

**Complete Request/Response Cycle**:

```python
# 1. POST - Start Scraping (Client initiates)
POST /api/jobs/bulk-scrape/
Content-Type: application/json
{
  "max_age_hours": 48,
  "include_portals": ["guru", "truelancer", "twine", "remotework"],
  "filter_ai_ml": true
}

# Response (200 OK)
{
  "status": "success",
  "scraping_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": { "total_jobs": 312, ... }
}

# 2. GET - Check Status (Client polls)
GET /api/jobs/scraping-status/550e8400-e29b-41d4-a716-446655440000/

# Response (200 OK)
{
  "status": "success",
  "data": { "status": "completed", "jobs_stored": 82, ... }
}

# 3. GET - Retrieve Jobs (Client fetches results)
GET /api/jobs/list/?ai_ml_only=true&limit=20

# Response (200 OK)
{
  "status": "success",
  "data": { "total_count": 82, "jobs": [ {...}, {...} ] }
}
```

#### Flow 2: Real-time Guru Workflow

```
User Action                    HTTP Method    URL
──────────────────────────────────────────────────────────
1. Get Real-time Guru   →     POST         /api/jobs/realtime-guru/
2. Store New Jobs       ←     201 Created
3. Check Status         →     GET          /api/jobs/scraping-status/{id}/
4. View New Jobs        →     GET          /api/jobs/list/?portal=guru
```

```python
# 1. POST - Real-time Scrape
POST /api/jobs/realtime-guru/
Content-Type: application/json
{}

# Response (200 OK)
{
  "status": "success",
  "scraping_id": "550e8400-e29b-41d4-a716-446655440001",
  "data": {
    "jobs_fetched": 45,
    "jobs_stored": 23,
    "ai_ml_jobs": 21
  }
}

# 2. GET - Check Scraping Status
GET /api/jobs/scraping-status/550e8400-e29b-41d4-a716-446655440001/
```

#### Flow 3: Data Retrieval Workflow

```
User Action                    HTTP Method    URL
──────────────────────────────────────────────────────────
1. Get AI/ML Jobs      →      GET          /api/jobs/list/?ai_ml_only=true
2. Filter by Portal    →      GET          /api/jobs/list/?portal=guru&ai_ml_only=true
3. Pagination          →      GET          /api/jobs/list/?limit=50&offset=100
4. View Results        ←      200 Response (JSON with job list)
```

```python
# 1. GET - All AI/ML Jobs
GET /api/jobs/list/?ai_ml_only=true

# Response (200 OK)
{
  "status": "success",
  "data": {
    "total_count": 243,
    "returned": 20,
    "jobs": [ {...} ]
  }
}

# 2. GET - Filter by Portal
GET /api/jobs/list/?ai_ml_only=true&portal=guru&limit=10

# 3. GET - Pagination
GET /api/jobs/list/?limit=50&offset=50  # Second page of 50 items
```

### HTTP Status Codes Used

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Success - GET/POST returns data | `/list/` successful retrieval |
| 201 | Created - Resource created | Job record created successfully |
| 400 | Bad Request - Invalid input | Malformed JSON |
| 404 | Not Found - Resource doesn't exist | Invalid scraping_id |
| 500 | Server Error - Processing failed | Database connection error |

### Request Methods Summary

```
POST /api/jobs/bulk-scrape/
├─ Purpose: Initiate bulk scraping
├─ When: User wants to scrape all portals
├─ Returns: scraping_id for tracking
└─ Status: 200 or 500

POST /api/jobs/realtime-guru/
├─ Purpose: Real-time Guru scraping
├─ When: User wants fresh Guru jobs
├─ Returns: scraping_id for tracking
└─ Status: 200 or 500

GET /api/jobs/list/
├─ Purpose: Retrieve stored jobs
├─ When: User wants to view jobs
├─ Parameters: Filters and pagination
└─ Status: 200 or 500

GET /api/jobs/scraping-status/{id}/
├─ Purpose: Check operation status
├─ When: User wants operation details
├─ Returns: Status and statistics
└─ Status: 200, 404, or 500
```

### API Call Sequence Diagram

```
Client                          Server
  │                              │
  ├─────POST bulk-scrape────────→│
  │                              ├─ Create ScrapingMetadata
  │                              ├─ Start scraping (async)
  │                              │
  │←──200 + scraping_id ────────│
  │                              ├─ Scraping in progress
  │                              │
  ├─GET scraping-status/id────→│
  │                              ├─ Check status
  │←──200 + status ────────────│
  │                              ├─ Scraping continues
  │                              │
  ├─GET scraping-status/id────→│
  │←──200 + completed ─────────│
  │                              │
  ├──GET jobs/list/ ──────────→│
  │                              ├─ Query database
  │←──200 + jobs ──────────────│
  │                              │
```

---

## Summary Table

| Question | Answer |
|----------|--------|
| **Metadata Storage** | ✅ Stored in `scraping_metadata` table with 15+ fields |
| **Sync or Async** | ✅ Sync + Threading (ThreadPoolExecutor with 4 workers) |
| **Scrapeable Sites** | ✅ All 4 (Guru, Truelancer, Twine, RemoteWork) without auth |
| **APIs Required** | ✅ 4 main APIs (bulk, realtime, list, status) + 4 optional |
| **Request Methods** | ✅ POST for scraping, GET for retrieval and status |

---

**Document Created**: January 17, 2026
**Version**: 1.0
