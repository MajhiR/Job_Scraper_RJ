"""
URL Configuration for ML Job Scraper.
"""
from django.urls import path, include

urlpatterns = [
    path('api/jobs/', include('jobs.urls')),
    path('api/companies/', include('companies.urls')),
]
