#!/usr/bin/env python
"""Test scraper service with WeWorkRemotely"""
import os
import sys

os.chdir('d:\\web_scraping\\ml_job_scraper')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

try:
    from scraper.scraper import JobScraperService
    print("Testing JobScraperService with weworkremotely portal...")
    
    scraper_service = JobScraperService(max_workers=1)
    
    # Get available scrapers
    print(f"Available portals: {list(scraper_service.SCRAPER_CLASSES.keys())}")
    
    # Scrape weworkremotely
    results = scraper_service.scrape_portals(['weworkremotely'])
    print(f"\nResults: {results}")
    
except Exception as e:
    print(f'Error: {type(e).__name__}: {str(e)}')
    import traceback
    traceback.print_exc()
