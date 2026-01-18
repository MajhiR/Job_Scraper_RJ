"""
URLs for jobs API endpoints.
"""
from django.urls import path
from jobs import views

urlpatterns = [
    # Documentation
    path('', views.api_documentation, name='api_documentation'),
    
    # Scraping endpoints
    path('bulk-scrape/', views.bulk_scrape_jobs, name='bulk_scrape_jobs'),
    path('realtime-guru/', views.realtime_scrape_guru, name='realtime_scrape_guru'),
    
    # Retrieval endpoints
    path('list/', views.get_jobs, name='get_jobs'),
    path('scraping-status/<str:scraping_id>/', views.get_scraping_status, name='get_scraping_status'),
]
