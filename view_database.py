#!/usr/bin/env python
"""
Script to display database contents
"""
import os
import django

os.chdir('d:\\web_scraping\\ml_job_scraper')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job, ScrapingMetadata
from companies.models import Company

print("=" * 80)
print("COMPANIES IN DATABASE")
print("=" * 80)
companies = Company.objects.all()
if companies.exists():
    for company in companies:
        print(f"ID: {company.id}, Name: {company.name}, Industry: {company.industry}")
else:
    print("No companies found")

print("\n" + "=" * 80)
print("JOBS IN DATABASE")
print("=" * 80)
jobs = Job.objects.all()
if jobs.exists():
    for job in jobs:
        print(f"ID: {job.id}")
        print(f"  Title: {job.title}")
        print(f"  Company: {job.company.name if job.company else 'N/A'}")
        print(f"  Portal: {job.source_portal}")
        print(f"  URL: {job.job_url}")
        print(f"  AI/ML: {job.is_ai_ml_job}")
        print(f"  Posted: {job.job_posted_at}")
        print()
else:
    print("No jobs found")

print("=" * 80)
print("SCRAPING METADATA")
print("=" * 80)
metadata = ScrapingMetadata.objects.all()
if metadata.exists():
    for m in metadata:
        print(f"ID: {m.id}")
        print(f"  Type: {m.scrape_type}")
        print(f"  Status: {m.status}")
        print(f"  Portal: {m.source_portal}")
        if hasattr(m, 'created_at'):
            print(f"  Created: {m.created_at}")
        print()
else:
    print("No scraping metadata found")

print("=" * 80)
print("DATABASE SUMMARY")
print("=" * 80)
print(f"Total Companies: {Company.objects.count()}")
print(f"Total Jobs: {Job.objects.count()}")
print(f"Total Scraping Metadata: {ScrapingMetadata.objects.count()}")
