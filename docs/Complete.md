# ML Job Scraper - Complete Guide

## End-to-End Implementation Guide

This document provides a comprehensive walkthrough of the entire ML Job Scraper system, from setup to deployment.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Installation & Setup](#installation--setup)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Scraping Process](#scraping-process)
7. [AI/ML Classification](#aiml-classification)
8. [Concurrency Model](#concurrency-model)
9. [Error Handling](#error-handling)
10. [Deployment Guide](#deployment-guide)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Project Overview

### Purpose
The ML Job Scraper automatically collects AI/ML job listings from multiple job portals, filters them based on keywords, and stores them in a local database for analysis and retrieval.

### Key Features
- **Multi-portal scraping**: Guru.com, Truelancer.com, Twine.com, RemoteWork.com
- **Concurrent execution**: Up to 4 portals scraped simultaneously
- **AI/ML filtering**: Keyword-based classification with confidence scoring
- **REST APIs**: Two main APIs for bulk and real-time scraping
- **Database tracking**: Complete metadata about each scraping operation
- **Error handling**: Graceful error recovery and detailed error logging

### High-Level Flow

```
User Request (POST /api/jobs/bulk-scrape/)
    ↓
Django API Handler
    ↓
JobScraperService (orchestrator)
    ↓
ThreadPoolExecutor (4 concurrent threads)
    ├─ Guru.com Scraper
    ├─ Truelancer.com Scraper
    ├─ Twine.com Scraper
    └─ RemoteWork.com Scraper
    ↓
AI/ML Classification Filter
    ↓
Store in SQLite Database
    ↓
Return Response to User
```

---

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | Django | 4.2.8 |
| **Language** | Python | 3.9+ |
| **Database** | SQLite | 3.x |
| **Web Scraping** | BeautifulSoup4 | 4.12.2 |
| **HTTP Library** | Requests | 2.31.0 |
| **HTML Parser** | lxml | 4.9.3 |
| **Concurrency** | ThreadPoolExecutor | Built-in |
| **ORM** | Django ORM | Built-in |

---

## Installation & Setup

### Step 1: Prerequisites
```bash
# Verify Python installation
python --version  # Should be 3.9 or higher

# Verify pip
pip --version
```

### Step 2: Create Virtual Environment
```bash
# Navigate to project directory
cd d:\web_scraping

# Create virtual environment
python -m venv ml_job_env

# Activate (Windows PowerShell)
.\ml_job_env\Scripts\Activate.ps1

# Activate (Windows CMD)
ml_job_env\Scripts\activate.bat
```

### Step 3: Install Dependencies
```bash
# Navigate to project folder
cd ml_job_scraper

# Install all requirements
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Verify database creation
ls db.sqlite3  # Should exist
```

### Step 5: Run Development Server
```bash
# Start server on port 8000
python manage.py runserver

# Or use different port
python manage.py runserver 8001
```

Server should start at: `http://127.0.0.1:8000`

---

## Database Schema

### Companies Table

```sql
CREATE TABLE companies (
    id TEXT PRIMARY KEY,                    -- UUID
    company_id TEXT UNIQUE NOT NULL,        -- Unique identifier
    name TEXT NOT NULL,                     -- Company name
    description TEXT,                       -- Company description
    website TEXT,                           -- Company website
    company_size TEXT,                      -- Size category
    headquarters_location TEXT,             -- HQ location
    country TEXT,                           -- Country
    email TEXT,                             -- Contact email
    phone TEXT,                             -- Phone number
    rating REAL,                            -- Rating (0-5)
    review_count INTEGER,                   -- Number of reviews
    industry TEXT,                          -- Industry
    focus_areas TEXT,                       -- Focus areas (AI, ML, etc.)
    is_verified BOOLEAN,                    -- Verification status
    metadata JSON,                          -- Additional data
    created_at TIMESTAMP NOT NULL,          -- Creation time
    updated_at TIMESTAMP NOT NULL           -- Last update
);

CREATE INDEX idx_company_name ON companies(name);
CREATE INDEX idx_company_country ON companies(country);
CREATE INDEX idx_company_created_at ON companies(created_at);
```

### Jobs Table

```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,                    -- UUID
    job_id TEXT UNIQUE NOT NULL,            -- Unique job identifier
    title TEXT NOT NULL,                    -- Job title
    description TEXT NOT NULL,              -- Job description
    job_url TEXT NOT NULL,                  -- Job posting URL
    source_portal TEXT NOT NULL,            -- 'guru', 'truelancer', 'twine', 'remotework'
    job_type TEXT,                          -- 'Full-time', 'Contract', etc.
    experience_level TEXT,                  -- 'Senior', 'Junior', etc.
    salary_min DECIMAL,                     -- Minimum salary
    salary_max DECIMAL,                     -- Maximum salary
    currency TEXT,                          -- 'USD', 'EUR', etc.
    location TEXT,                          -- Job location
    skills_required TEXT,                   -- Required skills
    status TEXT,                            -- 'active', 'closed', 'expired'
    company_id TEXT NOT NULL,               -- Foreign key
    job_posted_at TIMESTAMP NOT NULL,       -- Posted time
    is_ai_ml_job BOOLEAN NOT NULL,          -- AI/ML classification
    ai_ml_score REAL,                       -- Confidence (0-100)
    metadata JSON,                          -- Additional data
    created_at TIMESTAMP NOT NULL,          -- Record creation
    updated_at TIMESTAMP NOT NULL,          -- Last update
    scraped_at TIMESTAMP NOT NULL,          -- Scrape time
    
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE INDEX idx_job_ai_ml_status ON jobs(is_ai_ml_job, status);
CREATE INDEX idx_job_portal_date ON jobs(source_portal, created_at);
CREATE INDEX idx_job_company_date ON jobs(company_id, created_at);
```

### Scraping Metadata Table

```sql
CREATE TABLE scraping_metadata (
    id TEXT PRIMARY KEY,                    -- UUID
    scrape_type TEXT NOT NULL,              -- 'bulk' or 'realtime'
    status TEXT NOT NULL,                   -- 'pending', 'in_progress', 'completed', 'failed'
    source_portal TEXT NOT NULL,            -- Portal name
    started_at TIMESTAMP NOT NULL,          -- Start time
    completed_at TIMESTAMP,                 -- Completion time
    duration_seconds INTEGER,               -- Execution duration
    jobs_scraped INTEGER,                   -- Total jobs found
    jobs_stored INTEGER,                    -- Jobs saved to DB
    ai_ml_jobs_found INTEGER,               -- AI/ML jobs identified
    errors_count INTEGER,                   -- Error count
    error_message TEXT,                     -- Error description
    error_details JSON,                     -- Detailed error info
    request_params JSON NOT NULL,           -- Original request
    metadata JSON                           -- Additional tracking
);

CREATE INDEX idx_metadata_status_date ON scraping_metadata(status, started_at);
CREATE INDEX idx_metadata_portal_type ON scraping_metadata(source_portal, scrape_type);
```

---

## API Endpoints

### 1. Bulk Scrape API

**Endpoint**: `POST /api/jobs/bulk-scrape/`

**Description**: Scrape all portals concurrently and filter for AI/ML jobs

**Request**:
```json
{
  "max_age_hours": 48,
  "include_portals": ["guru", "truelancer", "twine", "remotework"],
  "filter_ai_ml": true
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "scraping_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Successfully scraped and stored jobs",
  "data": {
    "total_jobs": 312,
    "ai_ml_jobs": 87,
    "stored_jobs": 82,
    "duration_seconds": 14.3,
    "errors": null
  }
}
```

**Response (Error)**:
```json
{
  "status": "error",
  "message": "Connection timeout while scraping Guru.com"
}
```

**Using PowerShell**:
```powershell
$body = @{
    max_age_hours = 48
    include_portals = @('guru', 'truelancer', 'twine', 'remotework')
    filter_ai_ml = $true
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/bulk-scrape/" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

$response.Content | ConvertFrom-Json
```

---

### 2. Real-time Guru Scraping API

**Endpoint**: `POST /api/jobs/realtime-guru/`

**Description**: Fetch real-time jobs from Guru.com only

**Request**:
```json
{
  "job_id": "optional_specific_job_id"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "scraping_id": "550e8400-e29b-41d4-a716-446655440001",
  "message": "Real-time Guru.com scraping completed",
  "data": {
    "jobs_fetched": 45,
    "jobs_stored": 23,
    "ai_ml_jobs": 21
  }
}
```

**Using PowerShell**:
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/realtime-guru/" `
  -Method POST `
  -ContentType "application/json" `
  -Body "{}"

$response.Content | ConvertFrom-Json
```

---

### 3. Get Jobs API

**Endpoint**: `GET /api/jobs/list/`

**Description**: Retrieve stored jobs with filtering and pagination

**Query Parameters**:
- `ai_ml_only` (boolean): Filter only AI/ML jobs (default: true)
- `portal` (string): Filter by portal ('guru', 'truelancer', 'twine', 'remotework')
- `company_id` (UUID): Filter by company
- `limit` (integer): Number of results (default: 20, max: 100)
- `offset` (integer): Pagination offset (default: 0)

**Example URL**:
```
GET /api/jobs/list/?ai_ml_only=true&portal=guru&limit=10&offset=0
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "total_count": 243,
    "returned": 10,
    "offset": 0,
    "limit": 10,
    "jobs": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "job_id": "guru_12345",
        "title": "Senior Machine Learning Engineer",
        "description": "We are looking for an experienced ML engineer...",
        "job_url": "https://guru.com/jobs/12345",
        "source_portal": "guru",
        "company": {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "name": "Tech Company Inc"
        },
        "ai_ml_score": 95.5,
        "job_posted_at": "2026-01-16T10:30:00Z",
        "created_at": "2026-01-17T08:15:00Z"
      }
    ]
  }
}
```

**Using PowerShell**:
```powershell
$uri = "http://127.0.0.1:8000/api/jobs/list/?ai_ml_only=true&limit=5"
$response = Invoke-WebRequest -Uri $uri -Method GET
$response.Content | ConvertFrom-Json
```

---

### 4. Check Scraping Status API

**Endpoint**: `GET /api/jobs/scraping-status/{scraping_id}/`

**Description**: Get detailed status of a scraping operation

**Example URL**:
```
GET /api/jobs/scraping-status/550e8400-e29b-41d4-a716-446655440000/
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "scraping_id": "550e8400-e29b-41d4-a716-446655440000",
    "scrape_type": "bulk",
    "status": "completed",
    "source_portal": "multi",
    "jobs_scraped": 312,
    "jobs_stored": 82,
    "ai_ml_jobs_found": 87,
    "errors_count": 0,
    "duration_seconds": 14,
    "started_at": "2026-01-17T08:00:00Z",
    "completed_at": "2026-01-17T08:00:14Z"
  }
}
```

---

## Scraping Process

### High-Level Process

```
1. User submits API request
   │
2. Validate request parameters
   │
3. Create ScrapingMetadata record (in_progress)
   │
4. Initialize JobScraperService
   │
5. Launch ThreadPoolExecutor with 4 workers
   │
6. Each worker scrapes one portal:
   ├─ Fetch job listings from portal
   ├─ Parse HTML/JSON response
   ├─ Extract job details
   └─ Return raw job data
   │
7. Apply AI/ML keyword filter to all jobs
   │
8. For each AI/ML job:
   ├─ Get or create Company record
   ├─ Create or update Job record
   └─ Update counts
   │
9. Update ScrapingMetadata (completed/failed)
   │
10. Return response to user with statistics
```

### Scraper Implementation Details

#### BaseScraper Class

```python
class BaseScraper:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()  # Connection pooling
    
    def scrape_jobs(self) -> List[Dict]:
        """Override in subclass"""
        raise NotImplementedError
    
    def is_ai_ml_job(self, title, description) -> Tuple[bool, float]:
        """
        Classify job as AI/ML related
        
        Logic:
        1. Combine title + description to lowercase
        2. Count keyword matches against AI_ML_KEYWORDS
        3. Calculate confidence = (matches / total_keywords) * 100
        4. Return True if: matches >= 2 OR confidence >= 20%
        """
        # Implementation details...
```

#### Portal-Specific Scrapers

Each portal has specific HTML structure:

**Guru.com**:
```html
<div class="job-item" data-job-id="12345">
  <h2 class="job-title">Job Title</h2>
  <p class="job-description">Job description...</p>
  <a class="job-link" href="/job/12345">Link</a>
  <span class="company-name">Company Name</span>
  <span class="posted-time">2 days ago</span>
</div>
```

**Truelancer.com**:
```html
<div class="project-item" data-project-id="67890">
  <h3 class="project-title">Project Title</h3>
  <!-- Similar structure -->
</div>
```

---

## AI/ML Classification

### Classification Algorithm

```python
def is_ai_ml_job(title: str, description: str) -> Tuple[bool, float]:
    """
    Keywords: [
        'machine learning', 'deep learning', 'neural network',
        'nlp', 'computer vision', 'ai', 'tensorflow', 'pytorch',
        'scikit-learn', 'data science', 'ml engineer',
        'ai engineer', 'llm', 'gpt', 'transformer', 'bert',
        # ... and more
    ]
    
    Process:
    1. text = (title + description).lower()
    2. matches = count of keywords found in text
    3. confidence = (matches / 24) * 100  # 24 total keywords
    4. is_ai_ml = (matches >= 2) OR (confidence >= 20%)
    """
```

### Example Classifications

**Example 1: True Positive**
```
Title: "Senior Machine Learning Engineer"
Description: "Build deep learning models using TensorFlow and PyTorch..."
Keywords matched: machine learning, deep learning, tensorflow, pytorch
Matches: 4
Confidence: (4/24) * 100 = 16.7%
Decision: matches >= 2 → TRUE (AI/ML job)
Score: 16.7
```

**Example 2: False Positive Filter**
```
Title: "Software Engineer"
Description: "General software development with Java and Python"
Keywords matched: None (python is keyword but generic context)
Matches: 0
Confidence: 0%
Decision: FALSE (Not AI/ML job)
Score: 0
```

**Example 3: Threshold Test**
```
Title: "Data Analyst"
Description: "Analyze data, create reports, no ML/AI required"
Keywords matched: data (generic)
Matches: 0
Confidence: 0%
Decision: FALSE (Not AI/ML job)
Score: 0
```

---

## Concurrency Model

### ThreadPoolExecutor Implementation

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit 4 tasks (one per portal)
    future_to_portal = {
        executor.submit(scrape_portal, portal): portal
        for portal in ['guru', 'truelancer', 'twine', 'remotework']
    }
    
    # Collect results as they complete
    for future in as_completed(future_to_portal):
        portal = future_to_portal[future]
        try:
            jobs, ai_ml_count, error = future.result()
            # Process results
        except Exception as e:
            # Handle error
```

### Timeline Comparison

**Sequential Execution** (without threading):
```
Guru scrape:        1 second ━━━━
Truelancer scrape:  1 second      ━━━━
Twine scrape:       1 second           ━━━━
RemoteWork scrape:  1 second               ━━━━
                    ───────────────────────────
Total:              4 seconds
```

**Concurrent Execution** (with ThreadPoolExecutor):
```
Guru scrape:        1 second ━━━━
Truelancer scrape:  1 second ━━━━ (parallel)
Twine scrape:       1 second ━━━━ (parallel)
RemoteWork scrape:  1 second ━━━━ (parallel)
                    ───────
Total:              1-2 seconds (max individual time)
Speedup:            2-4x faster
```

---

## Error Handling

### Error Types and Recovery

```
Network Errors
├─ Connection timeout
├─ DNS resolution failure
└─ HTTP error codes
    └─ Retry logic or skip portal

Parsing Errors
├─ HTML structure changed
├─ Missing expected elements
└─ Invalid data format
    └─ Log error, skip job

Validation Errors
├─ Invalid URL format
├─ Missing required fields
└─ Duplicate job ID
    └─ Skip or merge record

Database Errors
├─ Constraint violations
├─ Transaction conflicts
└─ Connection issues
    └─ Rollback transaction, retry
```

### Error Logging

```python
import logging

logger = logging.getLogger('scraper')

try:
    jobs = scraper.scrape_jobs()
except Exception as e:
    logger.error(f"Error scraping {portal}: {str(e)}")
    metadata.error_message = str(e)
    metadata.error_details = {
        'exception_type': type(e).__name__,
        'traceback': traceback.format_exc()
    }
```

### Graceful Degradation

If a portal fails:
1. Log the error
2. Continue scraping other portals
3. Return partial results
4. Include error details in response

---

## Deployment Guide

### Development Deployment (Current)

```bash
# 1. Create virtual environment
python -m venv ml_job_env
.\ml_job_env\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Start server
python manage.py runserver
```

### Production Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY` to secure random value
- [ ] Configure allowed hosts
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up Gunicorn or uWSGI
- [ ] Configure Nginx as reverse proxy
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up environment variables
- [ ] Configure logging to files
- [ ] Set up monitoring/alerting
- [ ] Implement rate limiting
- [ ] Add backup strategy

---

## Troubleshooting

### Issue 1: Virtual Environment Not Found

**Error**: `ModuleNotFoundError: No module named 'django'`

**Solution**:
```bash
# Activate virtual environment
.\ml_job_env\Scripts\Activate.ps1

# Verify it's activated (should see (ml_job_env) in prompt)
```

### Issue 2: Port 8000 Already in Use

**Error**: `OSError: [WinError 10048]`

**Solution**:
```bash
# Use different port
python manage.py runserver 8001
```

### Issue 3: Database Not Found

**Error**: `no such table: jobs_job`

**Solution**:
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### Issue 4: Scraper Returns No Results

**Possible Causes**:
1. Website structure changed
2. Website has anti-scraping protection
3. Network connectivity issue
4. Portal is offline

**Debug Steps**:
```bash
# Open Django shell
python manage.py shell

# Test scraper directly
from scraper.scraper import GuruScraper
scraper = GuruScraper()
jobs = scraper.scrape_jobs()
print(f"Found {len(jobs)} jobs")

# Exit shell
exit()
```

### Issue 5: Jobs Not Being Classified as AI/ML

**Debug Steps**:
```bash
# Check classification logic
from scraper.scraper import BaseScraper
scraper = BaseScraper()
title = "Machine Learning Engineer"
desc = "Build AI models with TensorFlow"
is_ai_ml, score = scraper.is_ai_ml_job(title, desc)
print(f"AI/ML: {is_ai_ml}, Score: {score}")
```

---

## FAQ

**Q1: Can I add more job portals?**

A: Yes! Create a new scraper class:
```python
class NewPortalScraper(BaseScraper):
    BASE_URL = "https://www.newportal.com"
    
    def scrape_jobs(self):
        # Implementation
        pass
    
    def _parse_job(self, element):
        # Implementation
        pass

# Add to JobScraperService.SCRAPER_CLASSES
SCRAPER_CLASSES['newportal'] = NewPortalScraper
```

**Q2: How do I modify AI/ML keywords?**

A: Edit the `AI_ML_KEYWORDS` list in `scraper/scraper.py`:
```python
AI_ML_KEYWORDS = [
    'machine learning', 'deep learning', # ... add more
]
```

**Q3: Can I run this on cloud (AWS, Azure, GCP)?**

A: Yes! Deploy using:
- **AWS**: EC2, Lambda, RDS
- **Azure**: App Service, SQL Database
- **GCP**: Compute Engine, Cloud SQL

**Q4: How do I handle authentication on job portals?**

A: Some portals require login. Use Selenium for authentication:
```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://portal.com")
# Login steps here
```

**Q5: Can I schedule periodic scraping?**

A: Yes! Use APScheduler or Celery:
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(scrape_jobs, 'interval', hours=1)
scheduler.start()
```

---

**Document Version**: 1.0
**Last Updated**: January 17, 2026
