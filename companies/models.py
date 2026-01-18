"""
Database models for Companies.
"""
from django.db import models
import uuid


class Company(models.Model):
    """
    Model to store company information that posts jobs.
    """
    COMPANY_SIZE_CHOICES = [
        ('startup', 'Startup'),
        ('small', 'Small (1-50)'),
        ('medium', 'Medium (51-200)'),
        ('large', 'Large (201-1000)'),
        ('enterprise', 'Enterprise (1000+)'),
        ('unknown', 'Unknown'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.CharField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=500, db_index=True)
    description = models.TextField(blank=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZE_CHOICES, default='unknown')
    
    # Location
    headquarters_location = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Contact info
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Ratings and reviews
    rating = models.FloatField(default=0.0, null=True, blank=True)
    review_count = models.IntegerField(default=0)
    
    # Industry and focus
    industry = models.CharField(max_length=255, blank=True)
    focus_areas = models.TextField(blank=True)  # AI, ML, Data Science, etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'companies'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company_id})"

    def get_total_jobs_posted(self):
        """Get total number of jobs posted by this company."""
        return self.jobs.filter(is_ai_ml_job=True).count()

    def get_active_ai_ml_jobs(self):
        """Get active AI/ML jobs posted by this company."""
        return self.jobs.filter(is_ai_ml_job=True, status='active')
