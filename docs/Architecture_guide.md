# ML Job Scraper - Architecture Guide

## System Overview

The ML Job Scraper is a Django-based web application that automatically scrapes AI/ML job listings from multiple job portals and stores them in a SQLite database. It provides two main APIs for bulk scraping and real-time updates.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                       │
│            (Web Apps, Mobile Apps, Scripts)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   DJANGO REST API LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐      │
│  │  Bulk Scrape │  │ Real-time    │  │  Get Jobs API │      │
│  │  API (POST)  │  │  Guru API    │  │   (GET)       │      │
│  └──────────────┘  └──────────────┘  └───────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Business   │  │  Data Model  │  │   Scraper    │
│   Logic      │  │  (Models)    │  │   Module     │
│  (Views)     │  │              │  │  (Service)   │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Company DB  │  │   Jobs DB    │  │  Scraping    │
│   Tables     │  │   Tables     │  │  Metadata    │
└──────────────┘  └──────────────┘  └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   SQLite Database (db.sqlite3) │
        └────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │Companies │  │   Jobs   │  │ Scraping │
    │ Table    │  │  Table   │  │ Metadata │
    └──────────┘  └──────────┘  └──────────┘
```

## Component Architecture

### 1. **API Layer** (`jobs/views.py`)
   - **bulk_scrape_jobs()** - Initiates bulk scraping from all portals
   - **realtime_scrape_guru()** - Real-time Guru.com scraping
   - **get_jobs()** - Retrieve stored jobs with filters
   - **get_scraping_status()** - Check scraping operation status

### 2. **Data Model Layer** (`jobs/models.py` & `companies/models.py`)
   - **Job Model** - Stores job listings with metadata
   - **Company Model** - Stores company information
   - **ScrapingMetadata Model** - Tracks scraping operations

### 3. **Scraper Module** (`scraper/scraper.py`)
   - **BaseScraper** - Base class with common functionality
   - **GuruScraper** - Guru.com scraper
   - **TruelancerScraper** - Truelancer.com scraper
   - **TwineScraper** - Twine.com scraper
   - **RemoteWorkScraper** - RemoteWork.com scraper
   - **JobScraperService** - Main orchestrator with thread pool

### 4. **Database Layer** (SQLite)
   - **companies** table
   - **jobs** table
   - **scraping_metadata** table

## Data Flow

### Bulk Scraping Flow

```
1. Client sends POST request to /api/jobs/bulk-scrape/
                    │
                    ▼
2. API creates ScrapingMetadata record (status: in_progress)
                    │
                    ▼
3. JobScraperService initializes with ThreadPoolExecutor
                    │
        ┌───────────┼───────────┬──────────┬────────────┐
        │           │           │          │            │
        ▼           ▼           ▼          ▼            ▼
   GuruScraper  TruelancerScraper TwineScraper RemoteWorkScraper
        │           │           │          │            │
        └───────────┼───────────┼──────────┼────────────┘
                    │
                    ▼
        4. AI/ML filtering applied (keyword matching)
                    │
                    ▼
        5. For each job:
           - Get or create Company
           - Create or update Job record
                    │
                    ▼
        6. Update ScrapingMetadata with results
                    │
                    ▼
        7. Return response with scraping_id and stats
```

### Real-time Guru Scraping Flow

```
1. Client sends POST request to /api/jobs/realtime-guru/
                    │
                    ▼
2. API creates ScrapingMetadata record (status: in_progress)
                    │
                    ▼
3. GuruScraper fetches latest jobs
                    │
                    ▼
4. Filter for AI/ML jobs only
                    │
                    ▼
5. For each AI/ML job:
   - Get or create Company
   - Create new Job record (as new record, not update)
                    │
                    ▼
6. Update ScrapingMetadata
                    │
                    ▼
7. Return response with stats
```

## Asynchronous Processing

The application uses **ThreadPoolExecutor** for concurrent scraping:

```python
with ThreadPoolExecutor(max_workers=4) as executor:
    # 4 threads scrape 4 portals simultaneously
    future_to_portal = {
        executor.submit(scrape_portal, portal): portal
        for portal in portals
    }
    
    for future in as_completed(future_to_portal):
        # Collect results as they complete
```

**Benefits:**
- Multiple portals scraped in parallel
- Significantly faster overall execution
- Non-blocking operations
- Better resource utilization

## Database Schema

### Companies Table
```
id (UUID)
company_id (String, unique)
name (String)
description (Text)
website (URL)
company_size (Choice)
headquarters_location (String)
country (String)
email (Email)
phone (String)
rating (Float)
review_count (Integer)
industry (String)
focus_areas (Text)
is_verified (Boolean)
created_at (DateTime)
updated_at (DateTime)
metadata (JSON)
```

### Jobs Table
```
id (UUID)
job_id (String, unique)
title (String)
description (Text)
job_url (URL)
source_portal (Choice: guru, truelancer, twine, remotework)
job_type (String)
experience_level (String)
salary_min (Decimal)
salary_max (Decimal)
currency (String)
location (String)
skills_required (Text)
status (Choice: active, closed, expired)
company_id (FK to Companies)
job_posted_at (DateTime)
is_ai_ml_job (Boolean)
ai_ml_score (Float) - 0-100 confidence
created_at (DateTime)
updated_at (DateTime)
scraped_at (DateTime)
metadata (JSON)
```

### Scraping Metadata Table
```
id (UUID)
scrape_type (Choice: bulk, realtime)
status (Choice: pending, in_progress, completed, failed)
source_portal (String)
started_at (DateTime)
completed_at (DateTime)
duration_seconds (Integer)
jobs_scraped (Integer)
jobs_stored (Integer)
ai_ml_jobs_found (Integer)
errors_count (Integer)
error_message (Text)
error_details (JSON)
request_params (JSON)
metadata (JSON)
```

## AI/ML Job Filtering

The system uses **keyword-based classification** to identify AI/ML jobs:

**Keywords List:**
- Core ML: machine learning, deep learning, neural network, ai, artificial intelligence
- Frameworks: tensorflow, pytorch, scikit-learn
- Roles: data scientist, ml engineer, ai engineer
- Techniques: NLP, computer vision, clustering, classification, regression
- Advanced: LLM, GPT, generative, transformer, BERT, reinforcement learning

**Classification Logic:**
1. Combine job title + description
2. Count keyword matches
3. Calculate confidence score: (matches / total_keywords) × 100
4. Threshold: ≥2 keywords OR ≥20% confidence

## API Endpoints

### POST /api/jobs/bulk-scrape/
Bulk scrape all portals for AI/ML jobs

**Request:**
```json
{
  "max_age_hours": 48,
  "include_portals": ["guru", "truelancer", "twine", "remotework"],
  "filter_ai_ml": true
}
```

**Response:**
```json
{
  "status": "success",
  "scraping_id": "uuid",
  "data": {
    "total_jobs": 150,
    "ai_ml_jobs": 45,
    "stored_jobs": 42,
    "duration_seconds": 12.5
  }
}
```

### POST /api/jobs/realtime-guru/
Real-time scrape from Guru.com

**Request:**
```json
{
  "job_id": "optional_id"
}
```

**Response:**
```json
{
  "status": "success",
  "scraping_id": "uuid",
  "data": {
    "jobs_fetched": 50,
    "jobs_stored": 25,
    "ai_ml_jobs": 23
  }
}
```

### GET /api/jobs/list/
Retrieve stored jobs with filters

**Query Parameters:**
- `ai_ml_only=true|false`
- `portal=guru|truelancer|twine|remotework`
- `company_id=uuid`
- `limit=20`
- `offset=0`

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_count": 500,
    "returned": 20,
    "jobs": [...]
  }
}
```

### GET /api/jobs/scraping-status/{scraping_id}/
Check scraping operation status

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "completed",
    "jobs_scraped": 150,
    "jobs_stored": 42,
    "duration_seconds": 12
  }
}
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2 |
| Database | SQLite |
| Web Scraping | BeautifulSoup4, Requests |
| Async Processing | ThreadPoolExecutor |
| HTTP Server | Django Development Server |
| Language | Python 3.9+ |

## Security Considerations

1. **CSRF Protection** - Disabled for APIs (`@csrf_exempt`)
2. **Input Validation** - JSON validation for requests
3. **Error Handling** - Proper error messages and logging
4. **Database Indexing** - Key fields indexed for performance
5. **Rate Limiting** - Should be added in production

## Performance Optimization

1. **Database Indexing** - Composite indexes on frequently queried columns
2. **Pagination** - GET endpoints support limit/offset
3. **Concurrent Scraping** - ThreadPoolExecutor for parallel requests
4. **Batch Operations** - Bulk create/update for efficiency
5. **Connection Pooling** - Requests session reuse

## Scalability Considerations

**Current Implementation (Single Server):**
- SQLite suitable for development
- ThreadPoolExecutor limits to 4 concurrent threads

**For Production Scaling:**
- Replace SQLite with PostgreSQL
- Use Celery + Redis for async jobs
- Implement message queue for scraping tasks
- Add caching layer (Redis)
- Separate scraper workers from API servers

## Deployment Architecture

```
                ┌────────────────────┐
                │   Load Balancer    │
                └────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐       ┌────────┐       ┌────────┐
    │ Django │       │ Django │       │ Django │
    │ Server │       │ Server │       │ Server │
    │ Port   │       │ Port   │       │ Port   │
    └────────┘       └────────┘       └────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    ┌────────┐       ┌────────┐       ┌────────┐
    │Scraper │       │Scraper │       │Scraper │
    │Worker  │       │Worker  │       │Worker  │
    └────────┘       └────────┘       └────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                 ┌───────▼────────┐
                 │ PostgreSQL DB  │
                 │    (Prod)      │
                 └────────────────┘
                 
                 ┌────────────────┐
                 │ Redis Cache    │
                 └────────────────┘
```

---

**Document Version**: 1.0
**Last Updated**: January 17, 2026
