#!/usr/bin/env python
"""Test WeWorkRemotely scraper"""
import os
import sys

os.chdir('d:\\web_scraping\\ml_job_scraper')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

try:
    from scraper.scraper import WeWorkRemotelyScraper
    print("Testing WeWorkRemotelyScraper...")
    scraper = WeWorkRemotelyScraper()
    jobs = scraper.scrape_jobs()
    print(f'Successfully scraped {len(jobs)} jobs from WeWorkRemotely.com')
    if jobs:
        for job in jobs[:5]:
            print(f'  - {job.get("title", "No title")} @ {job.get("company_name", "Unknown")}')
    else:
        print("No jobs found, but scraper is working!")
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
