ve# ML Job Scraper - LLD Structure

## Detailed File Structure

```
ml_job_scraper/
│
├── manage.py                           # Django management command entry point
├── db.sqlite3                          # SQLite database (created after migration)
├── requirements.txt                    # Python dependencies
│
├── config/                             # Django project configuration
│   ├── __init__.py                    # Package initialization
│   ├── settings.py                    # Project settings (DEBUG, DATABASES, APPS, etc.)
│   ├── urls.py                        # Root URL dispatcher routing
│   └── wsgi.py                        # WSGI application for deployment
│
├── jobs/                               # Django app for job management
│   ├── __init__.py                    # Package initialization
│   ├── apps.py                        # App configuration (JobsConfig)
│   ├── models.py                      # ORM models: Job, ScrapingMetadata
│   ├── views.py                       # API view functions
│   ├── urls.py                        # URL patterns for jobs app
│   ├── admin.py                       # Django admin configuration (optional)
│   ├── tests.py                       # Unit tests (optional)
│   └── migrations/                    # Database migration files (auto-generated)
│       ├── __init__.py
│       └── 0001_initial.py            # Initial migrations
│
├── companies/                          # Django app for company management
│   ├── __init__.py                    # Package initialization
│   ├── apps.py                        # App configuration (CompaniesConfig)
│   ├── models.py                      # ORM model: Company
│   ├── views.py                       # View functions (currently empty)
│   ├── urls.py                        # URL patterns for companies app
│   └── migrations/                    # Database migration files (auto-generated)
│       └── __init__.py
│
├── scraper/                            # Web scraping module
│   ├── __init__.py                    # Package initialization
│   ├── scraper.py                     # Scraper implementations
│   │   ├── BaseScraper                # Abstract base class
│   │   ├── GuruScraper                # Guru.com implementation
│   │   ├── TruelancerScraper          # Truelancer.com implementation
│   │   ├── TwineScraper               # Twine.com implementation
│   │   ├── RemoteWorkScraper          # RemoteWork.com implementation
│   │   └── JobScraperService          # Main orchestrator
│   └── utils.py                       # Helper functions (optional)
│
├── utils/                              # Utility modules
│   ├── __init__.py                    # Package initialization
│   ├── constants.py                   # AI/ML keywords, configurations (optional)
│   ├── helpers.py                     # Helper functions (optional)
│   └── validators.py                  # Data validators (optional)
│
├── migrations/                         # Root migrations folder
│   └── __init__.py
│
├── logs/                               # Application logs
│   ├── debug.log                      # Debug and error logs
│   └── .gitkeep                       # Keep folder in git
│
├── docs/                               # Documentation
│   ├── SETUP_GUIDE.md                 # Complete setup instructions
│   ├── Architecture_guide.md           # High-level architecture
│   ├── System_Architecture.md          # Detailed system design
│   ├── LLD_Structure.md                # This file - code structure
│   ├── API_Documentation.md            # Complete API reference
│   ├── Complete.md                     # End-to-end guide
│   ├── File_Index.md                   # File organization guide
│   └── WORKFLOW.md                     # Workflow diagrams
│
├── .gitignore                          # Git ignore configuration
├── .env.example                        # Environment variables template (optional)
└── README.md                           # Project README
```

## Module-Level Description

### 1. manage.py

**Purpose**: Django management interface

**Key Functions**:
```python
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    execute_from_command_line(sys.argv)
```

**Commands**:
- `python manage.py runserver` - Start development server
- `python manage.py makemigrations` - Create migrations
- `python manage.py migrate` - Apply migrations
- `python manage.py shell` - Interactive shell
- `python manage.py createsuperuser` - Create admin user

---

### 2. config/settings.py

**Purpose**: Django project configuration

**Key Configurations**:
```python
INSTALLED_APPS = ['django.contrib.contenttypes', 'jobs', 'companies']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
LOGGING = { 'version': 1, 'handlers': {...}, 'loggers': {...} }
```

**Sections**:
- Project metadata (SECRET_KEY, DEBUG)
- Installed apps
- Middleware
- Database configuration
- Logging setup
- Static files configuration

---

### 3. config/urls.py

**Purpose**: Root URL dispatcher

**Routing**:
```python
urlpatterns = [
    path('api/jobs/', include('jobs.urls')),
    path('api/companies/', include('companies.urls')),
]
```

**URL Resolution**:
- `/api/jobs/` → jobs app urls
- `/api/jobs/bulk-scrape/` → jobs.views.bulk_scrape_jobs
- `/api/jobs/realtime-guru/` → jobs.views.realtime_scrape_guru

---

### 4. jobs/models.py

**Purpose**: Database ORM models for jobs

#### Job Model

**Fields**:
```python
class Job(models.Model):
    id: UUIDField                 # Primary key
    job_id: CharField             # Unique job identifier from portal
    title: CharField              # Job title
    description: TextField        # Job description
    job_url: URLField             # Link to job posting
    source_portal: CharField      # 'guru', 'truelancer', 'twine', 'remotework'
    job_type: CharField           # 'Full-time', 'Contract', etc.
    experience_level: CharField   # 'Senior', 'Junior', etc.
    salary_min: DecimalField      # Minimum salary
    salary_max: DecimalField      # Maximum salary
    currency: CharField           # 'USD', 'EUR', etc.
    location: CharField           # Job location
    skills_required: TextField    # Required skills
    status: CharField             # 'active', 'closed', 'expired'
    company: ForeignKey           # Link to Company
    job_posted_at: DateTimeField  # When job was posted
    created_at: DateTimeField     # Record creation time
    updated_at: DateTimeField     # Last update time
    scraped_at: DateTimeField     # When scraped
    is_ai_ml_job: BooleanField    # AI/ML classification flag
    ai_ml_score: FloatField       # Confidence score (0-100)
    metadata: JSONField           # Additional data
```

**Indexes**:
```python
Index(fields=['is_ai_ml_job', 'status'])
Index(fields=['source_portal', 'created_at'])
Index(fields=['company', 'created_at'])
```

**Meta Attributes**:
- `db_table = 'jobs'`
- `ordering = ['-job_posted_at']`

#### ScrapingMetadata Model

**Fields**:
```python
class ScrapingMetadata(models.Model):
    id: UUIDField                 # Primary key
    scrape_type: CharField        # 'bulk', 'realtime'
    status: CharField             # 'pending', 'in_progress', 'completed', 'failed'
    source_portal: CharField      # Portal being scraped
    started_at: DateTimeField     # Start time
    completed_at: DateTimeField   # Completion time
    duration_seconds: IntegerField # Execution duration
    jobs_scraped: IntegerField    # Total jobs found
    jobs_stored: IntegerField     # Jobs stored in DB
    ai_ml_jobs_found: IntegerField# AI/ML jobs identified
    errors_count: IntegerField    # Error count
    error_message: TextField      # Error description
    error_details: JSONField      # Detailed errors
    request_params: JSONField     # Original request parameters
    metadata: JSONField           # Additional tracking info
```

**Indexes**:
```python
Index(fields=['status', 'started_at'])
Index(fields=['source_portal', 'scrape_type'])
```

---

### 5. jobs/views.py

**Purpose**: API endpoint implementations

#### Functions

##### bulk_scrape_jobs(request)
```
Method: POST
URL: /api/jobs/bulk-scrape/
Request: {max_age_hours, include_portals, filter_ai_ml}
Response: {status, scraping_id, data}
Logic:
  1. Parse JSON request
  2. Create ScrapingMetadata record
  3. Initialize JobScraperService
  4. Run scrape_all_portals()
  5. Process results:
     - Get/Create companies
     - Create/Update jobs
     - Update metadata
  6. Return response with stats
```

##### realtime_scrape_guru(request)
```
Method: POST
URL: /api/jobs/realtime-guru/
Request: {job_id}
Response: {status, scraping_id, data}
Logic:
  1. Create ScrapingMetadata (realtime type)
  2. Initialize GuruScraper
  3. Scrape jobs
  4. Filter for AI/ML only
  5. Create new Job records (not update)
  6. Update metadata and return
```

##### get_jobs(request)
```
Method: GET
URL: /api/jobs/list/
Query: ai_ml_only, portal, company_id, limit, offset
Response: {status, data: {total_count, returned, jobs}}
Logic:
  1. Parse query parameters
  2. Build queryset with filters
  3. Apply pagination
  4. Format job data
  5. Return results
```

##### get_scraping_status(request, scraping_id)
```
Method: GET
URL: /api/jobs/scraping-status/{scraping_id}/
Response: {status, data: {scraping_id, status, stats}}
Logic:
  1. Fetch ScrapingMetadata by ID
  2. Format status information
  3. Return operation details
```

---

### 6. companies/models.py

**Purpose**: Database ORM model for companies

#### Company Model

**Fields**:
```python
class Company(models.Model):
    id: UUIDField                 # Primary key
    company_id: CharField         # Unique company identifier
    name: CharField               # Company name (indexed)
    description: TextField        # Company description
    website: URLField             # Company website
    company_size: CharField       # Size category (indexed)
    headquarters_location: CharField # HQ location
    country: CharField            # Country (indexed)
    email: EmailField             # Contact email
    phone: CharField              # Phone number
    rating: FloatField            # Company rating
    review_count: IntegerField    # Number of reviews
    industry: CharField           # Industry classification
    focus_areas: TextField        # AI, ML, Data Science, etc.
    is_verified: BooleanField     # Verification status
    created_at: DateTimeField     # Record creation
    updated_at: DateTimeField     # Last update
    metadata: JSONField           # Additional data
```

**Methods**:
```python
def get_total_jobs_posted():
    """Get total AI/ML jobs posted"""
    return self.jobs.filter(is_ai_ml_job=True).count()

def get_active_ai_ml_jobs():
    """Get active AI/ML jobs"""
    return self.jobs.filter(is_ai_ml_job=True, status='active')
```

---

### 7. scraper/scraper.py

**Purpose**: Web scraping implementation

#### BaseScraper

**Methods**:
```python
class BaseScraper:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
    
    def is_ai_ml_job(title, description) -> (bool, float):
        """
        Classify job as AI/ML
        Returns: (is_ai_ml, confidence_score)
        """
        combined_text = f"{title} {description}".lower()
        matches = sum(1 for keyword in AI_ML_KEYWORDS if keyword in combined_text)
        confidence = (matches / len(AI_ML_KEYWORDS)) * 100
        is_ai_ml = matches >= 2 or confidence >= 20
        return is_ai_ml, confidence
    
    def get_posted_time(posted_str) -> datetime:
        """Parse posted time string"""
        return datetime.now()
    
    def close():
        """Close session"""
        self.session.close()
```

**Constants**:
```python
AI_ML_KEYWORDS = [
    'machine learning', 'deep learning', 'neural network',
    'nlp', 'computer vision', 'ai', 'artificial intelligence',
    'tensorflow', 'pytorch', 'scikit-learn', 'data science',
    # ... more keywords
]
```

#### GuruScraper, TruelancerScraper, TwineScraper, RemoteWorkScraper

**Each implements**:
```python
class XxxScraper(BaseScraper):
    BASE_URL = "https://www.xxx.com"
    
    def scrape_jobs() -> List[Dict]:
        """Fetch and parse jobs from portal"""
        jobs = []
        response = self.session.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        for element in soup.find_all(...):
            job = self._parse_job(element)
            jobs.append(job)
        return jobs
    
    def _parse_job(element) -> Dict:
        """Extract job details from HTML element"""
        return {
            'job_id': ...,
            'title': ...,
            'description': ...,
            'url': ...,
            'company_name': ...,
            'posted_at': ...,
            'source': 'guru'  # or 'truelancer', etc.
        }
```

#### JobScraperService

**Purpose**: Orchestrate scraping from all portals

```python
class JobScraperService:
    SCRAPER_CLASSES = {
        'guru': GuruScraper,
        'truelancer': TruelancerScraper,
        'twine': TwineScraper,
        'remotework': RemoteWorkScraper,
    }
    
    def scrape_all_portals(max_age_hours=48) -> Dict:
        """
        Concurrent scraping from all portals
        Uses ThreadPoolExecutor for parallelization
        
        Returns:
        {
            'total_jobs': 150,
            'ai_ml_jobs': 45,
            'by_portal': {
                'guru': {'total_jobs': 50, 'ai_ml_jobs': 15, 'jobs': [...]},
                ...
            },
            'errors': [],
            'duration_seconds': 12.5
        }
        """
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_portal = {
                executor.submit(self._scrape_portal, portal): portal
                for portal in self.SCRAPER_CLASSES.keys()
            }
            for future in as_completed(future_to_portal):
                portal = future_to_portal[future]
                jobs, ai_ml_count, error = future.result()
                # Aggregate results
        return results
    
    def _scrape_portal(portal_name) -> (List, int, str):
        """
        Single portal scraping
        Returns: (jobs_list, ai_ml_count, error)
        """
        scraper = self.SCRAPER_CLASSES[portal_name]()
        jobs = scraper.scrape_jobs()
        filtered_jobs = [j for j in jobs if is_ai_ml_job(j)]
        return filtered_jobs, len(filtered_jobs), None
```

---

## Class Hierarchy

```
models.Model (Django)
├── Job
│   ├── Fields: job_id, title, description, ...
│   ├── Relations: company (ForeignKey)
│   └── Methods: __str__()
│
├── Company
│   ├── Fields: company_id, name, website, ...
│   └── Methods: get_total_jobs_posted(), get_active_ai_ml_jobs()
│
└── ScrapingMetadata
    ├── Fields: scrape_type, status, jobs_scraped, ...
    └── Methods: __str__()

BaseScraper
├── GuruScraper
├── TruelancerScraper
├── TwineScraper
└── RemoteWorkScraper

JobScraperService
└── Methods: scrape_all_portals(), _scrape_portal()
```

## Function Call Chain

### Bulk Scraping Flow

```
POST /api/jobs/bulk-scrape/
    │
    └─→ bulk_scrape_jobs(request)
            │
            ├─→ json.loads(request.body)
            │
            ├─→ ScrapingMetadata.objects.create(status='in_progress')
            │
            ├─→ JobScraperService(max_workers=4)
            │       │
            │       └─→ scrape_all_portals()
            │           │
            │           ├─→ ThreadPoolExecutor
            │           │   ├─→ _scrape_portal('guru')
            │           │   │   └─→ GuruScraper().scrape_jobs()
            │           │   ├─→ _scrape_portal('truelancer')
            │           │   ├─→ _scrape_portal('twine')
            │           │   └─→ _scrape_portal('remotework')
            │           │
            │           └─→ is_ai_ml_job() filter
            │
            ├─→ For each job:
            │   ├─→ Company.objects.get_or_create()
            │   └─→ Job.objects.update_or_create()
            │
            ├─→ ScrapingMetadata.update(status='completed')
            │
            └─→ JsonResponse(results)
```

## Database Transaction Flow

```
1. START TRANSACTION
   │
2. INSERT INTO companies (...)  # or UPDATE if exists
   │
3. INSERT INTO jobs (...)      # or UPDATE if exists
   │
4. UPDATE scraping_metadata
   │
5. COMMIT

Error Handler:
   └─→ ROLLBACK on exception
```

## 1. Storing Metadata in DB

**ScrapingMetadata Model**:
```python
class ScrapingMetadata(models.Model):
    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    # Operation Tracking
    scrape_type = models.CharField(max_length=20, choices=[
        ('bulk', 'Bulk Scraping'),
        ('realtime', 'Real-time Scraping')
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    jobs_scraped = models.IntegerField(default=0)
    jobs_stored = models.IntegerField(default=0)
    ai_ml_jobs_found = models.IntegerField(default=0)
    total_duration_seconds = models.FloatField(null=True, blank=True)
    
    # Error Tracking
    error_details = models.JSONField(default=dict, blank=True)
    error_count = models.IntegerField(default=0)
    
    # Request Parameters
    request_params = models.JSONField(default=dict, blank=True)
```

**Storage Flow**:
```
1. Create ScrapingMetadata(status='pending')
2. Set status='in_progress' before scraping
3. Update jobs_scraped, jobs_stored during scraping
4. Update error_details if exceptions occur
5. Set status='completed', add completed_at timestamp
6. Return metadata ID for status tracking
```

**Query Examples**:
```python
# Get last scraping operation
last_op = ScrapingMetadata.objects.latest('created_at')

# Get failed operations
failed_ops = ScrapingMetadata.objects.filter(status='failed')

# Get statistics for bulk scraping
bulk_stats = ScrapingMetadata.objects.filter(
    scrape_type='bulk',
    status='completed'
).aggregate(
    total_jobs=Sum('jobs_scraped'),
    total_ai_ml=Sum('ai_ml_jobs_found')
)
```

---

## 2. Sync or Async Job?

**Current Implementation**: Synchronous with Threading (Hybrid)

**Architecture**:
```
API Request
    ↓
Django View (Synchronous)
    ↓
Create ScrapingMetadata (status='pending')
    ↓
ThreadPoolExecutor(max_workers=4)
    ├─→ Thread 1: Scrape Guru.com
    ├─→ Thread 2: Scrape Truelancer.com
    ├─→ Thread 3: Scrape Twine.com
    └─→ Thread 4: Scrape RemoteWork.com
    ↓
as_completed() - Process results as available
    ↓
Store in Database (Synchronous ORM)
    ↓
Update ScrapingMetadata (status='completed')
    ↓
Return JSON Response with metadata_id
```

**Why This Approach?**

✅ **Advantages**:
- Simple: No Celery/RabbitMQ setup needed
- Fast: Direct response to client (not waiting for all scraping)
- Scalable: Thread pool handles concurrent portals
- Reliable: Database transactions ensure consistency
- Suitable for: Development, small to medium deployments

❌ **Limitations**:
- Single server only (not distributed)
- Limited by thread count
- Not suitable for thousands of concurrent requests

**Upgrade to Async?**

When to upgrade to Celery + Redis:
```python
# Celery would look like this:
@app.task
def scrape_all_portals_async():
    # Celery handles task queue
    # Separate worker processes
    # Scales across multiple machines

# API would return immediately:
task_id = scrape_all_portals_async.delay()
return {'task_id': task_id, 'status_url': f'/api/jobs/task-status/{task_id}/'}
```

**Current Flow Diagram**:
```
Bulk Scrape Request
        ↓
Create metadata (pending)
        ↓
Spawn 4 threads (Guru, Truelancer, Twine, RemoteWork)
        ↓
Process results as threads complete (5-30 seconds)
        ↓
Store to DB (5-30 seconds)
        ↓
Return response (total: 10-60 seconds)
        ↓
Client uses metadata_id to check status via GET API
```

---

## 3. Websites That Can Be Scraped Without Auth

**Current Implementations**:

1. **Guru.com** ✅
   - No authentication required
   - Public job listings
   - ScrapeScraper class: `GuruScraper`

2. **Truelancer.com** ✅
   - No authentication required
   - Public job postings
   - Scraper class: `TruelancerScraper`

3. **Twine.com** ✅
   - No authentication required
   - Public jobs available
   - Scraper class: `TwineScraper`

4. **RemoteWork.com** ✅
   - No authentication required
   - Public job board
   - Scraper class: `RemoteWorkScraper`

**Additional Websites (Can Be Added)**:

5. **Upwork.com** (Limited free access)
   - Requires: Basic HTML parsing
   - Limitation: Rate limiting on free tier

6. **Freelancer.com** (Limited free access)
   - Requires: Basic HTML parsing
   - Limitation: Some pages require login

7. **Indeed.com** (No auth, HTML parsing)
   - Requires: BeautifulSoup for dynamic content
   - Limitation: Robots.txt restrictions

8. **LinkedIn Jobs** (API available)
   - Requires: LinkedIn API key
   - Limitation: API rate limits

9. **Stack Overflow Jobs** (Discontinued)
   - Status: Service ended January 2022

10. **GitHub Jobs** (Discontinued)
    - Status: Service ended July 2021

**How to Add New Scraper**:

```python
# In scraper/scraper.py, add new class:
class NewPlatformScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://newplatform.com/jobs"
        
    def scrape_jobs(self, keywords=None, max_age_hours=48):
        """Scrape jobs from new platform"""
        try:
            response = self.session.get(self.base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            for job_element in soup.find_all('div', class_='job-card'):
                job = self._parse_job(job_element)
                if job:
                    jobs.append(job)
                    
            return jobs, len([j for j in jobs if j['is_ai_ml']]), None
        except Exception as e:
            logger.error(f"Error scraping new platform: {e}")
            return [], 0, str(e)
    
    def _parse_job(self, element):
        """Parse single job from new platform"""
        try:
            title = element.find('h2', class_='job-title').text.strip()
            description = element.find('p', class_='job-desc').text.strip()
            is_ai_ml, score = self.is_ai_ml_job(title, description)
            
            return {
                'job_id': element.get('data-id'),
                'title': title,
                'description': description,
                'is_ai_ml_job': is_ai_ml,
                'ai_ml_score': score,
                'source_portal': 'newplatform.com'
            }
        except Exception as e:
            logger.error(f"Error parsing job: {e}")
            return None

# Update JobScraperService.SCRAPER_CLASSES:
SCRAPER_CLASSES = {
    'guru': GuruScraper,
    'truelancer': TruelancerScraper,
    'twine': TwineScraper,
    'remotework': RemoteWorkScraper,
    'newplatform': NewPlatformScraper  # Add here
}
```

---

## 4. List of APIs Required

**Core APIs**:

### 1. **POST /api/jobs/bulk-scrape/**
Purpose: Scrape all 4 portals
```json
Request: {}
Response: {
    "scraping_id": "uuid",
    "status": "in_progress",
    "created_at": "2026-01-17T10:30:00Z",
    "message": "Scraping started"
}
```

### 2. **POST /api/jobs/realtime-guru/**
Purpose: Scrape Guru.com only
```json
Request: {}
Response: {
    "scraping_id": "uuid",
    "status": "in_progress",
    "portal": "guru.com"
}
```

### 3. **GET /api/jobs/list/**
Purpose: Retrieve stored jobs with filters
```json
Request: ?ai_ml_only=true&portal=guru&limit=10&offset=0
Response: {
    "total": 150,
    "count": 10,
    "results": [
        {
            "id": "uuid",
            "job_id": "12345",
            "title": "ML Engineer",
            "is_ai_ml_job": true,
            "ai_ml_score": 95.5
        }
    ]
}
```

### 4. **GET /api/jobs/scraping-status/{id}/**
Purpose: Check operation status
```json
Response: {
    "id": "uuid",
    "status": "completed",
    "jobs_scraped": 250,
    "jobs_stored": 248,
    "ai_ml_jobs_found": 75,
    "total_duration_seconds": 45.2,
    "error_count": 0
}
```

**Optional APIs**:

### 5. **GET /api/jobs/search/**
Purpose: Search jobs by keyword
```json
Request: ?q=tensorflow&ai_ml_only=true
```

### 6. **GET /api/jobs/{id}/**
Purpose: Get single job details
```json
Response: {
    "id": "uuid",
    "title": "ML Engineer",
    "description": "...",
    "company": {
        "id": "uuid",
        "name": "Tech Corp",
        "website": "techcorp.com"
    }
}
```

### 7. **DELETE /api/jobs/old-jobs/**
Purpose: Delete jobs older than N days
```json
Request: {"days": 30}
Response: {"deleted_count": 125}
```

### 8. **GET /api/stats/**
Purpose: Get scraping statistics
```json
Response: {
    "total_jobs": 5420,
    "total_ai_ml": 1650,
    "last_scrape": "2026-01-17T10:00:00Z",
    "portals": {
        "guru": 1350,
        "truelancer": 1200,
        "twine": 950,
        "remotework": 920
    }
}
```

**API Endpoint Summary Table**:

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|----------------|
| `/api/jobs/bulk-scrape/` | POST | Scrape all portals | ~10-60 sec |
| `/api/jobs/realtime-guru/` | POST | Scrape Guru only | ~10-30 sec |
| `/api/jobs/list/` | GET | Get stored jobs | ~100-500 ms |
| `/api/jobs/scraping-status/{id}/` | GET | Check status | ~50-100 ms |
| `/api/jobs/search/` | GET | Search jobs | ~100-300 ms |
| `/api/jobs/{id}/` | GET | Get job details | ~50-100 ms |
| `/api/jobs/old-jobs/` | DELETE | Delete old jobs | ~1-5 sec |
| `/api/stats/` | GET | Get statistics | ~100-200 ms |

---

## 5. In Which Flow What Will Be the Request Method?

**Complete Request Flow Diagrams**:

### Flow A: Bulk Scraping Workflow (POST → GET)

```
STEP 1: Client Initiates Scraping (POST)
    ┌─────────────────────────────────────┐
    │ POST /api/jobs/bulk-scrape/         │
    │ Content-Type: application/json      │
    │ Body: {}                            │
    └────────────┬────────────────────────┘
                 ↓
    RESPONSE (Immediate - 200 OK):
    {
        "scraping_id": "a1b2c3d4-e5f6...",
        "status": "in_progress",
        "created_at": "2026-01-17T10:30:00Z",
        "message": "Scraping started for 4 portals"
    }

STEP 2: Client Polls Status (GET)
    ┌─────────────────────────────────────────────────────────┐
    │ GET /api/jobs/scraping-status/a1b2c3d4-e5f6.../        │
    └────────────┬────────────────────────────────────────────┘
                 ↓
    RESPONSE (Poll every 5 seconds):
    {
        "id": "a1b2c3d4-e5f6...",
        "status": "in_progress",
        "jobs_scraped": 125,
        "jobs_stored": 120,
        "ai_ml_jobs_found": 35,
        "total_duration_seconds": 15.2
    }

STEP 3: Client Retrieves Results (GET)
    ┌─────────────────────────────────────┐
    │ GET /api/jobs/list/?ai_ml_only=true │
    │ &limit=20&offset=0                  │
    └────────────┬────────────────────────┘
                 ↓
    RESPONSE (200 OK - All data):
    {
        "total": 350,
        "count": 20,
        "results": [
            {
                "id": "job-uuid-1",
                "title": "ML Engineer",
                "is_ai_ml_job": true,
                "ai_ml_score": 92.5
            },
            ...
        ]
    }
```

### Flow B: Real-time Guru Scraping (POST)

```
STEP 1: Client Requests Real-time Scraping (POST)
    ┌──────────────────────────────────────┐
    │ POST /api/jobs/realtime-guru/        │
    │ Content-Type: application/json       │
    │ Body: {}                             │
    └────────────┬──────────────────────────┘
                 ↓
    RESPONSE (Immediate - 200 OK):
    {
        "scraping_id": "guru-b2c3d4e5-f6g7...",
        "status": "in_progress",
        "portal": "guru.com",
        "started_at": "2026-01-17T10:35:00Z"
    }

STEP 2: Poll Status (GET)
    ┌────────────────────────────────────────────────┐
    │ GET /api/jobs/scraping-status/guru-b2c3d4e5... │
    └────────────┬─────────────────────────────────────┘
                 ↓
    RESPONSE:
    {
        "status": "completed",
        "jobs_scraped": 85,
        "jobs_stored": 82,
        "ai_ml_jobs_found": 28,
        "total_duration_seconds": 22.3
    }

STEP 3: Get Guru-specific Jobs (GET)
    ┌──────────────────────────────────────────────┐
    │ GET /api/jobs/list/?portal=guru&limit=50     │
    └────────────┬───────────────────────────────────┘
                 ↓
    RESPONSE: List of Guru.com jobs
```

### Flow C: Search Jobs (GET)

```
GET /api/jobs/search/
    ├─→ Query Parameter: q=tensorflow
    ├─→ Query Parameter: ai_ml_only=true
    ├─→ Query Parameter: portal=guru
    ├─→ Query Parameter: limit=20
    └─→ Query Parameter: offset=0

    ↓ (Database Query)
    
SELECT * FROM jobs 
WHERE (title LIKE '%tensorflow%' OR description LIKE '%tensorflow%')
  AND is_ai_ml_job = true
  AND source_portal = 'guru'
LIMIT 20 OFFSET 0;

    ↓
    
RESPONSE (200 OK):
{
    "total": 45,
    "count": 20,
    "results": [
        {
            "id": "job-uuid",
            "title": "TensorFlow ML Engineer",
            "is_ai_ml_job": true,
            "ai_ml_score": 98.5
        }
    ]
}
```

### Flow D: Get Single Job Details (GET)

```
GET /api/jobs/uuid-12345/
    
    ↓ (Database Query)
    
SELECT jobs.*, companies.* 
FROM jobs 
LEFT JOIN companies ON jobs.company_id = companies.id
WHERE jobs.id = 'uuid-12345';

    ↓
    
RESPONSE (200 OK):
{
    "id": "uuid-12345",
    "job_id": "guru-job-5678",
    "title": "ML Engineer - Remote",
    "description": "Looking for experienced ML Engineer...",
    "is_ai_ml_job": true,
    "ai_ml_score": 92.3,
    "source_portal": "guru.com",
    "company": {
        "id": "company-uuid",
        "name": "TechCorp AI",
        "website": "https://techcorp.com",
        "rating": 4.8
    },
    "job_posted_at": "2026-01-15T08:30:00Z",
    "created_at": "2026-01-17T10:32:00Z"
}
```

### Flow E: Get Statistics (GET)

```
GET /api/stats/

    ↓ (Database Aggregation)
    
SELECT 
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN is_ai_ml_job = true THEN 1 END) as ai_ml_jobs,
    source_portal,
    MAX(created_at) as last_updated
FROM jobs
GROUP BY source_portal;

    ↓
    
RESPONSE (200 OK):
{
    "total_jobs": 5420,
    "total_ai_ml_jobs": 1650,
    "ai_ml_percentage": 30.4,
    "last_scrape": "2026-01-17T10:30:00Z",
    "portals": {
        "guru.com": {
            "total": 1350,
            "ai_ml": 450,
            "percentage": 33.3
        },
        "truelancer.com": {
            "total": 1200,
            "ai_ml": 350,
            "percentage": 29.2
        },
        "twine.com": {
            "total": 950,
            "ai_ml": 280,
            "percentage": 29.5
        },
        "remotework.com": {
            "total": 920,
            "ai_ml": 270,
            "percentage": 29.3
        }
    }
}
```

**Request Method Summary Table**:

| Scenario | Method | Endpoint | When to Use |
|----------|--------|----------|-------------|
| **Start bulk scraping** | POST | `/api/jobs/bulk-scrape/` | User clicks "Scrape All" button |
| **Start real-time scraping** | POST | `/api/jobs/realtime-guru/` | User wants fresh Guru data |
| **Check operation status** | GET | `/api/jobs/scraping-status/{id}/` | Poll after POST to track progress |
| **List stored jobs** | GET | `/api/jobs/list/` | Load jobs table in UI |
| **Search jobs** | GET | `/api/jobs/search/` | User enters search term |
| **Get job details** | GET | `/api/jobs/{id}/` | User clicks on a job card |
| **Get statistics** | GET | `/api/stats/` | Display dashboard metrics |
| **Delete old jobs** | DELETE | `/api/jobs/old-jobs/` | Cleanup jobs older than N days |

---

## Performance Optimizations

1. **Database Indexes**
   ```
   CREATE INDEX idx_job_ai_ml_status ON jobs(is_ai_ml_job, status)
   CREATE INDEX idx_job_portal_date ON jobs(source_portal, created_at)
   ```

2. **Concurrent Scraping**
   ```
   ThreadPoolExecutor(max_workers=4) - 4 portals in parallel
   ```

3. **Connection Pooling**
   ```
   requests.Session() - Reuse HTTP connections
   ```

4. **Query Optimization**
   ```
   select_related() - Avoid N+1 queries
   prefetch_related() - For reverse relations
   ```

---

**Document Version**: 1.0
**Last Updated**: January 17, 2026
