"""
Web scraper module for fetching jobs from various portals.
"""
import logging
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
from typing import List, Dict, Tuple
import time

logger = logging.getLogger('scraper')

# AI/ML Keywords for filtering
AI_ML_KEYWORDS = [
    'machine learning', 'deep learning', 'neural network', 'nlp', 'natural language',
    'computer vision', 'ai', 'artificial intelligence', 'tensorflow', 'pytorch',
    'scikit-learn', 'data science', 'data scientist', 'ml engineer', 'ai engineer',
    'predictive modeling', 'classification', 'regression', 'clustering',
    'llm', 'gpt', 'generative', 'transformer', 'bert', 'model training',
    'data analysis', 'analytics', 'algorithm', 'optimization', 'reinforcement learning'
]


class BaseScraper:
    """Base scraper class with common functionality."""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        })
    
    def is_ai_ml_job(self, title: str, description: str) -> Tuple[bool, float]:
        """
        Check if a job is AI/ML related and return confidence score.
        
        Args:
            title: Job title
            description: Job description
            
        Returns:
            Tuple of (is_ai_ml, confidence_score)
        """
        combined_text = f"{title} {description}".lower()
        matches = sum(1 for keyword in AI_ML_KEYWORDS if keyword in combined_text)
        
        total_keywords = len(AI_ML_KEYWORDS)
        confidence = (matches / total_keywords) * 100 if total_keywords > 0 else 0
        
        # Threshold: at least 2 keywords or 20% confidence
        is_ai_ml = matches >= 2 or confidence >= 20
        
        return is_ai_ml, confidence
    
    def get_posted_time(self, posted_str: str) -> datetime:
        """Parse posted time string to datetime."""
        # Default: current time
        return datetime.now()
    
    def close(self):
        """Close the session."""
        self.session.close()


class GuruScraper(BaseScraper):
    """Scraper for Guru.com"""
    
    BASE_URL = "https://www.guru.com"
    JOBS_ENDPOINT = "/api/jobs"
    
    def scrape_jobs(self) -> List[Dict]:
        """
        Scrape jobs from Guru.com
        Note: Guru.com has anti-scraping measures. Using public API endpoint.
        """
        try:
            logger.info("Starting Guru.com scraping...")
            jobs = []
            
            # Attempt to fetch from jobs page
            url = f"{self.BASE_URL}/jobs"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            }
            
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse response
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Guru uses dynamic loading, so we'll need to parse what's available
            job_elements = soup.find_all('div', class_='job-item')
            
            for element in job_elements:
                try:
                    job = self._parse_guru_job(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Guru job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Guru.com")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Guru.com: {e}")
            return []
    
    def _parse_guru_job(self, element) -> Dict:
        """Parse a single job element from Guru."""
        try:
            # Try multiple ways to get job ID
            job_id = element.get('data-job-id', '')
            if not job_id:
                url_elem = element.find('a')
                if url_elem and 'href' in url_elem.attrs:
                    job_id = url_elem['href'].split('/')[-1]
            
            # Try multiple selectors for title
            title = element.find('h2', class_='job-title')
            if not title:
                title = element.find('h3')
            if not title:
                title = element.find('a')
            
            if not title:
                return None
            
            title_text = title.get_text(strip=True)
            if not title_text:
                return None
            
            # Find description - try multiple selectors
            description = element.find('p', class_='job-description')
            if not description:
                description = element.find('div', class_='description')
            if not description:
                description = element.find('p')
            
            description_text = description.get_text(strip=True)[:500] if description else ''
            
            # Find URL
            url = element.find('a', class_='job-link')
            if not url:
                url = element.find('a')
            
            url_text = url.get('href', '') if url else ''
            if url_text and not url_text.startswith('http'):
                url_text = self.BASE_URL + url_text
            
            # Find company name
            company = element.find('span', class_='company-name')
            if not company:
                company = element.find('div', class_='company')
            if not company:
                company = element.find('span')
            
            company_text = company.get_text(strip=True) if company else 'Unknown'
            
            # Find posted time
            posted_at = element.find('span', class_='posted-time')
            if not posted_at:
                posted_at = element.find('span', class_='time')
            
            posted_text = posted_at.get_text(strip=True) if posted_at else ''
            
            return {
                'job_id': job_id or f"guru_{title_text[:20]}",
                'title': title_text,
                'description': description_text,
                'url': url_text,
                'company_name': company_text or 'Unknown',
                'posted_at': posted_text,
                'source': 'guru'
            }
        except Exception as e:
            logger.error(f"Error parsing Guru job element: {e}")
            return None


class TruelancerScraper(BaseScraper):
    """Scraper for Truelancer.com"""
    
    BASE_URL = "https://www.truelancer.com"
    
    def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from Truelancer.com"""
        try:
            logger.info("Starting Truelancer.com scraping...")
            jobs = []
            
            url = f"{self.BASE_URL}/projects"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            project_elements = soup.find_all('div', class_='project-item')
            
            for element in project_elements:
                try:
                    job = self._parse_truelancer_job(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Truelancer job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Truelancer.com")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Truelancer.com: {e}")
            return []
    
    def _parse_truelancer_job(self, element) -> Dict:
        """Parse a single job element from Truelancer."""
        try:
            # Try multiple ways to get job ID
            job_id = element.get('data-project-id', '')
            if not job_id:
                url_elem = element.find('a')
                if url_elem and 'href' in url_elem.attrs:
                    job_id = url_elem['href'].split('/')[-1]
            
            # Try multiple selectors for title
            title = element.find('h3', class_='project-title')
            if not title:
                title = element.find('h3')
            if not title:
                title = element.find('h2')
            if not title:
                title = element.find('a')
            
            if not title:
                return None
            
            title_text = title.get_text(strip=True)
            if not title_text:
                return None
            
            # Find description
            description = element.find('p', class_='project-desc')
            if not description:
                description = element.find('p', class_='description')
            if not description:
                description = element.find('p')
            
            description_text = description.get_text(strip=True)[:500] if description else ''
            
            # Find URL
            url = element.find('a', class_='project-link')
            if not url:
                url = element.find('a')
            
            url_text = url.get('href', '') if url else ''
            if url_text and not url_text.startswith('http'):
                url_text = self.BASE_URL + url_text
            
            # Find company/client name
            company = element.find('span', class_='client-name')
            if not company:
                company = element.find('span', class_='author')
            if not company:
                company = element.find('div', class_='client')
            
            company_text = company.get_text(strip=True) if company else 'Unknown'
            
            # Find posted time
            posted_at = element.find('span', class_='posted-time')
            if not posted_at:
                posted_at = element.find('span', class_='time')
            
            posted_text = posted_at.get_text(strip=True) if posted_at else ''
            
            return {
                'job_id': job_id or f"truelancer_{title_text[:20]}",
                'title': title_text,
                'description': description_text,
                'url': url_text,
                'company_name': company_text or 'Unknown',
                'posted_at': posted_text,
                'source': 'truelancer'
            }
        except Exception as e:
            logger.error(f"Error parsing Truelancer job element: {e}")
            return None


class TwineScraper(BaseScraper):
    """Scraper for Twine.com"""
    
    BASE_URL = "https://www.twine.com"
    
    def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from Twine.com"""
        try:
            logger.info("Starting Twine.com scraping...")
            jobs = []
            
            url = f"{self.BASE_URL}/jobs"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            job_elements = soup.find_all('div', class_='job-card')
            
            for element in job_elements:
                try:
                    job = self._parse_twine_job(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing Twine job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Twine.com")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Twine.com: {e}")
            return []
    
    def _parse_twine_job(self, element) -> Dict:
        """Parse a single job element from Twine."""
        try:
            job_id = element.get('data-job-id', '')
            title = element.find('h4', class_='job-title')
            description = element.find('p', class_='job-description')
            url = element.find('a', class_='job-url')
            company = element.find('span', class_='company-name')
            posted_at = element.find('span', class_='post-date')
            
            if not all([job_id, title, description]):
                return None
            
            return {
                'job_id': job_id,
                'title': title.get_text(strip=True) if title else '',
                'description': description.get_text(strip=True) if description else '',
                'url': url.get('href', '') if url else '',
                'company_name': company.get_text(strip=True) if company else '',
                'posted_at': posted_at.get_text(strip=True) if posted_at else '',
                'source': 'twine'
            }
        except Exception as e:
            logger.error(f"Error parsing Twine job element: {e}")
            return None


class RemoteWorkScraper(BaseScraper):
    """Scraper for RemoteWork.com"""
    
    BASE_URL = "https://www.remotework.com"
    
    def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from RemoteWork.com"""
        try:
            logger.info("Starting RemoteWork.com scraping...")
            jobs = []
            
            url = f"{self.BASE_URL}/remote-jobs"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            job_elements = soup.find_all('div', class_='job-listing')
            
            for element in job_elements:
                try:
                    job = self._parse_remotework_job(element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing RemoteWork job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from RemoteWork.com")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping RemoteWork.com: {e}")
            return []
    
    def _parse_remotework_job(self, element) -> Dict:
        """Parse a single job element from RemoteWork."""
        try:
            job_id = element.get('data-job-id', '')
            title = element.find('h3', class_='job-name')
            description = element.find('p', class_='job-summary')
            url = element.find('a', class_='job-url')
            company = element.find('span', class_='employer-name')
            posted_at = element.find('span', class_='posted-on')
            
            if not all([job_id, title, description]):
                return None
            
            return {
                'job_id': job_id,
                'title': title.get_text(strip=True) if title else '',
                'description': description.get_text(strip=True) if description else '',
                'url': url.get('href', '') if url else '',
                'company_name': company.get_text(strip=True) if company else '',
                'posted_at': posted_at.get_text(strip=True) if posted_at else '',
                'source': 'remotework'
            }
        except Exception as e:
            logger.error(f"Error parsing RemoteWork job element: {e}")
            return None


class WeWorkRemotelyScraper(BaseScraper):
    """Scraper for WeWorkRemotely.com"""
    
    BASE_URL = "https://weworkremotely.com"
    
    def scrape_jobs(self) -> List[Dict]:
        """Scrape jobs from WeWorkRemotely.com"""
        try:
            logger.info("Starting WeWorkRemotely.com scraping...")
            jobs = []
            
            # Try main jobs page
            url = f"{self.BASE_URL}/remote-jobs"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # WeWorkRemotely uses li.feature for job listings
            job_elements = soup.find_all('li', class_='feature')
            
            if not job_elements:
                # Try alternative selectors
                job_elements = soup.find_all('div', class_='job')
            
            if not job_elements:
                # Try finding all list items and filter
                job_elements = soup.find_all('div', {'data-job-id': True})
            
            logger.info(f"Found {len(job_elements)} job elements to parse")
            
            for element in job_elements:
                try:
                    job = self._parse_weworkremotely_job(element)
                    if job and job.get('title') and 'View' not in job.get('title', ''):
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error parsing WeWorkRemotely job: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} valid jobs from WeWorkRemotely.com")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping WeWorkRemotely.com: {e}")
            return []
    
    def _parse_weworkremotely_job(self, element) -> Dict:
        """Parse a single job element from WeWorkRemotely."""
        try:
            # WeWorkRemotely structure: h3.new-listing__header__title
            title_elem = element.find('h3', class_='new-listing__header__title')
            if not title_elem:
                title_elem = element.find('h3')
            if not title_elem:
                title_elem = element.find('h2')
            
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if not title:
                return None
            
            # Find the main job link
            job_link = element.find('a', class_='listing-link--unlocked')
            if not job_link:
                job_link = element.find('a', {'href': lambda x: x and '/remote-jobs/' in x})
            
            url = job_link.get('href', '') if job_link else ''
            if url and not url.startswith('http'):
                url = self.BASE_URL + url
            
            # Find company name - look for any link with /company/ in href
            company_link = element.find('a', {'href': lambda x: x and '/company/' in x})
            company_name = 'Unknown'
            if company_link:
                # Try to get text from the link or nearby elements
                text = company_link.get_text(strip=True)
                # If it's just "View Company Profile", look for the name in the listing
                if 'View Company Profile' in text or not text:
                    # Try to find company name in the listing content
                    all_text = element.get_text(separator=' ', strip=True)
                    # Company name usually appears after the job title
                    parts = all_text.split(title)
                    if len(parts) > 1:
                        # Take words after title until we hit other keywords
                        after_title = parts[1].strip()
                        words = after_title.split()
                        # Get company name (first few words before keywords like "New", "Full-Time", etc.)
                        company_words = []
                        for word in words:
                            if word in ['New', 'Featured', 'Full-Time', 'Part-Time', 'Hourly', 'United', 'States', 'Anywhere', 'World', 'Remote']:
                                break
                            company_words.append(word)
                        company_name = ' '.join(company_words) if company_words else 'Unknown'
                else:
                    company_name = text
            
            # Get description from the listing text or meta info
            description = ''
            # Try to extract salary or job type as part of description
            meta_info = element.find('p', class_='new-listing__header__icons__date')
            if not meta_info:
                # Get all text as description
                all_text = element.get_text(separator=' ', strip=True)
                description = all_text[:300]
            else:
                description = meta_info.get_text(strip=True)
            
            # Create job ID
            job_id = f"weworkremotely_{url.split('/')[-1]}" if url else f"weworkremotely_{title[:20]}"
            
            return {
                'job_id': job_id,
                'title': title,
                'description': description,
                'url': url,
                'company_name': company_name,
                'source': 'weworkremotely'
            }
        except Exception as e:
            logger.error(f"Error parsing WeWorkRemotely job element: {e}")
            return None


class JobScraperService:
    """Main service for scraping jobs from all portals using thread pool."""
    
    SCRAPER_CLASSES = {
        'guru': GuruScraper,
        'truelancer': TruelancerScraper,
        'twine': TwineScraper,
        'remotework': RemoteWorkScraper,
        'weworkremotely': WeWorkRemotelyScraper,
    }
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
    
    def scrape_all_portals(self, max_age_hours=48, include_portals=None) -> Dict:
        """
        Scrape jobs from all portals using thread pool.
        
        Args:
            max_age_hours: Only include jobs posted within last N hours
            include_portals: List of specific portals to scrape. If None, scrapes all.
            
        Returns:
            Dictionary with scraped data and statistics
        """
        logger.info("Starting bulk scraping from all portals...")
        start_time = time.time()
        
        # Determine which portals to scrape
        if include_portals is None:
            portals_to_scrape = list(self.SCRAPER_CLASSES.keys())
        else:
            portals_to_scrape = [p for p in include_portals if p in self.SCRAPER_CLASSES]
        
        results = {
            'total_jobs': 0,
            'ai_ml_jobs': 0,
            'by_portal': {},
            'errors': []
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit scraping tasks
            future_to_portal = {
                executor.submit(self._scrape_portal, portal_name): portal_name
                for portal_name in portals_to_scrape
            }
            
            # Collect results
            for future in as_completed(future_to_portal):
                portal_name = future_to_portal[future]
                try:
                    jobs, ai_ml_count, error = future.result()
                    results['total_jobs'] += len(jobs)
                    results['ai_ml_jobs'] += ai_ml_count
                    results['by_portal'][portal_name] = {
                        'total_jobs': len(jobs),
                        'ai_ml_jobs': ai_ml_count,
                        'jobs': jobs
                    }
                    if error:
                        results['errors'].append(f"{portal_name}: {error}")
                except Exception as e:
                    logger.error(f"Error scraping {portal_name}: {e}")
                    results['errors'].append(f"{portal_name}: {str(e)}")
        
        duration = time.time() - start_time
        results['duration_seconds'] = duration
        
        logger.info(f"Scraping completed in {duration:.2f}s. "
                   f"Total jobs: {results['total_jobs']}, AI/ML jobs: {results['ai_ml_jobs']}")
        
        return results
    
    def _scrape_portal(self, portal_name: str) -> Tuple[List, int, str]:
        """
        Scrape a single portal.
        
        Returns:
            Tuple of (jobs_list, ai_ml_count, error_message)
        """
        error = None
        ai_ml_count = 0
        
        try:
            scraper_class = self.SCRAPER_CLASSES.get(portal_name)
            if not scraper_class:
                return [], 0, f"Unknown portal: {portal_name}"
            
            scraper = scraper_class()
            jobs = scraper.scrape_jobs()
            
            # Filter for AI/ML jobs
            filtered_jobs = []
            for job in jobs:
                is_ai_ml, score = scraper.is_ai_ml_job(job.get('title', ''), job.get('description', ''))
                if is_ai_ml:
                    job['ai_ml_score'] = score
                    filtered_jobs.append(job)
                    ai_ml_count += 1
            
            scraper.close()
            return filtered_jobs, ai_ml_count, None
            
        except Exception as e:
            error = str(e)
            logger.error(f"Error in _scrape_portal for {portal_name}: {e}")
            return [], 0, error
