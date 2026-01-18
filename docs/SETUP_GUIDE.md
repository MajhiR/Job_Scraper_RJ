# ML Job Scraper - Setup Guide

Complete step-by-step guide to set up and run the ML Job Scraper application locally.

## Prerequisites

- **Python 3.9+** installed on your machine
- **Windows PowerShell** or Command Prompt
- **Git** (optional, for version control)
- **VS Code** (optional, but recommended)

## Step 1: Create Virtual Environment

### 1.1 Navigate to Project Directory

```bash
cd d:\web_scraping
```

### 1.2 Create Virtual Environment

```bash
# On Windows PowerShell
python -m venv ml_job_env

# Activate the virtual environment
.\ml_job_env\Scripts\Activate.ps1

# Note: If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

After activation, you should see `(ml_job_env)` prefix in your terminal.

### 1.3 Verify Python and Pip

```bash
python --version
pip --version
```

## Step 2: Install Dependencies

### 2.1 Navigate to Project Folder

```bash
cd d:\web_scraping\ml_job_scraper
```

### 2.2 Install Requirements

```bash
pip install -r requirements.txt
```

This will install:
- **Django 4.2.8** - Web framework
- **requests** - HTTP library for web scraping
- **beautifulsoup4** - HTML parsing
- **lxml** - XML/HTML processing
- **selenium** - Browser automation (optional, for JavaScript-heavy sites)
- **And other dependencies listed in requirements.txt**

## Step 3: Initialize Database

### 3.1 Create Migrations

```bash
python manage.py makemigrations
```

You should see output like:
```
Migrations for 'jobs':
  jobs/migrations/0001_initial.py
    - Create model Job
    - Create model ScrapingMetadata
```

### 3.2 Apply Migrations

```bash
python manage.py migrate
```

This creates the SQLite database (`db.sqlite3`) with all tables.

### 3.3 Verify Database

Check that `db.sqlite3` file was created in the project root directory:
```bash
ls db.sqlite3  # Or dir db.sqlite3 on Command Prompt
```

## Step 4: Run Django Development Server

### 4.1 Start the Server

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 4.2 Server is Running!

The API is now accessible at:
- **Base URL**: `http://127.0.0.1:8000`
- **API Base**: `http://127.0.0.1:8000/api`

## Step 5: Test the APIs

### 5.1 Bulk Scraping API

**Endpoint**: `POST http://127.0.0.1:8000/api/jobs/bulk-scrape/`

**Request Body** (JSON):
```json
{
  "max_age_hours": 48,
  "include_portals": ["guru", "truelancer", "twine", "remotework"],
  "filter_ai_ml": true
}
```

**Using cURL**:
```bash
curl -X POST http://127.0.0.1:8000/api/jobs/bulk-scrape/ ^
  -H "Content-Type: application/json" ^
  -d "{\"max_age_hours\": 48, \"filter_ai_ml\": true}"
```

**Using PowerShell**:
```powershell
$body = @{
    max_age_hours = 48
    filter_ai_ml = $true
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/bulk-scrape/" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

### 5.2 Real-time Guru Scraping API

**Endpoint**: `POST http://127.0.0.1:8000/api/jobs/realtime-guru/`

**Request Body** (JSON):
```json
{
  "job_id": "optional_job_id"
}
```

**Using PowerShell**:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/realtime-guru/" `
  -Method POST `
  -ContentType "application/json" `
  -Body "{}"
```

### 5.3 Get Scraping Status

**Endpoint**: `GET http://127.0.0.1:8000/api/jobs/scraping-status/<scraping_id>/`

After running bulk scrape, you'll get a `scraping_id` in response. Use it to check status:

```powershell
$scrapingId = "returned-from-bulk-scrape-response"
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/scraping-status/$scrapingId/" `
  -Method GET
```

### 5.4 List Stored Jobs

**Endpoint**: `GET http://127.0.0.1:8000/api/jobs/list/`

**Query Parameters**:
- `ai_ml_only=true` - Filter only AI/ML jobs
- `portal=guru` - Filter by specific portal
- `limit=20` - Number of results
- `offset=0` - Pagination offset

```bash
# Get AI/ML jobs
curl "http://127.0.0.1:8000/api/jobs/list/?ai_ml_only=true&limit=10"

# Get jobs from Guru
curl "http://127.0.0.1:8000/api/jobs/list/?portal=guru&limit=10"
```

## Step 6: Project Structure

```
ml_job_scraper/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database (created after migration)
├── requirements.txt         # Python dependencies
│
├── config/                  # Django configuration
│   ├── settings.py         # Settings and database config
│   ├── urls.py             # URL routing
│   ├── wsgi.py             # WSGI configuration
│   └── __init__.py
│
├── jobs/                    # Jobs application
│   ├── models.py           # Job and ScrapingMetadata models
│   ├── views.py            # API endpoints
│   ├── urls.py             # URL patterns
│   ├── apps.py             # App configuration
│   └── __init__.py
│
├── companies/              # Companies application
│   ├── models.py           # Company model
│   ├── views.py            # (empty for now)
│   ├── urls.py
│   ├── apps.py
│   └── __init__.py
│
├── scraper/                # Web scraping logic
│   ├── scraper.py          # Scraper classes with thread pool
│   └── __init__.py
│
├── utils/                  # Utility functions
│   └── __init__.py
│
├── migrations/             # Database migrations
│   └── __init__.py
│
├── logs/                   # Log files
│   └── debug.log
│
└── docs/                   # Documentation
    ├── Architecture_guide.md
    ├── System_Architecture.md
    ├── LLD_Structure.md
    └── Complete.md
```

## Step 7: View Database Content

### 7.1 Using Django Shell

```bash
python manage.py shell

# In the shell:
from jobs.models import Job, ScrapingMetadata
from companies.models import Company

# Get all jobs
jobs = Job.objects.all()
print(f"Total jobs: {jobs.count()}")

# Get AI/ML jobs
ai_ml_jobs = Job.objects.filter(is_ai_ml_job=True)
print(f"AI/ML jobs: {ai_ml_jobs.count()}")

# Get scraping history
scrapings = ScrapingMetadata.objects.all().order_by('-started_at')
for scrape in scrapings:
    print(f"{scrape.scrape_type} - {scrape.status}: {scrape.jobs_stored} jobs stored")

# Exit shell
exit()
```

### 7.2 Using SQLite Browser

Download **DB Browser for SQLite** (free) to view the database visually.

## Step 8: Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution**: Make sure virtual environment is activated:
```bash
.\ml_job_env\Scripts\Activate.ps1
```

### Issue: "Port 8000 is already in use"

**Solution**: Use a different port:
```bash
python manage.py runserver 8001
```

### Issue: "No such table: jobs_job"

**Solution**: Run migrations:
```bash
python manage.py migrate
```

### Issue: Scraper not finding jobs

**Solution**: Some websites have anti-scraping measures. Try:
1. Check internet connection
2. Wait a few seconds and retry
3. Check logs in `logs/debug.log`
4. Verify website structure hasn't changed

## Step 9: Common Commands

```bash
# Activate virtual environment
.\ml_job_env\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Run Django development server
python manage.py runserver

# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Open Django shell
python manage.py shell

# Create superuser (for admin panel)
python manage.py createsuperuser

# Reset database (delete all data)
# 1. Delete db.sqlite3
# 2. Run: python manage.py migrate
```

## Step 10: Production Deployment

For production use:

1. **Set DEBUG = False** in `config/settings.py`
2. **Change SECRET_KEY** to a secure random value
3. **Use a production database** (PostgreSQL, MySQL)
4. **Use a production server** (Gunicorn, uWSGI)
5. **Use HTTPS** and SSL certificates
6. **Configure ALLOWED_HOSTS** for your domain
7. **Set up environment variables** for sensitive data

## Next Steps

- Read [Architecture_guide.md](./docs/Architecture_guide.md) for system overview
- Check [System_Architecture.md](./docs/System_Architecture.md) for detailed architecture
- Review [LLD_Structure.md](./docs/LLD_Structure.md) for code structure
- See [API_Documentation.md](./docs/API_Documentation.md) for complete API reference

---

**Last Updated**: January 17, 2026
**Django Version**: 4.2.8
**Python Version**: 3.9+
