#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display complete job details from database and attempt to fetch live job info.
Shows all stored job information with full details.
"""
import os
import django
import json
from datetime import datetime
import sys

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job, ScrapingMetadata
from companies.models import Company

print("\n" + "=" * 120)
print("COMPLETE JOB DATABASE REPORT")
print("=" * 120)

# Get all jobs
jobs = Job.objects.all().order_by('-job_posted_at')
total_jobs = jobs.count()

print(f"\n[DATABASE OVERVIEW]")
print(f"   Total Jobs: {total_jobs}")
print(f"   AI/ML Jobs: {Job.objects.filter(is_ai_ml_job=True).count()}")
print(f"   Total Companies: {Company.objects.count()}")
print(f"   Total Scraping Operations: {ScrapingMetadata.objects.count()}")

if total_jobs == 0:
    print("\n❌ No jobs found in database")
else:
    print("\n" + "=" * 120)
    print("DETAILED JOB LISTINGS")
    print("=" * 120)
    
    for idx, job in enumerate(jobs, 1):
        print(f"\n{'─' * 120}")
        print(f"JOB #{idx}")
        print(f"{'─' * 120}")
        
        print(f"✓ JOB ID:        {job.job_id}")
        print(f"✓ TITLE:         {job.title}")
        print(f"✓ COMPANY:       {job.company.name if job.company else 'Unknown'}")
        print(f"✓ PORTAL:        {job.source_portal.upper()}")
        print(f"✓ URL:           {job.job_url}")
        print(f"✓ POSTED:        {job.job_posted_at}")
        print(f"✓ AI/ML JOB:     {'Yes' if job.is_ai_ml_job else 'No'} (Confidence: {job.ai_ml_score:.2f}%)")
        
        if job.description:
            desc = job.description
            if len(desc) > 200:
                print(f"✓ DESCRIPTION:   {desc[:200]}...")
            else:
                print(f"✓ DESCRIPTION:   {desc}")
        
        if job.metadata:
            try:
                meta = json.loads(job.metadata) if isinstance(job.metadata, str) else job.metadata
                print(f"✓ METADATA:      {json.dumps(meta, indent=20)[:200]}...")
            except:
                pass
    
    # Detailed statistics
    print("\n" + "=" * 120)
    print("DETAILED STATISTICS")
    print("=" * 120)
    
    print(f"\n📈 AI/ML Jobs by Portal:")
    for portal in Job.objects.values('source_portal').distinct():
        portal_name = portal['source_portal']
        total = Job.objects.filter(source_portal=portal_name).count()
        ai_ml = Job.objects.filter(source_portal=portal_name, is_ai_ml_job=True).count()
        print(f"   {portal_name.upper():20} - Total: {total:3}, AI/ML: {ai_ml:3}")
    
    print(f"\n🏢 Jobs by Company:")
    for company in Company.objects.all():
        job_count = Job.objects.filter(company=company).count()
        ai_ml_count = Job.objects.filter(company=company, is_ai_ml_job=True).count()
        print(f"   {company.name[:50]:50} - Total: {job_count}, AI/ML: {ai_ml_count}")
    
    print(f"\n📊 AI/ML Score Distribution:")
    ai_ml_jobs = Job.objects.filter(is_ai_ml_job=True)
    if ai_ml_jobs.exists():
        scores = [j.ai_ml_score for j in ai_ml_jobs]
        print(f"   Min Score:   {min(scores):.2f}%")
        print(f"   Max Score:   {max(scores):.2f}%")
        print(f"   Avg Score:   {sum(scores)/len(scores):.2f}%")
    
    print(f"\n🔗 URL Accessibility Test:")
    import requests
    
    working_urls = 0
    broken_urls = 0
    blocked_urls = 0
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.google.com/',
    }
    
    for job in jobs:
        if not job.job_url:
            continue
        
        try:
            response = requests.get(job.job_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                working_urls += 1
                print(f"   ✅ {job.title[:50]:50} - OK (200)")
            elif response.status_code == 403:
                blocked_urls += 1
                print(f"   ⚠️  {job.title[:50]:50} - BLOCKED (403)")
            else:
                broken_urls += 1
                print(f"   ❌ {job.title[:50]:50} - ERROR ({response.status_code})")
        except Exception as e:
            broken_urls += 1
            print(f"   ❌ {job.title[:50]:50} - {str(e)[:20]}")
    
    print(f"\n   Summary: ✅ {working_urls} working | ⚠️  {blocked_urls} blocked | ❌ {broken_urls} errors")
    
    # Recent scraping operations
    print("\n" + "=" * 120)
    print("RECENT SCRAPING OPERATIONS")
    print("=" * 120)
    
    recent_scrapes = ScrapingMetadata.objects.all().order_by('-completed_at')[:5]
    
    for idx, scrape in enumerate(recent_scrapes, 1):
        print(f"\n{idx}. Scraping ID: {scrape.id}")
        print(f"   Type:     {scrape.scrape_type.upper()}")
        print(f"   Status:   {scrape.status.upper()}")
        print(f"   Portal:   {scrape.source_portal}")
        print(f"   Duration: {scrape.duration_seconds:.2f}s" if scrape.duration_seconds else "   Duration: N/A")
        print(f"   Time:     {scrape.completed_at}")
        print(f"   Found:    {scrape.jobs_scraped} jobs | Stored: {scrape.jobs_stored} | AI/ML: {scrape.ai_ml_jobs_found}")

print("\n" + "=" * 120)
print("✅ REPORT COMPLETE")
print("=" * 120 + "\n")
