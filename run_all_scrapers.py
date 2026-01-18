#!/usr/bin/env python
"""Run all job scrapers to populate database."""

import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from scraper.scraper import JobScraperService
from jobs.models import Job

print("=" * 100)
print("RUNNING ALL JOB SCRAPERS")
print("=" * 100)

# Initialize scraper service
service = JobScraperService(max_workers=4)

try:
    # Scrape all portals
    print("\nStarting bulk scraping from all available portals...")
    results = service.scrape_all_portals(max_pages=2, filter_ai_ml=False)
    
    print("\n" + "=" * 100)
    print("SCRAPING RESULTS")
    print("=" * 100)
    
    print(f"\nTotal Jobs Scraped: {results['total_jobs']}")
    print(f"AI/ML Jobs: {results['ai_ml_jobs']}")
    
    print("\nResults by Portal:")
    for portal, data in results['by_portal'].items():
        print(f"  {portal.upper():20} - Jobs: {data['jobs']}, AI/ML: {data['ai_ml_jobs']}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    # Display database stats
    print("\n" + "=" * 100)
    print("DATABASE STATISTICS")
    print("=" * 100)
    
    total_jobs = Job.objects.count()
    ai_ml_jobs = Job.objects.filter(is_ai_ml_job=True).count()
    
    print(f"\nTotal Jobs in Database: {total_jobs}")
    print(f"AI/ML Jobs in Database: {ai_ml_jobs}")
    
    print("\nJobs by Portal:")
    for portal in Job.objects.values('source_portal').distinct():
        portal_name = portal['source_portal']
        count = Job.objects.filter(source_portal=portal_name).count()
        ai_ml = Job.objects.filter(source_portal=portal_name, is_ai_ml_job=True).count()
        print(f"  {portal_name.upper():20} - Total: {count}, AI/ML: {ai_ml}")
    
    print("\n" + "=" * 100)
    print("Scraping completed successfully!")
    print("=" * 100)

except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
