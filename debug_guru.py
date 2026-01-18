#!/usr/bin/env python
"""Diagnostic script to inspect Guru.com HTML structure."""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.guru.com/jobs?q=machine%20learning"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("=" * 80)
print("GURU.COM DIAGNOSTIC SCRIPT")
print("=" * 80)
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
        print("\n" + "=" * 80)
        print("HTML SNIPPET (first 2000 chars):")
        print("-" * 80)
        print(response.text[:2000])
        
except requests.exceptions.RequestException as e:
    print(f"ERROR: {str(e)}")
except Exception as e:
    print(f"ERROR: {str(e)}")
