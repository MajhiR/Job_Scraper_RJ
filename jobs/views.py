"""
API views for jobs endpoints.
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, timezone
from jobs.models import Job, ScrapingMetadata
from companies.models import Company
from scraper.scraper import JobScraperService

logger = logging.getLogger('jobs')


@csrf_exempt
@require_http_methods(["GET"])
def api_documentation(request):
    """
    Root API documentation endpoint.
    Shows available endpoints and usage information.
    """
    return JsonResponse({
        'status': 'success',
        'message': 'ML Job Scraper API',
        'version': '1.0',
        'endpoints': {
            'Jobs API': {
                'list': {
                    'method': 'GET',
                    'url': '/api/jobs/list/',
                    'description': 'Get all jobs from the database'
                },
                'bulk_scrape': {
                    'method': 'POST',
                    'url': '/api/jobs/bulk-scrape/',
                    'description': 'Trigger bulk scraping of jobs from all portals',
                    'body': {
                        'company_details': 'Optional filter by company',
                        'max_age_hours': 48,
                        'include_portals': ['guru', 'truelancer', 'twine', 'remotework', 'weworkremotely'],
                        'filter_ai_ml': True
                    }
                },
                'realtime_scrape': {
                    'method': 'POST',
                    'url': '/api/jobs/realtime-guru/',
                    'description': 'Real-time scraping from Guru portal',
                    'body': {
                        'search_terms': 'e.g., machine learning, AI'
                    }
                },
                'scraping_status': {
                    'method': 'GET',
                    'url': '/api/jobs/scraping-status/<scraping_id>/',
                    'description': 'Get status of a scraping job'
                }
            },
            'Companies API': {
                'url': '/api/companies/',
                'description': 'Company management endpoints'
            }
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def bulk_scrape_jobs(request):
    """
    API endpoint for bulk scraping jobs from all portals.
    
    Request body:
    {
        "company_details": "Optional filter by company",
        "max_age_hours": 48,
        "include_portals": ["guru", "truelancer", "twine", "remotework"],
        "filter_ai_ml": true
    }
    
    Response:
    {
        "status": "success" | "error",
        "scraping_id": "uuid",
        "message": "...",
        "data": {
            "total_jobs": 123,
            "ai_ml_jobs": 45,
            "stored_jobs": 45,
            "duration_seconds": 12.5,
            "by_portal": {...}
        }
    }
    """
    try:
        request_data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    
    # Extract parameters
    max_age_hours = request_data.get('max_age_hours', 48)
    include_portals = request_data.get('include_portals', 
                                      ['guru', 'truelancer', 'twine', 'remotework'])
    filter_ai_ml = request_data.get('filter_ai_ml', True)
    
    try:
        # Create metadata record for this scraping operation
        metadata = ScrapingMetadata.objects.create(
            scrape_type='bulk',
            status='in_progress',
            source_portal='multi',
            request_params=request_data
        )
        
        logger.info(f"Starting bulk scraping operation {metadata.id}")
        
        # Initialize scraper and run
        scraper_service = JobScraperService(max_workers=4)
        results = scraper_service.scrape_all_portals(
            max_age_hours=max_age_hours,
            include_portals=include_portals
        )
        
        # Store jobs in database
        stored_jobs = 0
        ai_ml_jobs_count = 0
        errors = []
        
        for portal_name, portal_data in results.get('by_portal', {}).items():
            for job_data in portal_data.get('jobs', []):
                try:
                    # Get or create company
                    company, created = Company.objects.get_or_create(
                        company_id=job_data.get('company_name', 'Unknown'),
                        defaults={
                            'name': job_data.get('company_name', 'Unknown'),
                            'industry': 'Technology',
                        }
                    )
                    
                    # Create or update job
                    job, created = Job.objects.update_or_create(
                        job_id=job_data.get('job_id'),
                        defaults={
                            'title': job_data.get('title', ''),
                            'description': job_data.get('description', ''),
                            'job_url': job_data.get('url', ''),
                            'source_portal': portal_name,
                            'company': company,
                            'job_posted_at': datetime.now(),
                            'is_ai_ml_job': True,  # Already filtered
                            'ai_ml_score': job_data.get('ai_ml_score', 0),
                            'metadata': job_data,
                        }
                    )
                    
                    if created:
                        stored_jobs += 1
                        ai_ml_jobs_count += 1
                        
                except Exception as e:
                    error_msg = f"Error storing job {job_data.get('job_id')}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        # Update metadata record
        metadata.status = 'completed'
        metadata.jobs_scraped = results.get('total_jobs', 0)
        metadata.jobs_stored = stored_jobs
        metadata.ai_ml_jobs_found = ai_ml_jobs_count
        metadata.errors_count = len(errors)
        metadata.duration_seconds = int(results.get('duration_seconds', 0))
        if errors:
            metadata.error_details = {'errors': errors}
        metadata.completed_at = datetime.now(timezone.utc)
        metadata.save()
        
        return JsonResponse({
            'status': 'success',
            'scraping_id': str(metadata.id),
            'message': f'Successfully scraped and stored jobs',
            'data': {
                'total_jobs': results.get('total_jobs', 0),
                'ai_ml_jobs': results.get('ai_ml_jobs', 0),
                'stored_jobs': stored_jobs,
                'duration_seconds': results.get('duration_seconds', 0),
                'errors': errors if errors else None,
            }
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error in bulk_scrape_jobs: {str(e)}")
        if 'metadata' in locals():
            metadata.status = 'failed'
            metadata.error_message = str(e)
            metadata.completed_at = datetime.now(timezone.utc)
            metadata.save()
        
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def realtime_scrape_guru(request):
    """
    API endpoint for real-time scraping from Guru.com only.
    
    Request body:
    {
        "job_id": "optional_specific_job_id"
    }
    
    Response:
    {
        "status": "success" | "error",
        "scraping_id": "uuid",
        "message": "...",
        "data": {
            "jobs_fetched": 10,
            "jobs_stored": 10,
            "ai_ml_jobs": 8
        }
    }
    """
    try:
        request_data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON in request body'
        }, status=400)
    
    try:
        # Create metadata record
        metadata = ScrapingMetadata.objects.create(
            scrape_type='realtime',
            status='in_progress',
            source_portal='guru',
            request_params=request_data
        )
        
        logger.info(f"Starting real-time Guru.com scraping operation {metadata.id}")
        
        # Import scraper here to avoid circular imports
        from scraper.scraper import GuruScraper
        
        scraper = GuruScraper()
        jobs = scraper.scrape_jobs()
        
        # Store jobs
        stored_jobs = 0
        ai_ml_count = 0
        errors = []
        
        for job_data in jobs:
            try:
                # Filter for AI/ML jobs
                is_ai_ml, score = scraper.is_ai_ml_job(
                    job_data.get('title', ''),
                    job_data.get('description', '')
                )
                
                if not is_ai_ml:
                    continue
                
                # Get or create company
                company, created = Company.objects.get_or_create(
                    company_id=job_data.get('company_name', 'Unknown'),
                    defaults={
                        'name': job_data.get('company_name', 'Unknown'),
                        'industry': 'Technology',
                    }
                )
                
                # Create job record
                job, created = Job.objects.create(
                    job_id=f"guru_{job_data.get('job_id')}_{datetime.now().timestamp()}",
                    title=job_data.get('title', ''),
                    description=job_data.get('description', ''),
                    job_url=job_data.get('url', ''),
                    source_portal='guru',
                    company=company,
                    job_posted_at=datetime.now(),
                    is_ai_ml_job=True,
                    ai_ml_score=score,
                    metadata=job_data,
                )
                
                stored_jobs += 1
                ai_ml_count += 1
                
            except Exception as e:
                error_msg = f"Error storing job: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        scraper.close()
        
        # Update metadata
        metadata.status = 'completed'
        metadata.jobs_scraped = len(jobs)
        metadata.jobs_stored = stored_jobs
        metadata.ai_ml_jobs_found = ai_ml_count
        metadata.errors_count = len(errors)
        if errors:
            metadata.error_details = {'errors': errors}
        metadata.completed_at = datetime.now(timezone.utc)
        metadata.save()
        
        return JsonResponse({
            'status': 'success',
            'scraping_id': str(metadata.id),
            'message': 'Real-time Guru.com scraping completed',
            'data': {
                'jobs_fetched': len(jobs),
                'jobs_stored': stored_jobs,
                'ai_ml_jobs': ai_ml_count,
            }
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error in realtime_scrape_guru: {str(e)}")
        if 'metadata' in locals():
            metadata.status = 'failed'
            metadata.error_message = str(e)
            metadata.completed_at = datetime.now(timezone.utc)
            metadata.save()
        
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_jobs(request):
    """
    GET endpoint to retrieve stored jobs with filters.
    
    Query parameters:
    - ai_ml_only: true|false (default: true)
    - portal: guru|truelancer|twine|remotework
    - company_id: filter by company UUID
    - limit: number of results (default: 20)
    - offset: pagination offset (default: 0)
    """
    try:
        ai_ml_only = request.GET.get('ai_ml_only', 'true').lower() == 'true'
        portal = request.GET.get('portal', None)
        company_id = request.GET.get('company_id', None)
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # Build query
        queryset = Job.objects.all()
        
        if ai_ml_only:
            queryset = queryset.filter(is_ai_ml_job=True)
        
        if portal:
            queryset = queryset.filter(source_portal=portal)
        
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        queryset = queryset.order_by('-job_posted_at')
        
        total_count = queryset.count()
        jobs = queryset[offset:offset+limit]
        
        jobs_data = [
            {
                'id': str(job.id),
                'job_id': job.job_id,
                'title': job.title,
                'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
                'job_url': job.job_url,
                'source_portal': job.source_portal,
                'company': {
                    'id': str(job.company.id),
                    'name': job.company.name,
                },
                'ai_ml_score': job.ai_ml_score,
                'job_posted_at': job.job_posted_at.isoformat(),
                'created_at': job.created_at.isoformat(),
            }
            for job in jobs
        ]
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'total_count': total_count,
                'returned': len(jobs_data),
                'offset': offset,
                'limit': limit,
                'jobs': jobs_data,
            }
        }, status=200)
        
    except Exception as e:
        logger.error(f"Error in get_jobs: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_scraping_status(request, scraping_id):
    """
    GET endpoint to check scraping operation status.
    """
    try:
        metadata = ScrapingMetadata.objects.get(id=scraping_id)
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'scraping_id': str(metadata.id),
                'scrape_type': metadata.scrape_type,
                'status': metadata.status,
                'source_portal': metadata.source_portal,
                'jobs_scraped': metadata.jobs_scraped,
                'jobs_stored': metadata.jobs_stored,
                'ai_ml_jobs_found': metadata.ai_ml_jobs_found,
                'errors_count': metadata.errors_count,
                'duration_seconds': metadata.duration_seconds,
                'started_at': metadata.started_at.isoformat(),
                'completed_at': metadata.completed_at.isoformat() if metadata.completed_at else None,
            }
        }, status=200)
        
    except ScrapingMetadata.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Scraping operation not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in get_scraping_status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
