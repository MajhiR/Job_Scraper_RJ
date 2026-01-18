#!/usr/bin/env python
"""Diagnostic script for Twine.com - try alternate endpoints."""

import requests
from bs4 import BeautifulSoup

print("=" * 80)
print("TWINE.COM DIAGNOSTIC SCRIPT (ALTERNATE ENDPOINTS)")
print("=" * 80)

urls = [
    ("Main page", "https://www.twine.com"),
    ("Jobs home", "https://www.twine.com/jobs"),
    ("Browse jobs", "https://www.twine.com/jobs/browse"),
    ("ML specialism", "https://www.twine.com/jobs?specialisms=machine-learning"),
    ("Search", "https://www.twine.com/search?type=job&q=machine+learning"),
    ("API", "https://api.twine.com/jobs"),
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
            
            if 'application/json' in response.headers.get('Content-Type', ''):
                print("Content-Type: JSON (API)")
                try:
                    data = response.json()
                    print(f"JSON records: {len(data) if isinstance(data, list) else 'dict'}")
                except:
                    print("Invalid JSON")
            else:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                jobs = soup.find_all('div', class_=lambda x: x and ('job' in x.lower() or 'listing' in x.lower()))
                print(f"Job elements found: {len(jobs)}")
                
                titles = soup.find_all(['h2', 'h3', 'h4', 'a'])
                print(f"Potential listings: {len(titles)}")
                
                if titles[:3]:
                    print("Sample items:")
                    for title in titles[:3]:
                        text = title.get_text(strip=True)[:60]
                        if text and len(text) > 3:
                            print(f"  - {text}")
        else:
            print(f"✗ NOT ACCESSIBLE ({response.status_code})")
            
    except Exception as e:
        print(f"✗ ERROR: {str(e)[:50]}")

print("\n" + "=" * 80)
