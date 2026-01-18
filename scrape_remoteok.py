#!/usr/bin/env python
"""RemoteOK.com scraper with company website extraction and verification."""

import os
import sys
import django
import requests
import json
from datetime import datetime
from django.utils import timezone
from bs4 import BeautifulSoup
from typing import List, Dict

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job, ScrapingMetadata
from companies.models import Company

print("=" * 120)
print("REMOTEOK.COM SCRAPER - JOB & COMPANY WEBSITE EXTRACTION")
print("=" * 120)

# RemoteOK API endpoint
API_URL = "https://remoteok.com/api"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("\n[STEP 1] Fetching jobs from RemoteOK API...")
print("-" * 120)

try:
    response = requests.get(API_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()
    
    data = response.json()
    print(f"✓ API Response received: {len(data)} records (includes metadata)")
    
    # Filter out metadata and get actual jobs
    jobs_data = [item for item in data if isinstance(item, dict) and 'id' in item and 'position' in item]
    print(f"✓ Extracted {len(jobs_data)} actual job listings\n")
    
    if len(jobs_data) == 0:
        print("No jobs found in API response")
        exit(1)
    
    # AI/ML Keywords
    AI_ML_KEYWORDS = [
        'machine learning', 'deep learning', 'ai', 'artificial intelligence',
        'nlp', 'neural network', 'tensorflow', 'pytorch', 'data science',
        'ml engineer', 'ai engineer', 'llm', 'gpt', 'generative', 'transformer'
    ]
    
    def is_ai_ml_job(title: str, description: str) -> tuple:
        """Check if job is AI/ML related."""
        combined = f"{title} {description}".lower()
        matches = sum(1 for kw in AI_ML_KEYWORDS if kw in combined)
        score = (matches / len(AI_ML_KEYWORDS)) * 100
        return matches >= 2 or score >= 20, score
    
    print("[STEP 2] Processing jobs and extracting company information...")
    print("-" * 120)
    
    jobs_processed = []
    companies_found = {}
    
    for idx, job in enumerate(jobs_data, 1):  # Process all jobs
        try:
            job_id = str(job.get('id', f'remoteok_{idx}'))
            title = job.get('position', '')
            company_name = job.get('company', '')
            slug = job.get('slug', '')
            # Build company URL from slug
            company_url = f"https://remoteok.com/remote-jobs/{slug}" if slug else ''
            description = job.get('description', '')[:500] if job.get('description') else ''
            tags = job.get('tags', [])
            
            if not title or not company_name:
                continue
            
            # Check if AI/ML job
            is_ai_ml, score = is_ai_ml_job(title, description)
            
            job_info = {
                'job_id': f"remoteok_{job_id}",
                'title': title,
                'company_name': company_name,
                'company_url': company_url,
                'description': description,
                'is_ai_ml': is_ai_ml,
                'ai_ml_score': score,
                'source': 'remoteok',
                'tags': tags
            }
            
            jobs_processed.append(job_info)
            
            # Track companies
            if company_name not in companies_found:
                companies_found[company_name] = {
                    'url': company_url,
                    'count': 0,
                    'ai_ml_count': 0
                }
            
            companies_found[company_name]['count'] += 1
            if is_ai_ml:
                companies_found[company_name]['ai_ml_count'] += 1
            
            # Print progress
            if idx % 10 == 0:
                print(f"  Processed {idx} jobs...")
        
        except Exception as e:
            print(f"  ⚠ Error processing job {idx}: {str(e)[:50]}")
            continue
    
    print(f"\n✓ Successfully processed {len(jobs_processed)} jobs")
    print(f"✓ Found {len(companies_found)} unique companies\n")
    
    # Step 3: Save to database
    print("[STEP 3] Saving jobs and companies to database...")
    print("-" * 120)
    
    companies_created = 0
    jobs_created = 0
    
    for company_name, company_info in companies_found.items():
        try:
            company_id = f"remoteok_{company_name[:30].lower().replace(' ', '_')}"
            
            company, created = Company.objects.get_or_create(
                company_id=company_id,
                defaults={
                    'name': company_name,
                    'website': company_info['url'] if company_info['url'] else None,
                }
            )
            
            if created:
                companies_created += 1
                print(f"  ✓ Created company: {company_name}")
                if company_info['url']:
                    print(f"     Website: {company_info['url']}")
        
        except Exception as e:
            print(f"  ✗ Error creating company {company_name}: {str(e)[:50]}")
    
    # Create jobs
    for job_data in jobs_processed:
        try:
            company = Company.objects.filter(name=job_data['company_name']).first()
            
            job, created = Job.objects.get_or_create(
                job_id=job_data['job_id'],
                defaults={
                    'title': job_data['title'],
                    'company': company,
                    'job_url': job_data['company_url'],
                    'description': job_data['description'],
                    'is_ai_ml_job': job_data['is_ai_ml'],
                    'ai_ml_score': job_data['ai_ml_score'],
                    'source_portal': 'remoteok',
                    'job_posted_at': timezone.now(),
                    'metadata': {
                        'tags': job_data['tags'],
                        'company_url': job_data['company_url']
                    }
                }
            )
            
            if created:
                jobs_created += 1
        
        except Exception as e:
            print(f"  ✗ Error creating job {job_data.get('job_id')}: {str(e)[:50]}")
    
    print(f"\n✓ Database updated:")
    print(f"  - Companies created: {companies_created}")
    print(f"  - Jobs created: {jobs_created}")
    
    # Step 4: Test URL accessibility
    print("\n[STEP 4] Testing company URL accessibility...")
    print("-" * 120)
    
    accessible = 0
    blocked = 0
    failed = 0
    
    for company_name, company_info in list(companies_found.items())[:10]:
        url = company_info['url']
        
        if not url:
            print(f"  ⚠ {company_name}: No URL")
            continue
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✓ {company_name}")
                print(f"    URL: {url[:80]}")
                print(f"    Status: 200 OK")
                accessible += 1
            elif response.status_code == 403:
                print(f"  ⚠ {company_name}")
                print(f"    URL: {url[:80]}")
                print(f"    Status: 403 Forbidden (Anti-scraping protection)")
                blocked += 1
            else:
                print(f"  ✗ {company_name}")
                print(f"    URL: {url[:80]}")
                print(f"    Status: {response.status_code}")
                failed += 1
        
        except Exception as e:
            print(f"  ✗ {company_name}: {str(e)[:50]}")
            failed += 1
    
    print(f"\n✓ Accessible: {accessible} | ⚠ Blocked: {blocked} | ✗ Failed: {failed}")
    
    # Step 5: Summary
    print("\n" + "=" * 120)
    print("SUMMARY")
    print("=" * 120)
    
    print(f"\nJobs Scraped: {len(jobs_processed)}")
    print(f"Companies Found: {len(companies_found)}")
    
    ai_ml_count = sum(1 for j in jobs_processed if j['is_ai_ml'])
    print(f"AI/ML Jobs: {ai_ml_count}")
    
    print(f"\nTop Companies:")
    sorted_companies = sorted(companies_found.items(), key=lambda x: x[1]['count'], reverse=True)
    for company_name, info in sorted_companies[:10]:
        print(f"  - {company_name}: {info['count']} jobs ({info['ai_ml_count']} AI/ML)")
    
    print("\n" + "=" * 120)
    print("RemoteOK scraping completed!")
    print("=" * 120)

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
