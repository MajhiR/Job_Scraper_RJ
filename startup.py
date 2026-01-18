#!/usr/bin/env python
"""
Startup script for ML Job Scraper with scheduled scraping.
Runs migrations and starts both the Django server and APScheduler.
"""
import os
import sys
import django
import subprocess
import threading
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def run_migrations():
    """Run Django migrations."""
    print("=" * 80)
    print("Running migrations...")
    print("=" * 80)
    os.system('python manage.py migrate')

def run_scheduler():
    """Run APScheduler in a separate thread."""
    print("=" * 80)
    print("Starting APScheduler...")
    print("=" * 80)
    os.system('python manage.py run_scheduler')

def run_server():
    """Run Django development server."""
    print("=" * 80)
    print("Starting Django development server...")
    print("=" * 80)
    os.system('python manage.py runserver 0.0.0.0:8000')

if __name__ == '__main__':
    print("=" * 80)
    print("ML JOB SCRAPER - STARTUP SCRIPT")
    print("=" * 80)
    
    # Run migrations
    run_migrations()
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    time.sleep(2)
    
    # Start Django server in main thread
    run_server()
