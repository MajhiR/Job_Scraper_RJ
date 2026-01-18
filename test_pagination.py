#!/usr/bin/env python
"""Test pagination on WeWorkRemotely scraper."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from scraper.scraper import WeWorkRemotelyScraper

print("=" * 80)
print("TESTING WEWORKREMOTELY PAGINATION SCRAPER")
print("=" * 80)

scraper = WeWorkRemotelyScraper()

# Test with 3 pages
print("\nScraping 3 pages...")
jobs = scraper.scrape_jobs(max_pages=3)

print(f"\n✓ Total jobs found: {len(jobs)}")

# Display summary
print("\n" + "=" * 80)
print("JOB SUMMARY")
print("=" * 80)

for i, job in enumerate(jobs, 1):
    print(f"\n{i}. {job.get('title', 'N/A')}")
    print(f"   Company: {job.get('company_name', 'Unknown')}")
    print(f"   URL: {job.get('url', 'N/A')}")
    print(f"   Source: {job.get('source', 'N/A')}")

print("\n" + "=" * 80)

# Check for duplicates
print(f"\nTotal jobs collected: {len(jobs)}")
job_ids = [job['job_id'] for job in jobs]
unique_jobs = len(set(job_ids))
print(f"Unique jobs: {unique_jobs}")
print(f"Duplicates: {len(jobs) - unique_jobs}")
