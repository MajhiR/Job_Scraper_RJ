"""
Database models for Jobs and related data.
"""
from django.db import models
from django.utils import timezone
import uuid


class Job(models.Model):
    """
    Model to store job listings scraped from various portals.
    """
    JOB_SOURCE_CHOICES = [
        ('guru', 'Guru.com'),
        ('truelancer', 'Truelancer.com'),
        ('twine', 'Twine.com'),
        ('remotework', 'RemoteWork.com'),
        ('upwork', 'Upwork.com'),
        ('freelancer', 'Freelancer.com'),
        ('fiverr', 'Fiverr.com'),
        ('Glassdoor', 'Glassdoor.com'),
        ('Indeed', 'Indeed.com'),
        ('LinkedIn', 'LinkedIn.com'),
        ('Experteer', 'Experteer.com'),
        ('FlexJobs', 'FlexJobs.com'),
        ('AngelList', 'AngelList.com'),
        ('WeWorkRemotely', 'WeWorkRemotely.com'),
        ('RemoteOK', 'RemoteOK.io'),
        ('Jobspresso', 'Jobspresso.co'),
        ('PowerToFly', 'PowerToFly.com'),
        ('Dice', 'Dice.com'),
        ('Hired', 'Hired.com'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job_id = models.CharField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=500)
    description = models.TextField()
    job_url = models.URLField(max_length=1000)
    source_portal = models.CharField(max_length=20, choices=JOB_SOURCE_CHOICES)
    job_type = models.CharField(max_length=100, blank=True)  # e.g., "Full-time", "Contract"
    experience_level = models.CharField(max_length=100, blank=True)  # e.g., "Senior", "Junior"
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    location = models.CharField(max_length=255, blank=True)
    skills_required = models.TextField(blank=True)  # JSON or comma-separated
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='jobs')
    
    # Timestamps
    job_posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata
    is_ai_ml_job = models.BooleanField(default=False, db_index=True)
    ai_ml_score = models.FloatField(default=0.0)  # Confidence score for AI/ML classification
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data

    class Meta:
        db_table = 'jobs'
        indexes = [
            models.Index(fields=['is_ai_ml_job', 'status']),
            models.Index(fields=['source_portal', 'created_at']),
            models.Index(fields=['company', 'created_at']),
        ]
        ordering = ['-job_posted_at']

    def __str__(self):
        return f"{self.title} - {self.source_portal} ({self.job_id})"


class ScrapingMetadata(models.Model):
    """
    Model to track scraping operations and metadata.
    """
    SCRAPE_TYPE_CHOICES = [
        ('bulk', 'Bulk Scraping'),
        ('realtime', 'Real-time Scraping'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scrape_type = models.CharField(max_length=20, choices=SCRAPE_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    source_portal = models.CharField(max_length=20)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    
    # Statistics
    jobs_scraped = models.IntegerField(default=0)
    jobs_stored = models.IntegerField(default=0)
    ai_ml_jobs_found = models.IntegerField(default=0)
    errors_count = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    # Request details
    request_params = models.JSONField(default=dict)  # Store original request parameters
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'scraping_metadata'
        indexes = [
            models.Index(fields=['status', 'started_at']),
            models.Index(fields=['source_portal', 'scrape_type']),
        ]
        ordering = ['-started_at']

    def __str__(self):
        return f"Scrape {self.scrape_type} - {self.source_portal} ({self.status})"
