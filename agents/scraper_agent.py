"""
Scraper Agent for collecting job postings from Craigslist.
Handles pagination, rate limiting, retries, and anti-bot protection.
"""
import time
import random
from typing import List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from ratelimit import limits, sleep_and_retry

from config import Config
from utils import get_logger
from models import RawJobPosting, ScraperConfig

logger = get_logger(__name__)


class ScraperAgent:
    """Agent for scraping Craigslist job postings."""

    # Craigslist base URL pattern
    BASE_URL = "https://{city}.craigslist.org/search/{category}"
    JOB_URL = "https://{city}.craigslist.org"

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the Scraper Agent.

        Args:
            config: Scraper configuration (uses defaults if not provided)
        """
        self.config = config or ScraperConfig()

        # Set up session with headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        logger.info(
            f"ScraperAgent initialized for city: {self.config.city}, "
            f"category: {self.config.category}"
        )

    def _random_delay(self):
        """Add a random delay between requests to avoid detection."""
        delay = random.uniform(
            self.config.delay_min,
            self.config.delay_max
        )
        logger.debug(f"Sleeping for {delay:.2f} seconds")
        time.sleep(delay)

    @retry(
        stop=stop_after_attempt(Config.MAX_RETRIES),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        reraise=True
    )
    def _fetch_page(self, url: str) -> str:
        """
        Fetch a page with retry logic.

        Args:
            url: URL to fetch

        Returns:
            Page HTML content
        """
        logger.debug(f"Fetching URL: {url}")

        try:
            response = self.session.get(
                url,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            logger.debug(f"Successfully fetched {url}")
            return response.text

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    def _is_quality_listing(self, title: str, location: str) -> bool:
        """
        Check if listing meets minimum quality standards.

        Quality filters:
        - Must be in English (basic check)
        - Must not be spam/junk keywords
        - Must have meaningful title (not just city name)

        Args:
            title: Job title
            location: Job location

        Returns:
            True if listing passes quality checks
        """
        import re

        # Filter 1: Title must exist and be substantial
        if not title or len(title) < 10:
            logger.debug(f"Rejected: Title too short ({len(title) if title else 0} chars)")
            return False

        # Filter 2: Check for English characters (must have some ASCII letters)
        if not re.search(r'[a-zA-Z]{3,}', title):
            logger.debug(f"Rejected: No English text in title: {title[:50]}")
            return False

        # Filter 3: Reject spam keywords
        spam_keywords = [
            'free', 'click here', 'earn money', 'work from home no experience',
            'make $$', 'quick cash', 'no experience needed', '$$$',
            'get paid to', 'easy money', 'free training provided'
        ]
        title_lower = title.lower()
        for spam in spam_keywords:
            if spam in title_lower:
                logger.debug(f"Rejected: Spam keyword '{spam}' in title")
                return False

        # Filter 4: Title shouldn't be just the location/city name
        if title.strip().lower() == location.strip().lower():
            logger.debug(f"Rejected: Title is just location: {title}")
            return False

        # Filter 5: Reject if title is mostly numbers or symbols
        alpha_chars = sum(1 for c in title if c.isalpha())
        if alpha_chars < 5:
            logger.debug(f"Rejected: Too few letters in title: {title[:50]}")
            return False

        return True

    def _parse_listing_page(self, html: str, city: str) -> List[dict]:
        """
        Parse job listings from a search results page with quality filtering.

        Args:
            html: HTML content of the page
            city: City being scraped

        Returns:
            List of quality job listing dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        listings = []
        filtered_count = 0

        # Find all job postings
        results = soup.find_all('li', class_='cl-static-search-result')

        logger.info(f"Found {len(results)} listings on page")

        for result in results:
            try:
                # Extract link element (direct child of li)
                link_elem = result.find('a')
                if not link_elem:
                    continue

                url = link_elem['href']

                # Extract title (from div with class 'title' inside link)
                title_elem = link_elem.find('div', class_='title')
                if not title_elem:
                    continue

                title = title_elem.text.strip()

                # Extract location from details div
                location_elem = link_elem.find('div', class_='location')
                location = location_elem.text.strip() if location_elem else city

                # Apply quality filter BEFORE processing further
                if not self._is_quality_listing(title, location):
                    filtered_count += 1
                    continue

                # Make URL absolute if needed
                if url.startswith('/'):
                    url = f"https://{city}.craigslist.org{url}"

                # Extract date if available
                date_elem = link_elem.find('time')
                posted_date = date_elem.get('datetime') if date_elem else None

                listing = {
                    'title': title,
                    'url': url,
                    'location': location,
                    'posted_date': posted_date,
                }

                listings.append(listing)

            except Exception as e:
                logger.warning(f"Failed to parse listing: {e}")
                continue

        logger.info(f"Quality filter: {len(listings)} passed, {filtered_count} filtered out")
        return listings

    def _parse_job_detail(self, html: str, url: str) -> Optional[str]:
        """
        Parse full job description from detail page.

        Args:
            html: HTML content of job detail page
            url: URL of the job posting

        Returns:
            Job description text or None if parsing fails
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            # Find the posting body
            body_elem = soup.find('section', id='postingbody')

            if not body_elem:
                logger.warning(f"Could not find job description for {url}")
                return None

            # Remove QR code text if present
            for qr in body_elem.find_all('div', class_='print-qrcode-container'):
                qr.decompose()

            description = body_elem.get_text(separator='\n', strip=True)

            return description

        except Exception as e:
            logger.error(f"Failed to parse job detail for {url}: {e}")
            return None

    def scrape_listings(
        self,
        keywords: Optional[List[str]] = None
    ) -> List[RawJobPosting]:
        """
        Scrape job listings from Craigslist.

        Args:
            keywords: Optional list of keywords to filter by

        Returns:
            List of raw job postings
        """
        logger.info(
            f"Starting scrape for {self.config.city}/{self.config.category}"
        )

        all_listings = []
        keywords = keywords or self.config.keywords

        # Build search URL
        base_url = self.BASE_URL.format(
            city=self.config.city,
            category=self.config.category
        )

        # Add keyword query if provided
        if keywords:
            keyword_query = ' '.join(keywords)
            base_url += f"?query={keyword_query}"

        # Scrape multiple pages
        for page in range(self.config.max_pages):
            try:
                # Build paginated URL
                if page == 0:
                    url = base_url
                else:
                    separator = '&' if '?' in base_url else '?'
                    url = f"{base_url}{separator}s={page * 120}"

                logger.info(f"Scraping page {page + 1}/{self.config.max_pages}")

                # Fetch page
                html = self._fetch_page(url)

                # Parse listings
                listings = self._parse_listing_page(html, self.config.city)

                if not listings:
                    logger.info("No more listings found, stopping pagination")
                    break

                all_listings.extend(listings)

                # Random delay before next page
                if page < self.config.max_pages - 1:
                    self._random_delay()

            except Exception as e:
                logger.error(f"Failed to scrape page {page + 1}: {e}")
                break

        logger.info(f"Scraped {len(all_listings)} total listings")

        # If quick scan only, return basic listings without fetching full details
        if self.config.quick_scan_only:
            logger.info("Quick scan mode - skipping full detail fetch")
            return self._convert_basic_listings_to_jobs(all_listings)

        # Otherwise fetch full details for each listing
        return self._fetch_job_details(all_listings)

    def _convert_basic_listings_to_jobs(self, listings: List[dict]) -> List[RawJobPosting]:
        """
        Convert basic listings to RawJobPosting objects without fetching full details.
        Used for quick scan mode.

        Args:
            listings: List of basic listing information

        Returns:
            List of RawJobPosting objects with minimal data
        """
        logger.info(f"Converting {len(listings)} basic listings to job objects")

        job_postings = []
        for listing in listings:
            try:
                # Create minimal RawJobPosting with just title/URL/location
                job = RawJobPosting(
                    title=listing['title'],
                    url=listing['url'],
                    description="[Quick scan - full details not fetched]",  # Placeholder
                    location=listing['location'],
                    category=self.config.category,
                    posted_date=listing.get('posted_date'),
                    raw_html=None
                )
                job_postings.append(job)
            except Exception as e:
                logger.error(f"Failed to convert listing: {e}")
                continue

        logger.info(f"Converted {len(job_postings)} listings")
        return job_postings

    def _fetch_job_details(
        self,
        listings: List[dict]
    ) -> List[RawJobPosting]:
        """
        Fetch full job details for each listing.

        Args:
            listings: List of basic listing information

        Returns:
            List of complete RawJobPosting objects
        """
        # Limit to max_jobs_to_analyze to prevent scraping 490+ jobs
        limited_listings = listings[:self.config.max_jobs_to_analyze]

        if len(listings) > self.config.max_jobs_to_analyze:
            logger.info(
                f"Limiting to first {self.config.max_jobs_to_analyze} jobs "
                f"(found {len(listings)} total listings)"
            )

        logger.info(f"Fetching details for {len(limited_listings)} jobs")

        job_postings = []

        for idx, listing in enumerate(limited_listings):
            try:
                # Remove emojis/special chars from title for logging (Windows console encoding issue)
                safe_title = listing['title'].encode('ascii', 'ignore').decode('ascii')
                logger.info(
                    f"Fetching job detail {idx + 1}/{len(limited_listings)}: "
                    f"{safe_title if safe_title else 'Job listing'}"
                )

                # Fetch job detail page
                html = self._fetch_page(listing['url'])

                # Parse description
                description = self._parse_job_detail(html, listing['url'])

                if not description:
                    logger.warning(f"Skipping job with no description: {listing['url']}")
                    continue

                # Create RawJobPosting
                job = RawJobPosting(
                    title=listing['title'],
                    url=listing['url'],
                    description=description,
                    location=listing['location'],
                    category=self.config.category,
                    posted_date=listing.get('posted_date'),
                    raw_html=html
                )

                job_postings.append(job)

                # Random delay between detail fetches
                if idx < len(listings) - 1:
                    self._random_delay()

            except Exception as e:
                logger.error(
                    f"Failed to fetch details for {listing['url']}: {e}"
                )
                continue

        logger.info(
            f"Successfully fetched details for {len(job_postings)} jobs"
        )

        return job_postings

    def scrape_single_job(self, url: str) -> Optional[RawJobPosting]:
        """
        Scrape a single job posting by URL.

        Args:
            url: Full URL to the job posting

        Returns:
            RawJobPosting or None if failed
        """
        logger.info(f"Scraping single job: {url}")

        try:
            # Fetch the page
            html = self._fetch_page(url)

            # Parse description
            description = self._parse_job_detail(html, url)

            if not description:
                return None

            # Extract title from HTML
            soup = BeautifulSoup(html, 'lxml')
            title_elem = soup.find('span', id='titletextonly')
            title = title_elem.text.strip() if title_elem else "Unknown Title"

            # Create job posting
            job = RawJobPosting(
                title=title,
                url=url,
                description=description,
                location=self.config.city,
                category=self.config.category,
                raw_html=html
            )

            logger.info(f"Successfully scraped job: {title}")
            return job

        except Exception as e:
            logger.error(f"Failed to scrape job {url}: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to Craigslist.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            url = self.BASE_URL.format(
                city=self.config.city,
                category=self.config.category
            )

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            logger.info("Connection test successful")
            return True

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
