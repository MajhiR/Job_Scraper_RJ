#!/usr/bin/env python
"""Test URL accessibility for jobs in database across all platforms."""

import os
import sys
import django
import requests

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job

print("=" * 100)
print("COMPREHENSIVE URL ACCESSIBILITY TEST - ALL JOBS IN DATABASE")
print("=" * 100)

# Get all jobs from database
all_jobs = Job.objects.all().order_by('source_portal', '-job_posted_at')

if all_jobs.count() == 0:
    print("\nNo jobs found in database.")
else:
    print(f"\n✓ Found {all_jobs.count()} total jobs in database\n")
    
    # Group by portal
    portals = all_jobs.values('source_portal').distinct()
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for portal_data in portals:
        portal = portal_data['source_portal']
        portal_jobs = all_jobs.filter(source_portal=portal)
        
        print("=" * 100)
        print(f"{portal.upper()} - URL ACCESSIBILITY TEST")
        print("=" * 100)
        print(f"\nTesting {portal_jobs.count()} jobs:\n")
        
        accessible = 0
        failed = 0
        no_url = 0
        
        for idx, job in enumerate(portal_jobs, 1):
            if not job.job_url:
                print(f"{idx}. ⚠ {job.title[:60]}")
                print(f"   NO URL")
                no_url += 1
                continue
            
            try:
                response = requests.get(job.job_url, headers=HEADERS, timeout=10)
                
                if response.status_code == 200:
                    print(f"{idx}. ✓ {job.title[:60]}")
                    print(f"   URL: {job.job_url[:80]}")
                    print(f"   Status: {response.status_code} OK")
                    print(f"   AI/ML: {job.is_ai_ml_job} (Score: {job.ai_ml_score:.2f}%)")
                    accessible += 1
                else:
                    print(f"{idx}. ✗ {job.title[:60]}")
                    print(f"   URL: {job.job_url[:80]}")
                    print(f"   Status: {response.status_code}")
                    failed += 1
                    
            except requests.exceptions.Timeout:
                print(f"{idx}. ✗ {job.title[:60]}")
                print(f"   URL: {job.job_url[:80]}")
                print(f"   Error: Request timeout")
                failed += 1
                
            except Exception as e:
                print(f"{idx}. ✗ {job.title[:60]}")
                print(f"   URL: {job.job_url[:80]}")
                print(f"   Error: {str(e)[:50]}")
                failed += 1
            
            print()
        
        print(f"\nSummary for {portal.upper()}:")
        print(f"  Accessible:  {accessible}")
        print(f"  Failed:      {failed}")
        print(f"  No URL:      {no_url}")
        print(f"  Total:       {portal_jobs.count()}")
        print()
    
    # Overall summary
    print("=" * 100)
    print("OVERALL SUMMARY")
    print("=" * 100)
    
    total_accessible = 0
    total_failed = 0
    total_no_url = 0
    
    for portal_data in portals:
        portal = portal_data['source_portal']
        portal_jobs = all_jobs.filter(source_portal=portal)
        
        accessible = 0
        failed = 0
        no_url = 0
        
        for job in portal_jobs:
            if not job.job_url:
                no_url += 1
            else:
                try:
                    response = requests.get(job.job_url, headers=HEADERS, timeout=10)
                    if response.status_code == 200:
                        accessible += 1
                    else:
                        failed += 1
                except:
                    failed += 1
        
        total_accessible += accessible
        total_failed += failed
        total_no_url += no_url
        
        print(f"\n{portal.upper():20} - Accessible: {accessible:2}, Failed: {failed:2}, No URL: {no_url:2}, Total: {portal_jobs.count():2}")
    
    print(f"\n{'TOTAL':20} - Accessible: {total_accessible}, Failed: {total_failed}, No URL: {total_no_url}, Total: {all_jobs.count()}")
    print("\n" + "=" * 100)
