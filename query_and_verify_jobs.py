#!/usr/bin/env python
"""
Query database for stored jobs and fetch details from their URLs.
"""
import os
import django
import requests
from bs4 import BeautifulSoup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job
from companies.models import Company

print("=" * 100)
print("DATABASE JOB DETAILS & URL VERIFICATION")
print("=" * 100)

# Query all jobs from database
jobs = Job.objects.all().order_by('-job_posted_at')

print(f"\n✓ Found {jobs.count()} total jobs in database\n")

if jobs.count() == 0:
    print("No jobs in database yet.")
else:
    print("=" * 100)
    print("JOB DETAILS FROM DATABASE")
    print("=" * 100)
    
    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. JOB ID: {job.job_id}")
        print(f"   Title: {job.title}")
        print(f"   Company: {job.company.name if job.company else 'Unknown'}")
        print(f"   Portal: {job.source_portal}")
        print(f"   URL: {job.job_url}")
        print(f"   Posted: {job.job_posted_at}")
        print(f"   AI/ML: {job.is_ai_ml_job} (Score: {job.ai_ml_score:.1f}%)")
        print(f"   Description: {job.description[:100]}...")
    
    # Now verify URLs are accessible
    print("\n" + "=" * 100)
    print("VERIFYING JOB URLs - FETCHING JOB DETAILS")
    print("=" * 100)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for idx, job in enumerate(jobs, 1):
        if not job.job_url:
            print(f"\n{idx}. ⚠ {job.title} - NO URL")
            continue
        
        print(f"\n{idx}. {job.title}")
        print(f"   URL: {job.job_url}")
        
        try:
            response = requests.get(job.job_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✓ Status: {response.status_code} OK")
                
                # Parse job details from the page
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to extract job title from page
                page_title = soup.find('h1') or soup.find('h2')
                if page_title:
                    print(f"   Page Title: {page_title.get_text(strip=True)[:60]}")
                
                # Try to extract company info
                company_info = soup.find('a', {'href': lambda x: x and '/company/' in x})
                if company_info:
                    print(f"   Company Link: {company_info.get_text(strip=True)}")
                
                # Try to extract job description
                description = soup.find('div', class_=lambda x: x and 'description' in x.lower())
                if description:
                    desc_text = description.get_text(strip=True)[:100]
                    print(f"   Description: {desc_text}...")
                
                # Count paragraphs as indicator of job posting content
                paragraphs = soup.find_all('p')
                print(f"   Content Paragraphs: {len(paragraphs)}")
                
            else:
                print(f"   ✗ Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ✗ Error: {str(e)[:50]}")
        except Exception as e:
            print(f"   ✗ Parse Error: {str(e)[:50]}")

# Summary statistics
print("\n" + "=" * 100)
print("SUMMARY STATISTICS")
print("=" * 100)

total_jobs = Job.objects.count()
ai_ml_jobs = Job.objects.filter(is_ai_ml_job=True).count()
total_companies = Company.objects.count()

print(f"Total Jobs: {total_jobs}")
print(f"AI/ML Jobs: {ai_ml_jobs}")
print(f"Total Companies: {total_companies}")

if total_companies > 0:
    print(f"\nCompanies:")
    for company in Company.objects.all():
        job_count = Job.objects.filter(company=company).count()
        print(f"  - {company.name}: {job_count} job(s)")

# Average AI/ML score
if ai_ml_jobs > 0:
    from django.db.models import Avg
    avg_result = Job.objects.filter(is_ai_ml_job=True).aggregate(avg_score=Avg('ai_ml_score'))
    print(f"\nAverage AI/ML Score: {avg_result['avg_score']:.2f}%")

print("\n" + "=" * 100)
