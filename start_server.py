#!/usr/bin/env python
"""Script to start Django development server"""
import os
import sys
import subprocess

os.chdir('d:\\web_scraping\\ml_job_scraper')
subprocess.run([
    sys.executable, 
    'manage.py', 
    'runserver', 
    '127.0.0.1:8000'
])
