#!/usr/bin/env python
"""
Test script to send scraping request to Guru.com endpoint
"""
import requests
import json
import sys

def main():
    url = 'http://127.0.0.1:8000/api/jobs/realtime-guru/'
    payload = {
        'email': 'rajamajho0019@gmail.com'
    }
    
    try:
        print("Sending request to Guru.com scraping endpoint...")
        print(f"URL: {url}")
        print(f"Email: rajamajho0019@gmail.com\n")
        
        response = requests.post(url, json=payload, timeout=300)
        
        print(f"Status Code: {response.status_code}\n")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Django server is running at http://127.0.0.1:8000/")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
