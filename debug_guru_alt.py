#!/usr/bin/env python
"""Diagnostic script to inspect Guru.com HTML structure - try alternate URLs."""

import requests
from bs4 import BeautifulSoup

print("=" * 80)
print("GURU.COM DIAGNOSTIC SCRIPT (ALTERNATE ENDPOINTS)")
print("=" * 80)

# Try multiple URLs
urls = [
    ("Main jobs page", "https://www.guru.com/jobs"),
    ("Search page", "https://www.guru.com/jobs/search"),
    ("API endpoint", "https://www.guru.com/api/jobs/search"),
    ("ML search", "https://www.guru.com/jobs/search?q=machine+learning"),
    ("AI search", "https://www.guru.com/jobs/search?q=artificial+intelligence"),
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
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for job listings
            jobs = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
            print(f"Job elements found: {len(jobs)}")
            
            # Check for titles
            titles = soup.find_all(['h2', 'h3', 'h4'])
            print(f"Headers found: {len(titles)}")
            
            if titles[:3]:
                print("Sample headers:")
                for title in titles[:3]:
                    print(f"  - {title.get_text(strip=True)[:60]}")
        else:
            print(f"✗ NOT ACCESSIBLE ({response.status_code})")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)[:50]}")

print("\n" + "=" * 80)
