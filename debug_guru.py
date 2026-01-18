#!/usr/bin/env python
"""Diagnostic script to inspect Guru.com HTML structure and database verification."""

import os
import django
import requests
from bs4 import BeautifulSoup
import re
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job, ScrapingMetadata
from companies.models import Company

BASE_URL = "https://www.guru.com/jobs?q=machine%20learning"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("=" * 100)
print("GURU.COM DIAGNOSTIC & DATABASE VERIFICATION SCRIPT")
print("=" * 100)
print(f"Target URL: {BASE_URL}\n")

try:
    response = requests.get(BASE_URL, headers=HEADERS, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Length: {len(response.text)} chars\n")
    
    if response.status_code != 200:
        print(f"ERROR: Got status code {response.status_code}")
        print(f"Response body (first 500 chars):\n{response.text[:500]}\n")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for job containers
        print("CHECKING FOR JOB CONTAINERS:")
        print("-" * 80)
        
        # Try multiple selectors
        selectors = [
            ('div[data-qa="job-tile"]', 'Job tile with data-qa'),
            ('div.job-tile', 'div with job-tile class'),
            ('li.job', 'li with job class'),
            ('div.job-posting', 'div with job-posting class'),
            ('article.job', 'article with job class'),
            ('div[class*="job"]', 'div with "job" in class'),
        ]
        
        for selector, desc in selectors:
            elements = soup.select(selector)
            print(f"{desc:40} ({selector}): {len(elements)} found")
        
        print("\n" + "=" * 80)
        print("JOB TITLE SELECTORS:")
        print("-" * 80)
        
        # Try to find job titles
        title_selectors = [
            ('h2', 'h2 tags'),
            ('h3', 'h3 tags'),
            ('a[class*="title"]', 'a with "title" in class'),
            ('span[class*="title"]', 'span with "title" in class'),
            ('[data-qa="job-title"]', 'element with data-qa="job-title"'),
        ]
        
        for selector, desc in title_selectors:
            elements = soup.select(selector)[:5]
            print(f"\n{desc} ({selector}): {len(soup.select(selector))} total")
            for elem in elements:
                text = elem.get_text(strip=True)[:60]
                print(f"  - {text}")
        
        print("\n" + "=" * 80)
        print("PAGE STRUCTURE ANALYSIS:")
        print("-" * 80)
        
        # Check page structure
        print(f"Total <div> elements: {len(soup.find_all('div'))}")
        print(f"Total <a> elements: {len(soup.find_all('a'))}")
        print(f"Total <span> elements: {len(soup.find_all('span'))}")
        print(f"Total <li> elements: {len(soup.find_all('li'))}")
        
        # Check for specific patterns
        print("\n" + "=" * 80)
        print("CONTENT CHECKS:")
        print("-" * 80)
        
        if 'machine learning' in response.text.lower():
            print("✓ 'machine learning' text found in page")
        else:
            print("✗ 'machine learning' text NOT found in page")
        
        if 'job' in response.text.lower():
            print("✓ 'job' text found in page")
        else:
            print("✗ 'job' text NOT found in page")
        
        # Check for pagination
        print("\n" + "=" * 80)
        print("PAGINATION CHECK:")
        print("-" * 80)
        
        pagination_selectors = [
            ('a[rel="next"]', 'next link'),
            ('button[aria-label*="next"]', 'next button'),
            ('.pagination', 'pagination container'),
            ('[data-qa="pagination"]', 'pagination with data-qa'),
        ]
        
        for selector, desc in pagination_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✓ {desc}: {len(elements)} found")
        
        # Print first 2000 chars of HTML for manual inspection
        print("\n" + "=" * 100)
        print("HTML SNIPPET (first 2000 chars):")
        print("-" * 100)
        print(response.text[:2000])
        
except requests.exceptions.RequestException as e:
    print(f"ERROR: {str(e)}")
except Exception as e:
    print(f"ERROR: {str(e)}")

# DATABASE VERIFICATION
print("\n\n" + "=" * 100)
print("DATABASE VERIFICATION - GURU.COM JOBS")
print("=" * 100)

# Query jobs from Guru.com in database
guru_jobs = Job.objects.filter(source_portal='guru').order_by('-job_posted_at')
print(f"\n✓ Found {guru_jobs.count()} Guru.com jobs in database\n")

if guru_jobs.exists():
    print("GURU.COM JOB DETAILS:")
    print("-" * 100)
    
    for idx, job in enumerate(guru_jobs[:10], 1):  # Show first 10
        print(f"\n{idx}. {job.title}")
        print(f"   Company: {job.company.name if job.company else 'Unknown'}")
        print(f"   URL: {job.job_url}")
        print(f"   Posted: {job.job_posted_at}")
        print(f"   AI/ML Job: {'Yes' if job.is_ai_ml_job else 'No'} (Score: {job.ai_ml_score:.2f}%)")
    
    # URL Accessibility Test
    print("\n" + "=" * 100)
    print("URL ACCESSIBILITY TEST - GURU.COM")
    print("-" * 100)
    
    accessible = 0
    failed = 0
    
    for idx, job in enumerate(guru_jobs[:5], 1):  # Test first 5
        if not job.job_url:
            print(f"\n{idx}. ⚠ {job.title} - NO URL")
            failed += 1
            continue
        
        try:
            response = requests.get(job.job_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                print(f"\n{idx}. ✓ {job.title[:50]}")
                print(f"   Status: {response.status_code} OK")
                accessible += 1
            else:
                print(f"\n{idx}. ✗ {job.title[:50]}")
                print(f"   Status: {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"\n{idx}. ✗ {job.title[:50]}")
            print(f"   Error: {str(e)[:50]}")
            failed += 1
    
    print(f"\n✓ Accessible: {accessible} | ✗ Failed: {failed}")
    
    # Company Extraction Analysis
    print("\n" + "=" * 100)
    print("COMPANY EXTRACTION ANALYSIS - GURU.COM")
    print("-" * 100)
    
    companies = Company.objects.filter(job__source_portal='guru').distinct()
    print(f"\nTotal Companies: {companies.count()}\n")
    
    for company in companies[:10]:
        job_count = Job.objects.filter(company=company, source_portal='guru').count()
        print(f"- {company.name}: {job_count} jobs")
    
    # AI/ML Scoring Statistics
    print("\n" + "=" * 100)
    print("AI/ML SCORING STATISTICS - GURU.COM")
    print("-" * 100)
    
    ai_ml_jobs = guru_jobs.filter(is_ai_ml_job=True)
    print(f"\nTotal AI/ML Jobs: {ai_ml_jobs.count()}")
    
    if ai_ml_jobs.exists():
        scores = [j.ai_ml_score for j in ai_ml_jobs]
        print(f"Score Range: {min(scores):.2f}% - {max(scores):.2f}%")
        print(f"Average Score: {sum(scores)/len(scores):.2f}%")
    
    # Scraping History
    print("\n" + "=" * 100)
    print("SCRAPING OPERATION HISTORY - GURU.COM")
    print("-" * 100)
    
    metadata = ScrapingMetadata.objects.filter(source='guru').order_by('-created_at')[:5]
    if metadata.exists():
        for meta in metadata:
            print(f"\n• {meta.created_at}")
            print(f"  Jobs Found: {meta.jobs_found}")
            print(f"  Status: {meta.status}")
            if meta.error_message:
                print(f"  Error: {meta.error_message}")
    else:
        print("No scraping history found.")
else:
    print("No Guru.com jobs found in database. Run scraper first.")
