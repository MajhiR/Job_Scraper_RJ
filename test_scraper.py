#!/usr/bin/env python
"""Test scraper directly"""
import os
import sys

os.chdir('d:\\web_scraping\\ml_job_scraper')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

try:
    from scraper.scraper import GuruScraper
    print("Testing GuruScraper...")
    scraper = GuruScraper()
    jobs = scraper.scrape_jobs()
    print(f'Successfully scraped {len(jobs)} jobs from Guru')
    for job in jobs[:3]:
        print(f'  - {job.get("title", "No title")}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
