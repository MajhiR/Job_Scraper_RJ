# ML Job Scraper - API Documentation

Complete API reference with examples for all endpoints.

---

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Request/Response Format](#requestresponse-format)
4. [Bulk Scrape Endpoint](#bulk-scrape-endpoint)
5. [Real-time Guru Endpoint](#real-time-guru-endpoint)
6. [Get Jobs Endpoint](#get-jobs-endpoint)
7. [Scraping Status Endpoint](#scraping-status-endpoint)
8. [Error Responses](#error-responses)
9. [Rate Limiting](#rate-limiting)
10. [Examples](#examples)

---

## API Overview

### Base URL
```
http://127.0.0.1:8000/api
```

### API Version
- Current Version: 1.0
- Status: Development (Beta)

### Available Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/jobs/bulk-scrape/` | Scrape all portals |
| POST | `/jobs/realtime-guru/` | Real-time Guru scraping |
| GET | `/jobs/list/` | Retrieve stored jobs |
| GET | `/jobs/scraping-status/{id}/` | Check operation status |

---

## Authentication

Currently **NO authentication required** (development mode).

For production, implement:
```python
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
```

---

## Request/Response Format

### Content-Type
```
Content-Type: application/json
```

### Request Format
All request bodies must be valid JSON.

### Response Format
```json
{
  "status": "success" | "error",
  "message": "Operation summary",
  "data": { /* Operation-specific data */ },
  "scraping_id": "UUID" /* Only for scraping operations */
}
```

### Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

## Bulk Scrape Endpoint

Scrape all configured portals concurrently.

### Endpoint
```
POST /api/jobs/bulk-scrape/
```

### Description
Initiates a bulk scraping operation across all configured job portals (Guru.com, Truelancer.com, Twine.com, RemoteWork.com). Results are filtered for AI/ML jobs and stored in the database.

### Request

#### Headers
```
Content-Type: application/json
```

#### Body
```json
{
  "max_age_hours": 48,
  "include_portals": ["guru", "truelancer", "twine", "remotework"],
  "filter_ai_ml": true
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `max_age_hours` | integer | No | 48 | Only include jobs posted within last N hours |
| `include_portals` | array | No | All | Which portals to scrape |
| `filter_ai_ml` | boolean | No | true | Filter for AI/ML jobs only |

### Response (Success)

#### Status Code: 200 OK

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
      "guru": {
        "total_jobs": 78,
        "ai_ml_jobs": 22
      },
      "truelancer": {
        "total_jobs": 65,
        "ai_ml_jobs": 18
      },
      "twine": {
        "total_jobs": 92,
        "ai_ml_jobs": 28
      },
      "remotework": {
        "total_jobs": 77,
        "ai_ml_jobs": 19
      }
    },
    "errors": null
  }
}
```

### Response (Error)

#### Status Code: 500 Internal Server Error

```json
{
  "status": "error",
  "message": "Failed to connect to Guru.com: Connection timeout"
}
```

### Examples

#### Using cURL (Windows PowerShell)
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

$result = $response.Content | ConvertFrom-Json
Write-Host "Scraping ID: $($result.scraping_id)"
Write-Host "Total Jobs: $($result.data.total_jobs)"
Write-Host "AI/ML Jobs: $($result.data.ai_ml_jobs)"
```

#### Using Python
```python
import requests
import json

url = "http://127.0.0.1:8000/api/jobs/bulk-scrape/"
payload = {
    "max_age_hours": 48,
    "include_portals": ["guru", "truelancer", "twine", "remotework"],
    "filter_ai_ml": True
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Scraping ID: {result['scraping_id']}")
print(f"Total Jobs: {result['data']['total_jobs']}")
print(f"AI/ML Jobs: {result['data']['ai_ml_jobs']}")
print(f"Duration: {result['data']['duration_seconds']}s")
```

#### Using JavaScript/Fetch
```javascript
const url = "http://127.0.0.1:8000/api/jobs/bulk-scrape/";
const payload = {
    max_age_hours: 48,
    include_portals: ["guru", "truelancer", "twine", "remotework"],
    filter_ai_ml: true
};

fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify(payload)
})
.then(response => response.json())
.then(data => {
    console.log("Scraping ID:", data.scraping_id);
    console.log("Total Jobs:", data.data.total_jobs);
    console.log("AI/ML Jobs:", data.data.ai_ml_jobs);
});
```

---

## Real-time Guru Endpoint

Real-time scraping from Guru.com only.

### Endpoint
```
POST /api/jobs/realtime-guru/
```

### Description
Fetches current job listings from Guru.com in real-time, filters for AI/ML jobs, and stores them as new records in the database.

### Request

#### Headers
```
Content-Type: application/json
```

#### Body
```json
{
  "job_id": "optional_specific_job_id"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `job_id` | string | No | Specific job ID to fetch (if provided) |

### Response (Success)

#### Status Code: 200 OK

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

### Examples

#### Using PowerShell
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/realtime-guru/" `
  -Method POST `
  -ContentType "application/json" `
  -Body "{}"

$result = $response.Content | ConvertFrom-Json
Write-Host "Jobs Stored: $($result.data.jobs_stored)"
Write-Host "AI/ML Jobs: $($result.data.ai_ml_jobs)"
```

#### Using Python
```python
import requests

url = "http://127.0.0.1:8000/api/jobs/realtime-guru/"
response = requests.post(url, json={})
result = response.json()

print(f"Jobs Stored: {result['data']['jobs_stored']}")
print(f"AI/ML Jobs: {result['data']['ai_ml_jobs']}")
```

---

## Get Jobs Endpoint

Retrieve stored jobs with filtering.

### Endpoint
```
GET /api/jobs/list/
```

### Description
Retrieves jobs from the database with optional filtering by AI/ML classification, portal, company, and pagination.

### Request

#### Headers
```
Accept: application/json
```

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `ai_ml_only` | boolean | No | true | Filter only AI/ML jobs |
| `portal` | string | No | - | Filter by portal (guru, truelancer, twine, remotework) |
| `company_id` | UUID | No | - | Filter by company UUID |
| `limit` | integer | No | 20 | Number of results (max 100) |
| `offset` | integer | No | 0 | Pagination offset |

### Response (Success)

#### Status Code: 200 OK

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
        "description": "We are looking for an experienced ML engineer to build...",
        "job_url": "https://guru.com/jobs/12345",
        "source_portal": "guru",
        "company": {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "name": "Tech Company Inc"
        },
        "ai_ml_score": 95.5,
        "job_posted_at": "2026-01-16T10:30:00Z",
        "created_at": "2026-01-17T08:15:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "job_id": "truelancer_67890",
        "title": "Data Scientist - NLP",
        "description": "Build NLP models using Python and TensorFlow...",
        "job_url": "https://truelancer.com/project/67890",
        "source_portal": "truelancer",
        "company": {
          "id": "550e8400-e29b-41d4-a716-446655440003",
          "name": "AI Startup LLC"
        },
        "ai_ml_score": 88.2,
        "job_posted_at": "2026-01-17T14:20:00Z",
        "created_at": "2026-01-17T14:25:00Z"
      }
    ]
  }
}
```

### Examples

#### Get all AI/ML jobs from Guru
```
GET /api/jobs/list/?ai_ml_only=true&portal=guru&limit=10
```

#### Using PowerShell
```powershell
$uri = "http://127.0.0.1:8000/api/jobs/list/?ai_ml_only=true&portal=guru&limit=5"
$response = Invoke-WebRequest -Uri $uri -Method GET
$result = $response.Content | ConvertFrom-Json

foreach ($job in $result.data.jobs) {
    Write-Host "Title: $($job.title)"
    Write-Host "Company: $($job.company.name)"
    Write-Host "URL: $($job.job_url)"
    Write-Host "---"
}
```

#### Using Python
```python
import requests

url = "http://127.0.0.1:8000/api/jobs/list/"
params = {
    "ai_ml_only": True,
    "portal": "guru",
    "limit": 10,
    "offset": 0
}

response = requests.get(url, params=params)
result = response.json()

print(f"Total Jobs: {result['data']['total_count']}")
print(f"Returned: {result['data']['returned']}")

for job in result['data']['jobs']:
    print(f"{job['title']} - {job['company']['name']}")
```

---

## Scraping Status Endpoint

Check the status of a scraping operation.

### Endpoint
```
GET /api/jobs/scraping-status/{scraping_id}/
```

### Description
Retrieves detailed information about a specific scraping operation, including status, statistics, and error details.

### Request

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `scraping_id` | UUID | Yes | ID returned from bulk-scrape or realtime-guru |

### Response (Success)

#### Status Code: 200 OK

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

### Response (Not Found)

#### Status Code: 404 Not Found

```json
{
  "status": "error",
  "message": "Scraping operation not found"
}
```

### Examples

#### Using PowerShell
```powershell
$scrapingId = "550e8400-e29b-41d4-a716-446655440000"
$uri = "http://127.0.0.1:8000/api/jobs/scraping-status/$scrapingId/"

$response = Invoke-WebRequest -Uri $uri -Method GET
$result = $response.Content | ConvertFrom-Json

Write-Host "Status: $($result.data.status)"
Write-Host "Jobs Scraped: $($result.data.jobs_scraped)"
Write-Host "Jobs Stored: $($result.data.jobs_stored)"
Write-Host "Duration: $($result.data.duration_seconds)s"
```

#### Using Python
```python
import requests

scraping_id = "550e8400-e29b-41d4-a716-446655440000"
url = f"http://127.0.0.1:8000/api/jobs/scraping-status/{scraping_id}/"

response = requests.get(url)
result = response.json()

print(f"Status: {result['data']['status']}")
print(f"Jobs Scraped: {result['data']['jobs_scraped']}")
print(f"Jobs Stored: {result['data']['jobs_stored']}")
print(f"AI/ML Jobs: {result['data']['ai_ml_jobs_found']}")
```

---

## Error Responses

### Error Types

#### 400 Bad Request
```json
{
  "status": "error",
  "message": "Invalid JSON in request body"
}
```

#### 404 Not Found
```json
{
  "status": "error",
  "message": "Scraping operation not found"
}
```

#### 500 Server Error
```json
{
  "status": "error",
  "message": "Failed to connect to database"
}
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| Invalid JSON | Malformed request body | Validate JSON syntax |
| Timeout | Portal not responding | Check internet connection, retry |
| Database error | Connection issue | Verify database is running |
| Portal structure changed | Website layout changed | Update parser in scraper code |
| No results found | Portal has no new jobs | Check portal status manually |

---

## Rate Limiting

Currently **no rate limiting** in development mode.

For production, implement:
```python
from rest_framework.throttling import UserRateThrottle

class JobScrapingThrottle(UserRateThrottle):
    scope = 'job_scraping'
    THROTTLE_RATES = {'job_scraping': '10/hour'}
```

---

## Examples

### Complete Workflow

#### Step 1: Start Bulk Scraping
```powershell
$body = @{
    max_age_hours = 48
    filter_ai_ml = $true
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/jobs/bulk-scrape/" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

$result = $response.Content | ConvertFrom-Json
$scrapingId = $result.scraping_id
Write-Host "Started scraping: $scrapingId"
```

#### Step 2: Check Status
```powershell
Start-Sleep -Seconds 5

$uri = "http://127.0.0.1:8000/api/jobs/scraping-status/$scrapingId/"
$response = Invoke-WebRequest -Uri $uri -Method GET
$status = $response.Content | ConvertFrom-Json

Write-Host "Status: $($status.data.status)"
Write-Host "Duration: $($status.data.duration_seconds)s"
```

#### Step 3: Retrieve Results
```powershell
$uri = "http://127.0.0.1:8000/api/jobs/list/?ai_ml_only=true&limit=20"
$response = Invoke-WebRequest -Uri $uri -Method GET
$jobs = $response.Content | ConvertFrom-Json

Write-Host "Total Jobs: $($jobs.data.total_count)"
foreach ($job in $jobs.data.jobs) {
    Write-Host "- $($job.title) at $($job.company.name)"
}
```

---

**Document Version**: 1.0
**Last Updated**: January 17, 2026
