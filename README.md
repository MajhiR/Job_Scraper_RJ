# ML Job Scraper - AI/ML Job Aggregation System

A Django-based web scraping application that automatically collects AI/ML job listings from multiple job portals, filters them using keyword classification, and stores them in a SQLite database.

## 🎯 Features

- **Multi-portal Scraping**: Scrapes from Guru.com, Truelancer.com, Twine.com, and RemoteWork.com
- **Concurrent Execution**: Uses ThreadPoolExecutor for 4 parallel scraping threads
- **AI/ML Classification**: Keyword-based filtering with confidence scoring
- **RESTful APIs**: Two main APIs for bulk and real-time scraping
- **Complete Metadata Tracking**: Detailed scraping operation history
- **Error Handling**: Graceful error recovery and comprehensive logging
- **SQLite Database**: Lightweight, portable local database

## 📋 Quick Start

### Prerequisites
- Python 3.9 or higher
- Windows PowerShell or Command Prompt

### Installation (5 minutes)

```bash
# 1. Navigate to project
cd d:\web_scraping\ml_job_scraper

# 2. Create virtual environment
python -m venv ml_job_env
.\ml_job_env\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python manage.py makemigrations
python manage.py migrate

# 5. Start server
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

## 🚀 API Usage

### 1. Bulk Scrape All Portals (POST)

```bash
curl -X POST http://127.0.0.1:8000/api/jobs/bulk-scrape/ \
  -H "Content-Type: application/json" \
  -d '{"max_age_hours": 48, "filter_ai_ml": true}'
```

**Response**:
```json
{
  "status": "success",
  "scraping_id": "550e8400-e29b-41d4-a716-446655440000",
  "data": {
    "total_jobs": 312,
    "ai_ml_jobs": 87,
    "stored_jobs": 82,
    "duration_seconds": 14.3
  }
}
```

### 2. Real-time Guru.com Scraping (POST)

```bash
curl -X POST http://127.0.0.1:8000/api/jobs/realtime-guru/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 3. Get Stored Jobs (GET)

```bash
curl "http://127.0.0.1:8000/api/jobs/list/?ai_ml_only=true&limit=10&portal=guru"
```

### 4. Check Scraping Status (GET)

```bash
curl "http://127.0.0.1:8000/api/jobs/scraping-status/550e8400-e29b-41d4-a716-446655440000/"
```

## 📁 Project Structure

```
ml_job_scraper/
├── config/              # Django configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── jobs/                # Job management app
│   ├── models.py       # Job & ScrapingMetadata models
│   ├── views.py        # API endpoints
│   └── urls.py
├── companies/           # Company management app
│   └── models.py       # Company model
├── scraper/             # Web scraping module
│   └── scraper.py      # Scraper implementations
├── docs/                # Documentation
│   ├── SETUP_GUIDE.md
│   ├── Architecture_guide.md
│   ├── System_Architecture.md
│   ├── LLD_Structure.md
│   ├── Complete.md
│   ├── File_Index.md
│   └── API_Documentation.md
├── manage.py            # Django management
├── requirements.txt     # Dependencies
└── db.sqlite3          # SQLite database (created after migration)
```

## 🏗️ Architecture

### Component Diagram
```
Request → Django API Layer → JobScraperService → ThreadPoolExecutor
                                    ↓
                    4 Concurrent Scrapers (Guru, Truelancer, Twine, RemoteWork)
                                    ↓
                            AI/ML Keyword Filter
                                    ↓
                        Store in SQLite Database
                                    ↓
                            Return Response
```

## 🗄️ Database Schema

### Job Model
- `job_id` (unique identifier)
- `title`, `description`, `job_url`
- `source_portal` (guru, truelancer, twine, remotework)
- `company_id` (foreign key)
- `is_ai_ml_job` (boolean flag)
- `ai_ml_score` (0-100 confidence)
- Timestamps: `job_posted_at`, `created_at`, `updated_at`

### Company Model
- `company_id` (unique identifier)
- `name`, `website`, `email`, `phone`
- `company_size`, `country`, `industry`
- `rating`, `review_count`

### ScrapingMetadata Model
- Tracks all scraping operations
- Status: pending, in_progress, completed, failed
- Statistics: jobs_scraped, jobs_stored, ai_ml_jobs_found
- Error tracking and request parameters

## 🤖 AI/ML Classification

Uses keyword-based matching with ~25 keywords:
- Core: machine learning, deep learning, neural network, AI
- Frameworks: TensorFlow, PyTorch, scikit-learn
- Roles: Data Scientist, ML Engineer, AI Engineer
- Techniques: NLP, Computer Vision, Classification, Regression
- Advanced: LLM, GPT, Generative, Transformer, BERT

**Threshold**: Job classified as AI/ML if ≥2 keywords matched OR confidence ≥20%

## 📚 Documentation

### For New Developers
1. Read [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Complete setup instructions
2. Read [API_Documentation.md](docs/API_Documentation.md) - All API endpoints with examples

### For Architects
1. Read [Architecture_guide.md](docs/Architecture_guide.md) - System overview
2. Read [System_Architecture.md](docs/System_Architecture.md) - Detailed design

### For Developers
1. Read [LLD_Structure.md](docs/LLD_Structure.md) - Code structure and modules
2. Read [File_Index.md](docs/File_Index.md) - File organization guide

### For Complete Reference
- [Complete.md](docs/Complete.md) - Comprehensive end-to-end guide

## ⚙️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Django 4.2 |
| **Language** | Python 3.9+ |
| **Database** | SQLite 3 |
| **Web Scraping** | BeautifulSoup4, Requests |
| **HTML Parser** | lxml |
| **Concurrency** | ThreadPoolExecutor |
| **ORM** | Django ORM |

## 🔧 Common Commands

```bash
# Start development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Interactive shell
python manage.py shell

# Check database
python manage.py dbshell

# Create admin user
python manage.py createsuperuser

# Run tests
python manage.py test
```

## 📊 API Response Examples

### Bulk Scrape Response
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
    "by_portal": {
      "guru": {"total_jobs": 78, "ai_ml_jobs": 22},
      "truelancer": {"total_jobs": 65, "ai_ml_jobs": 18},
      "twine": {"total_jobs": 92, "ai_ml_jobs": 28},
      "remotework": {"total_jobs": 77, "ai_ml_jobs": 19}
    },
    "errors": null
  }
}
```

### Get Jobs Response
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
        "description": "Build ML models with TensorFlow...",
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

## 🐛 Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Not Found
```bash
python manage.py migrate
```

### No Scraper Results
1. Check internet connection
2. Verify portal website is accessible
3. Check logs in `logs/debug.log`
4. Some portals have anti-scraping measures

### Virtual Environment Issues
```bash
# Deactivate
deactivate

# Reactivate
.\ml_job_env\Scripts\Activate.ps1
```

## 📈 Performance

- **Bulk Scraping**: ~14-20 seconds for all 4 portals
- **Jobs per Portal**: 50-100 jobs typically
- **AI/ML Filter Ratio**: 25-40% of jobs match AI/ML criteria
- **Concurrent Threads**: 4 (ThreadPoolExecutor)
- **Database Queries**: Optimized with indexes

## 🚀 Scaling

### Current (Development)
- Single machine
- SQLite database
- 4 concurrent threads

### Production Upgrades
- Use PostgreSQL instead of SQLite
- Deploy with Gunicorn/uWSGI
- Add Redis caching
- Use Celery for scheduled jobs
- Implement message queue (RabbitMQ)
- Add rate limiting and authentication

## 📝 API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/jobs/bulk-scrape/` | Scrape all portals |
| POST | `/api/jobs/realtime-guru/` | Real-time Guru scraping |
| GET | `/api/jobs/list/` | Retrieve stored jobs |
| GET | `/api/jobs/scraping-status/{id}/` | Check operation status |

## 🔐 Security Notes

**Development Mode**:
- DEBUG = True
- CSRF protection disabled for APIs
- No authentication required

**For Production**:
- Set DEBUG = False
- Enable CSRF protection
- Implement token authentication
- Use HTTPS/SSL
- Set secure SECRET_KEY
- Configure ALLOWED_HOSTS

## 📧 Error Handling

The system gracefully handles:
- Network timeouts
- Portal structure changes
- HTML parsing errors
- Database constraint violations
- Invalid data format

All errors are logged to `logs/debug.log` with full details.

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library](https://requests.readthedocs.io/)
- [Python Threading](https://docs.python.org/3/library/threading.html)

## 📄 License

This project is provided as-is for educational and development purposes.

## 👨‍💻 Contributing

To add new features:
1. Create a new branch
2. Make changes
3. Update relevant documentation
4. Test thoroughly
5. Submit pull request

## 📞 Support

For issues or questions:
1. Check [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) troubleshooting section
2. Review [docs/Complete.md](docs/Complete.md) FAQ section
3. Check logs in `logs/debug.log`

---

**Version**: 1.0
**Last Updated**: January 17, 2026
**Status**: Development (Beta)
