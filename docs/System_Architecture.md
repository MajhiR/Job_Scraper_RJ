# ML Job Scraper - System Architecture

## High-Level System Design

### Core Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL JOB PORTALS                         │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌───────────────┐         │
│  │Guru.com  │  │Truelancer│  │Twine   │  │RemoteWork.com │         │
│  └──────────┘  └──────────┘  └────────┘  └───────────────┘         │
└────────────────────┬────────────────────────────────────────────────┘
                     │ HTTP GET/POST
                     │ (Web Scraping)
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      SCRAPER MODULE LAYER                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  JobScraperService (Orchestrator)                            │  │
│  │  ├─ ThreadPoolExecutor (max_workers=4)                       │  │
│  │  ├─ Concurrent Scraping Scheduler                            │  │
│  │  └─ Result Aggregator                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌───────────────┐        │
│  │GuruScraper│ │Truelancer │ │Twine  │ │RemoteWorkScr. │        │
│  │Scraper   │  │Scraper   │  │Scraper │ │Scraper        │        │
│  └──────────┘  └──────────┘  └────────┘  └───────────────┘        │
│      │              │             │             │                 │
│      └──────────────┼─────────────┼─────────────┘                 │
│                     │ AI/ML Filtering & Validation                │
│                     ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Keyword-based AI/ML Classification                          │  │
│  │  - Keyword Matching                                          │  │
│  │  - Confidence Scoring (0-100)                                │  │
│  │  - Filtering (threshold: ≥2 keywords OR ≥20% confidence)    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────┬─────────────────────────────────────────────────────────────┘
         │
         │ Validated Job Data
         │ Company Information
         │ Metadata
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DJANGO REST API LAYER                            │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Request Handler (views.py)                                  │  │
│  │  ├─ JSON Request Parsing                                     │  │
│  │  ├─ Validation & Error Handling                              │  │
│  │  ├─ Business Logic Orchestration                             │  │
│  │  └─ Response Formatting                                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐              │
│  │  ORM Layer   │  │ Model Layer  │  │Transactions │              │
│  │  (Django ORM)│  │              │  │             │              │
│  └──────────────┘  └──────────────┘  └─────────────┘              │
└────────┬─────────────────────────────────────────────────────────────┘
         │
         │ SQL Queries
         │ (Create, Read, Update)
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       DATABASE LAYER (SQLite)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐             │
│  │ Companies    │  │ Jobs         │  │ Scraping      │             │
│  │ Table        │  │ Table        │  │ Metadata Table│             │
│  ├──────────────┤  ├──────────────┤  ├───────────────┤             │
│  │ id (UUID)    │  │ id (UUID)    │  │ id (UUID)     │             │
│  │ company_id   │  │ job_id       │  │ scrape_type   │             │
│  │ name         │  │ title        │  │ status        │             │
│  │ website      │  │ description  │  │ jobs_scraped  │             │
│  │ email        │  │ job_url      │  │ jobs_stored   │             │
│  │ rating       │  │ source_portal│  │ ai_ml_jobs    │             │
│  │ metadata     │  │ is_ai_ml_job │  │ duration_secs │             │
│  │ created_at   │  │ ai_ml_score  │  │ created_at    │             │
│  └──────────────┘  └──────────────┘  └───────────────┘             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Relationships:                                              │  │
│  │  - Job.company_id → Company.id (Foreign Key)                 │  │
│  │  - Indexes on: is_ai_ml_job, source_portal, company_id       │  │
│  │  - Timestamps for audit trail                                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         ▲
         │
         │ HTTP Response (JSON)
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CLIENT APPLICATIONS                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Web Apps     │  │ Mobile Apps  │  │ Scripts/CLI  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

## Request-Response Flow

### API Request 1: Bulk Scraping

```
CLIENT                          API LAYER                   SCRAPER LAYER                 DATABASE
  │                               │                              │                           │
  │─────POST /bulk-scrape/───────→│                              │                           │
  │ {max_age_hours: 48}           │                              │                           │
  │                               │                              │                           │
  │                      Create ScrapingMetadata────────────────────────────────────────────→│
  │                      (status: in_progress)                   │                           │
  │                               │                              │                           │
  │                      Create ThreadPoolExecutor               │                           │
  │                               │──→ GuruScraper.scrape()      │                           │
  │                               │──→ TruelancerScraper.scrape()│                           │
  │                               │──→ TwineScraper.scrape()     │                           │
  │                               │──→ RemoteWorkScraper.scrape()│                           │
  │                               │   (All Parallel)             │                           │
  │                               │                              │                           │
  │                               │←─ AI/ML filtered jobs        │                           │
  │                               │←─ Statistics                 │                           │
  │                               │                              │                           │
  │                      Get/Create Companies ───────────────────────────────────────────────→│
  │                      Get/Create Jobs      ───────────────────────────────────────────────→│
  │                               │                              │                           │
  │                      Update ScrapingMetadata────────────────────────────────────────────→│
  │                      (status: completed)                     │                           │
  │                               │                              │                           │
  │←──────JSON Response───────────│                              │                           │
  │ {scraping_id: "uuid",        │                              │                           │
  │  data: {...}}                │                              │                           │
  │                               │                              │                           │
```

### API Request 2: Get Jobs with Filters

```
CLIENT                          API LAYER                                    DATABASE
  │                               │                                            │
  │─GET /list/?ai_ml_only=true───→│                                            │
  │                      Query Jobs                                            │
  │                      WHERE is_ai_ml_job=true  ─────────────────────────────→│
  │                               │                                            │
  │                               │←─ Filtered Results (limit 20)──────────────│
  │                               │                                            │
  │                      Format Response                                       │
  │←──────JSON Response───────────│                                            │
  │ {jobs: [{...}, {...}]}        │                                            │
  │                               │                                            │
```

## Data Processing Pipeline

### Job Processing Stages

```
Stage 1: Fetch Raw Data
├─ HTTP GET to job portal
├─ Parse HTML/JSON response
└─ Extract raw job fields

Stage 2: Normalize Data
├─ Clean job title, description
├─ Extract company information
├─ Parse timestamps
└─ Standardize field formats

Stage 3: Classification
├─ Extract text features (title + description)
├─ Match against AI/ML keywords
├─ Calculate confidence score
└─ Apply threshold filter (≥2 keywords OR ≥20% confidence)

Stage 4: Validate & Enrich
├─ Validate URLs
├─ Check for duplicates (by job_id)
├─ Enrich company metadata
└─ Add timestamps

Stage 5: Store in Database
├─ Get or create Company record
├─ Create or update Job record
├─ Update ScrapingMetadata
└─ Commit transaction

Stage 6: Return Response
├─ Format statistics
├─ Include operation ID
├─ Return success/error status
└─ Provide pagination info for GET requests
```

## Concurrency Model

### ThreadPoolExecutor Architecture

```
JobScraperService.scrape_all_portals()
    │
    ├─ ThreadPoolExecutor(max_workers=4)
    │   │
    │   ├─ Thread 1: Guru.com (Concurrent)
    │   │   └─ Scrape, Filter, Wait for completion
    │   │
    │   ├─ Thread 2: Truelancer.com (Concurrent)
    │   │   └─ Scrape, Filter, Wait for completion
    │   │
    │   ├─ Thread 3: Twine.com (Concurrent)
    │   │   └─ Scrape, Filter, Wait for completion
    │   │
    │   └─ Thread 4: RemoteWork.com (Concurrent)
    │       └─ Scrape, Filter, Wait for completion
    │
    └─ as_completed() - Collect results as each thread finishes
        │
        ├─ Handle successful results
        ├─ Handle exceptions
        └─ Aggregate statistics

Time Benefit:
Sequential: 4 seconds (1 + 1 + 1 + 1 sec per portal)
Concurrent: ~1 second (max of individual times, run in parallel)
```

## Error Handling Strategy

```
┌─────────────────────────────────────────┐
│      Error Occurrence                   │
└────────────┬────────────────────────────┘
             │
    ┌────────▼────────┐
    │ Error Type?     │
    └────────┬────────┘
             │
        ┌────┼────────┐────────┐
        │    │        │        │
        ▼    ▼        ▼        ▼
    Network Parsing Validation DB
    Error   Error    Error     Error
        │    │        │        │
        └────┼────────┼────────┘
             │        │
        ┌────▼────────▼──────┐
        │ Log Error          │ (logger.error)
        └────┬───────────────┘
             │
        ┌────▼──────────────────┐
        │ Store Error Details   │ (metadata.error_details)
        │ in ScrapingMetadata   │
        └────┬──────────────────┘
             │
        ┌────▼─────────────────────────┐
        │ Continue Processing?         │
        │ (Non-blocking errors)        │
        └────┬──────────────┬──────────┘
             │ YES          │ NO
             ▼              ▼
        Continue        Set Status to
        Next Job        'failed'
             │              │
             └──────┬───────┘
                    │
             ┌──────▼───────┐
             │ Return Status │
             │ to Client     │
             └───────────────┘
```

## State Transitions for Scraping Metadata

```
        pending
          │
          ├─→ in_progress
          │       │
          │       ├─→ completed (success)
          │       │       │
          │       │       └─→ Store scraped data
          │       │           Update statistics
          │       │           Return results
          │       │
          │       └─→ failed (error)
          │               │
          │               └─→ Log error details
          │                   Store error message
          │                   Return error response
          │
          └─→ failed (immediate error)
                  │
                  └─→ Invalid parameters
                      Invalid configuration
```

## Key Design Patterns

### 1. Service Pattern
```python
# JobScraperService encapsulates business logic
scraper_service = JobScraperService(max_workers=4)
results = scraper_service.scrape_all_portals()
```

### 2. Factory Pattern
```python
# Scraper classes with common interface
scraper = SCRAPER_CLASSES[portal_name]()
jobs = scraper.scrape_jobs()
```

### 3. ORM Pattern
```python
# Django ORM for database operations
company = Company.objects.get_or_create(company_id=id)
job = Job.objects.create(...)
```

### 4. Thread Pool Pattern
```python
# ThreadPoolExecutor for concurrent operations
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(scrape, portal) for portal in portals]
    for future in as_completed(futures):
        result = future.result()
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Bulk Scrape Time** | ~10-15s | 4 portals parallel |
| **Average Jobs/Portal** | 50-100 | Depends on portal response |
| **AI/ML Filter Ratio** | ~30-50% | Percentage of jobs matching filters |
| **Database Insert Time** | ~50-100ms per job | Depends on server |
| **Concurrent Threads** | 4 | ThreadPoolExecutor max_workers |
| **API Response Time (list)** | <200ms | Depends on query complexity |

## Monitoring & Observability

### Logging Levels
```
DEBUG   - Detailed scraping operations
INFO    - Major operations (start/complete)
WARNING - Non-critical issues
ERROR   - Errors that need attention
```

### Metrics Tracked
- Jobs scraped per portal
- AI/ML jobs identified
- Jobs successfully stored
- Error count and types
- Operation duration
- Confidence scores

### Log Files
```
logs/
└── debug.log  # All application logs
```

---

**Document Version**: 1.0
**Last Updated**: January 17, 2026
**Database**: SQLite (db.sqlite3)
