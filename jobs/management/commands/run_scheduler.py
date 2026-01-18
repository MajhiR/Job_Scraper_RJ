"""
Django management command to run APScheduler for hourly job scraping.
"""
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils import timezone
import logging
import django
from django.core.exceptions import ObjectDoesNotExist

logger = logging.getLogger(__name__)


def scrape_jobs_hourly():
    """Execute job scraping task hourly."""
    from jobs.models import ScrapingMetadata
    from scraper.scraper import JobScraperService
    
    try:
        logger.info("Starting hourly job scraping task...")
        service = JobScraperService()
        
        # Perform the scraping with pagination
        jobs_data = service.scrape_all_portals(
            include_portals=['weworkremotely'],  # Focus on working portals
            filter_ai_ml=True,
            max_pages=3
        )
        
        logger.info(f"Hourly scraping completed: {jobs_data}")
        
        # Log successful execution
        DjangoJobExecution.objects.create(
            job_id="scrape_jobs_hourly",
            status="success",
            next_run_time=timezone.now()
        )
        
    except Exception as e:
        logger.error(f"Error during hourly scraping: {e}", exc_info=True)
        try:
            DjangoJobExecution.objects.create(
                job_id="scrape_jobs_hourly",
                status="failed",
                next_run_time=timezone.now()
            )
        except Exception as log_error:
            logger.error(f"Failed to log job execution: {log_error}")


class Command(BaseCommand):
    help = 'Start APScheduler for hourly job scraping'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hour',
            type=int,
            default=1,
            help='Run every N hours (default: 1)'
        )

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=timezone.utc)
        
        # Set up Django job store
        scheduler.configure(
            jobstores={'default': DjangoJobStore()},
            timezone=timezone.utc
        )

        # Add job to run every N hours
        hour_interval = options.get('hour', 1)
        
        scheduler.add_job(
            scrape_jobs_hourly,
            trigger=CronTrigger(minute=0),  # Run at the top of every hour
            id='scrape_jobs_hourly',
            name='Hourly Job Scraping',
            replace_existing=True,
        )

        logger.info(f"Scheduler started. Job scraping will run every hour.")
        
        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
            scheduler.shutdown()
