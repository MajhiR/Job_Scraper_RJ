#!/usr/bin/env python
"""Diagnostic script to check HTML structure of WeWorkRemotely"""
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
})

url = 'https://weworkremotely.com/remote-jobs'
response = session.get(url, timeout=10)
soup = BeautifulSoup(response.content, 'lxml')

print("=" * 80)
print("Checking HTML structure for WeWorkRemotely.com")
print("=" * 80)

# Find all li.feature
features = soup.find_all('li', class_='feature')
print(f"\nFound {len(features)} li.feature elements")

if features:
    print("\nFirst job element structure:")
    print(features[0].prettify()[:1000])
    
    # Extract sample text
    first_job = features[0]
    all_links = first_job.find_all('a')
    print(f"\nLinks in first job ({len(all_links)}):")
    for i, link in enumerate(all_links[:3]):
        print(f"  {i}: href='{link.get('href')}', text='{link.get_text(strip=True)[:50]}'")
    
    all_text = first_job.get_text()
    print(f"\nAll text (first 300 chars):")
    print(all_text[:300])
