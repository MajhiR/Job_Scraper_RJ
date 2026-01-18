import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from jobs.models import Job
from companies.models import Company

# Fetch the job
job = Job.objects.get(id='e4947775-d957-4328-8e21-10c003058844')

print('JOB RECORD')
print('='*80)
print(f'ID: {job.id}')
print(f'Job ID: {job.job_id}')
print(f'Title: {job.title}')
print(f'Description: {job.description}')
print(f'Job URL: {job.job_url}')
print(f'Source Portal: {job.source_portal}')
print(f'Job Type: {job.job_type}')
print(f'Experience Level: {job.experience_level}')
print(f'Salary Min: {job.salary_min}')
print(f'Salary Max: {job.salary_max}')
print(f'Currency: {job.currency}')
print(f'Location: {job.location}')
print(f'Skills Required: {job.skills_required}')
print(f'Status: {job.status}')
print(f'Company: {job.company.name}')
print(f'Job Posted At: {job.job_posted_at}')
print(f'Created At: {job.created_at}')
print(f'Updated At: {job.updated_at}')
print(f'Is AI/ML Job: {job.is_ai_ml_job}')
print(f'AI/ML Score: {job.ai_ml_score}')
print(f'Metadata: {job.metadata}')

print('\n' + '='*80)
print('COMPANY RECORD')
print('='*80)

# Fetch the company
company = Company.objects.get(name='New Proxify AB Sweden')

print(f'ID: {company.id}')
print(f'Company ID: {company.company_id}')
print(f'Name: {company.name}')
print(f'Website: {company.website}')
print(f'Description: {company.description}')
print(f'Industry: {company.industry}')
print(f'Focus Areas: {company.focus_areas}')
print(f'Headquarters Location: {company.headquarters_location}')
print(f'Country: {company.country}')
print(f'Company Size: {company.company_size}')
print(f'Email: {company.email}')
print(f'Phone: {company.phone}')
print(f'Rating: {company.rating}')
print(f'Review Count: {company.review_count}')
print(f'Is Verified: {company.is_verified}')
print(f'Created At: {company.created_at}')
print(f'Updated At: {company.updated_at}')

# Get all jobs for this company
print(f'\nTotal Jobs Posted: {company.jobs.count()}')
print('\nJobs from this company:')
for job in company.jobs.all():
    print(f'  - {job.title} ({job.source_portal})')
