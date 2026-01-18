#!/usr/bin/env python
"""Diagnostic script for RemoteOk.com with database verification."""

import os
import django
import requests
from bs4 import BeautifulSoup
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job, ScrapingMetadata
from companies.models import Company

print("=" * 100)
print("REMOTEOK.COM DIAGNOSTIC & DATABASE VERIFICATION SCRIPT")
print("=" * 100)

urls = [
    ("Main page", "https://remoteok.com"),
    ("Jobs page", "https://remoteok.com/jobs"),
    ("AI jobs", "https://remoteok.com/?q=ai"),
    ("ML jobs", "https://remoteok.com/?q=machine+learning"),
    ("API endpoint", "https://remoteok.com/api"),
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for desc, url in urls:
    print(f"\nTesting: {desc}")
    print(f"URL: {url}")
    print("-" * 80)
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ ACCESSIBLE")
            
            # Check content type
            if 'application/json' in response.headers.get('Content-Type', ''):
                print("Content-Type: JSON (API)")
                try:
                    data = response.json()
                    print(f"JSON records: {len(data) if isinstance(data, list) else 'N/A'}")
                    if isinstance(data, list) and len(data) > 0:
                        print(f"Sample record keys: {list(data[0].keys())[:5]}")
                except:
                    pass
            else:
                print("Content-Type: HTML")
                soup = BeautifulSoup(response.content, 'html.parser')
                
                jobs = soup.find_all('div', class_=lambda x: x and ('job' in x.lower() or 'listing' in x.lower()))
                print(f"Job elements found: {len(jobs)}")
                
                titles = soup.find_all(['h2', 'h3', 'h4', 'a'])
                print(f"Titles/Links found: {len(titles)}")
                
                if titles[:3]:
                    print("Sample items:")
                    for title in titles[:3]:
                        text = title.get_text(strip=True)[:60]
                        if text:
                            print(f"  - {text}")
        else:
            print(f"✗ NOT ACCESSIBLE ({response.status_code})")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)[:50]}")

print("\n" + "=" * 100)

# DATABASE VERIFICATION
print("\n" + "=" * 100)
print("DATABASE VERIFICATION - REMOTEOK.COM JOBS")
print("=" * 100)

# Query jobs from RemoteOk.com in database
remoteok_jobs = Job.objects.filter(source_portal='remoteok').order_by('-job_posted_at')
print(f"\n✓ Found {remoteok_jobs.count()} RemoteOk.com jobs in database\n")

if remoteok_jobs.exists():
    print("REMOTEOK.COM JOB DETAILS:")
    print("-" * 100)
    
    for idx, job in enumerate(remoteok_jobs[:10], 1):  # Show first 10
        print(f"\n{idx}. {job.title}")
        print(f"   Company: {job.company.name if job.company else 'Unknown'}")
        print(f"   URL: {job.job_url}")
        print(f"   Posted: {job.job_posted_at}")
        print(f"   AI/ML Job: {'Yes' if job.is_ai_ml_job else 'No'} (Score: {job.ai_ml_score:.2f}%)")
    
    # URL Accessibility Test
    print("\n" + "=" * 100)
    print("URL ACCESSIBILITY TEST - REMOTEOK.COM")
    print("-" * 100)
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    accessible = 0
    failed = 0
    
    for idx, job in enumerate(remoteok_jobs[:5], 1):  # Test first 5
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
    print("COMPANY EXTRACTION ANALYSIS - REMOTEOK.COM")
    print("-" * 100)
    
    companies = Company.objects.filter(job__source_portal='remoteok').distinct()
    print(f"\nTotal Companies: {companies.count()}\n")
    
    for company in companies[:10]:
        job_count = Job.objects.filter(company=company, source_portal='remoteok').count()
        print(f"- {company.name}: {job_count} jobs")
    
    # AI/ML Scoring Statistics
    print("\n" + "=" * 100)
    print("AI/ML SCORING STATISTICS - REMOTEOK.COM")
    print("-" * 100)
    
    ai_ml_jobs = remoteok_jobs.filter(is_ai_ml_job=True)
    print(f"\nTotal AI/ML Jobs: {ai_ml_jobs.count()}")
    
    if ai_ml_jobs.exists():
        scores = [j.ai_ml_score for j in ai_ml_jobs]
        print(f"Score Range: {min(scores):.2f}% - {max(scores):.2f}%")
        print(f"Average Score: {sum(scores)/len(scores):.2f}%")
    
    # Scraping History
    print("\n" + "=" * 100)
    print("SCRAPING OPERATION HISTORY - REMOTEOK.COM")
    print("-" * 100)
    
    metadata = ScrapingMetadata.objects.filter(source='remoteok').order_by('-created_at')[:5]
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
    print("No RemoteOk.com jobs found in database. Run scraper first.")

print("\n" + "=" * 100)
