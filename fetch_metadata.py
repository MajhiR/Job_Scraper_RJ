import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import ScrapingMetadata

meta = ScrapingMetadata.objects.get(id='22485af5-d671-4c3f-9fdb-a8ba0627d97f')

print('SCRAPING METADATA RECORD')
print('='*80)
print(f'ID: {meta.id}')
print(f'Type: {meta.scrape_type}')
print(f'Status: {meta.status}')
print(f'Source Portal: {meta.source_portal}')
print(f'Jobs Scraped: {meta.jobs_scraped}')
print(f'Jobs Stored: {meta.jobs_stored}')
print(f'AI/ML Jobs Found: {meta.ai_ml_jobs_found}')
print(f'Errors Count: {meta.errors_count}')
print(f'Duration (seconds): {meta.duration_seconds}')
print(f'Started At: {meta.started_at}')
print(f'Completed At: {meta.completed_at}')
print(f'Error Message: {meta.error_message if meta.error_message else "None"}')
print(f'Request Params: {meta.request_params}')
print(f'Metadata: {meta.metadata}')
