"""
Database Agent for managing job data in Supabase (PostgreSQL).
Handles CRUD operations, history tracking, and data retrieval.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client

from config import Config
from utils import get_logger, generate_job_id
from models import RawJobPosting, ParsedJobPosting

logger = get_logger(__name__)


class DatabaseAgent:
    """Agent for database operations using Supabase."""

    def __init__(self):
        """Initialize the Database Agent."""
        try:
            self.client: Client = create_client(
                Config.SUPABASE_URL,
                Config.SUPABASE_KEY
            )
            logger.info("DatabaseAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DatabaseAgent: {e}")
            raise

    def insert_raw_job(self, raw_job: RawJobPosting) -> bool:
        """
        Insert a raw job posting into the database.

        Args:
            raw_job: Raw job posting from scraper

        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'url': raw_job.url,
                'title': raw_job.title,
                'description': raw_job.description,
                'location': raw_job.location,
                'category': raw_job.category,
                'posted_date': raw_job.posted_date,
                'raw_html': raw_job.raw_html,
                'scraped_at': raw_job.scraped_at.isoformat(),
                'processed': False,
            }

            result = self.client.table('raw_jobs').insert(data).execute()

            logger.info(f"Inserted raw job: {raw_job.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert raw job: {e}")
            return False

    def insert_raw_jobs(self, raw_jobs: List[RawJobPosting]) -> int:
        """
        Insert multiple raw job postings.

        Args:
            raw_jobs: List of raw job postings

        Returns:
            Number of successfully inserted jobs
        """
        logger.info(f"Inserting {len(raw_jobs)} raw jobs")

        success_count = 0

        # Batch insert
        batch_size = 100
        for i in range(0, len(raw_jobs), batch_size):
            batch = raw_jobs[i:i + batch_size]

            try:
                data_batch = [
                    {
                        'url': job.url,
                        'title': job.title,
                        'description': job.description,
                        'location': job.location,
                        'category': job.category,
                        'posted_date': job.posted_date,
                        'raw_html': job.raw_html,
                        'scraped_at': job.scraped_at.isoformat(),
                        'processed': False,
                    }
                    for job in batch
                ]

                result = self.client.table('raw_jobs').insert(data_batch).execute()
                success_count += len(batch)

                logger.info(f"Inserted batch {i // batch_size + 1}: {len(batch)} jobs")

            except Exception as e:
                logger.error(f"Failed to insert batch: {e}")
                continue

        logger.info(f"Successfully inserted {success_count}/{len(raw_jobs)} raw jobs")
        return success_count

    def insert_parsed_job(self, parsed_job: ParsedJobPosting) -> bool:
        """
        Insert a parsed job posting into the database.

        Args:
            parsed_job: Parsed job posting

        Returns:
            True if successful, False otherwise
        """
        try:
            job_id = generate_job_id(parsed_job.url)

            data = {
                'job_id': job_id,
                'url': parsed_job.url,
                'title': parsed_job.title,
                'description': parsed_job.description,
                'location': parsed_job.location,
                'category': parsed_job.category,
                'posted_date': parsed_job.posted_date,
                'skills': parsed_job.skills,
                'pain_points': parsed_job.pain_points,
                'salary_min': parsed_job.salary_min,
                'salary_max': parsed_job.salary_max,
                'salary_text': parsed_job.salary_text,
                'is_remote': parsed_job.is_remote,
                'is_hybrid': parsed_job.is_hybrid,
                'is_onsite': parsed_job.is_onsite,
                'relevance_score': parsed_job.relevance_score,
                'parsed_at': parsed_job.parsed_at.isoformat(),
            }

            # Upsert (insert or update if exists)
            result = self.client.table('jobs').upsert(
                data,
                on_conflict='job_id'
            ).execute()

            logger.info(f"Inserted parsed job: {parsed_job.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to insert parsed job: {e}")
            return False

    def insert_parsed_jobs(self, parsed_jobs: List[ParsedJobPosting]) -> int:
        """
        Insert multiple parsed job postings.

        Args:
            parsed_jobs: List of parsed job postings

        Returns:
            Number of successfully inserted jobs
        """
        logger.info(f"Inserting {len(parsed_jobs)} parsed jobs")

        success_count = 0

        # Batch insert
        batch_size = 100
        for i in range(0, len(parsed_jobs), batch_size):
            batch = parsed_jobs[i:i + batch_size]

            try:
                data_batch = [
                    {
                        'job_id': generate_job_id(job.url),
                        'url': job.url,
                        'title': job.title,
                        'description': job.description,
                        'location': job.location,
                        'category': job.category,
                        'posted_date': job.posted_date,
                        'skills': job.skills,
                        'pain_points': job.pain_points,
                        'salary_min': job.salary_min,
                        'salary_max': job.salary_max,
                        'salary_text': job.salary_text,
                        'is_remote': job.is_remote,
                        'is_hybrid': job.is_hybrid,
                        'is_onsite': job.is_onsite,
                        'relevance_score': job.relevance_score,
                        'parsed_at': job.parsed_at.isoformat(),
                    }
                    for job in batch
                ]

                result = self.client.table('jobs').upsert(
                    data_batch,
                    on_conflict='job_id'
                ).execute()

                success_count += len(batch)

                logger.info(f"Inserted batch {i // batch_size + 1}: {len(batch)} jobs")

            except Exception as e:
                logger.error(f"Failed to insert batch: {e}")
                continue

        logger.info(f"Successfully inserted {success_count}/{len(parsed_jobs)} parsed jobs")
        return success_count

    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a job by its ID.

        Args:
            job_id: Job ID

        Returns:
            Job data or None if not found
        """
        try:
            result = self.client.table('jobs').select('*').eq(
                'job_id', job_id
            ).execute()

            if result.data:
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

    def get_job_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a job by its URL.

        Args:
            url: Job URL

        Returns:
            Job data or None if not found
        """
        try:
            result = self.client.table('jobs').select('*').eq(
                'url', url
            ).execute()

            if result.data:
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to get job by URL: {e}")
            return None

    def get_recent_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get most recently scraped jobs.

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job dictionaries
        """
        try:
            result = self.client.table('jobs').select('*').order(
                'scraped_at', desc=True
            ).limit(limit).execute()

            logger.info(f"Retrieved {len(result.data)} recent jobs")
            return result.data

        except Exception as e:
            logger.error(f"Failed to get recent jobs: {e}")
            return []

    def get_jobs_by_criteria(
        self,
        location: Optional[str] = None,
        category: Optional[str] = None,
        is_remote: Optional[bool] = None,
        min_relevance: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get jobs matching specific criteria.

        Args:
            location: Filter by location
            category: Filter by category
            is_remote: Filter by remote status
            min_relevance: Minimum relevance score
            limit: Maximum number of results

        Returns:
            List of matching jobs
        """
        try:
            query = self.client.table('jobs').select('*')

            if location:
                query = query.eq('location', location)

            if category:
                query = query.eq('category', category)

            if is_remote is not None:
                query = query.eq('is_remote', is_remote)

            if min_relevance is not None:
                query = query.gte('relevance_score', min_relevance)

            result = query.order('scraped_at', desc=True).limit(limit).execute()

            logger.info(f"Retrieved {len(result.data)} jobs matching criteria")
            return result.data

        except Exception as e:
            logger.error(f"Failed to get jobs by criteria: {e}")
            return []

    def search_jobs(
        self,
        search_term: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search jobs by text in title or description.

        Args:
            search_term: Text to search for
            limit: Maximum number of results

        Returns:
            List of matching jobs
        """
        try:
            # Use text search on title and description
            result = self.client.table('jobs').select('*').or_(
                f"title.ilike.%{search_term}%,description.ilike.%{search_term}%"
            ).limit(limit).execute()

            logger.info(f"Found {len(result.data)} jobs matching '{search_term}'")
            return result.data

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def update_job(
        self,
        job_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a job's data.

        Args:
            job_id: Job ID to update
            updates: Dictionary of fields to update

        Returns:
            True if successful
        """
        try:
            result = self.client.table('jobs').update(updates).eq(
                'job_id', job_id
            ).execute()

            logger.info(f"Updated job: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update job: {e}")
            return False

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from the database.

        Args:
            job_id: Job ID to delete

        Returns:
            True if successful
        """
        try:
            result = self.client.table('jobs').delete().eq(
                'job_id', job_id
            ).execute()

            logger.info(f"Deleted job: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete job: {e}")
            return False

    def create_scrape_run(
        self,
        city: str,
        category: str,
        keywords: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Create a new scrape run record.

        Args:
            city: City being scraped
            category: Category being scraped
            keywords: Optional keywords used

        Returns:
            Scrape run ID or None if failed
        """
        try:
            data = {
                'city': city,
                'category': category,
                'keywords': keywords or [],
                'status': 'running',
            }

            result = self.client.table('scrape_runs').insert(data).execute()

            if result.data:
                run_id = result.data[0]['id']
                logger.info(f"Created scrape run: {run_id}")
                return run_id

            return None

        except Exception as e:
            logger.error(f"Failed to create scrape run: {e}")
            return None

    def update_scrape_run(
        self,
        run_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a scrape run record.

        Args:
            run_id: Scrape run ID
            updates: Fields to update

        Returns:
            True if successful
        """
        try:
            result = self.client.table('scrape_runs').update(updates).eq(
                'id', run_id
            ).execute()

            logger.info(f"Updated scrape run: {run_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update scrape run: {e}")
            return False

    def complete_scrape_run(
        self,
        run_id: str,
        jobs_found: int,
        jobs_parsed: int,
        jobs_stored: int,
        error: Optional[str] = None
    ) -> bool:
        """
        Mark a scrape run as completed.

        Args:
            run_id: Scrape run ID
            jobs_found: Number of jobs found
            jobs_parsed: Number of jobs parsed
            jobs_stored: Number of jobs stored
            error: Optional error message

        Returns:
            True if successful
        """
        try:
            updates = {
                'jobs_found': jobs_found,
                'jobs_parsed': jobs_parsed,
                'jobs_stored': jobs_stored,
                'status': 'failed' if error else 'completed',
                'error_message': error,
                'completed_at': datetime.utcnow().isoformat(),
            }

            return self.update_scrape_run(run_id, updates)

        except Exception as e:
            logger.error(f"Failed to complete scrape run: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with various statistics
        """
        try:
            # Total jobs
            total_result = self.client.table('jobs').select(
                'id', count='exact'
            ).execute()
            total_jobs = total_result.count

            # Remote jobs
            remote_result = self.client.table('jobs').select(
                'id', count='exact'
            ).eq('is_remote', True).execute()
            remote_jobs = remote_result.count

            # Recent jobs (last 7 days)
            # Note: This is a simplified query, you might want to use SQL functions
            recent_result = self.client.table('jobs').select(
                'id', count='exact'
            ).gte(
                'scraped_at',
                (datetime.utcnow().replace(hour=0, minute=0, second=0) -
                 datetime.timedelta(days=7)).isoformat()
            ).execute()
            recent_jobs = recent_result.count if recent_result else 0

            return {
                'total_jobs': total_jobs,
                'remote_jobs': remote_jobs,
                'recent_jobs_7d': recent_jobs,
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def mark_raw_job_processed(self, url: str) -> bool:
        """
        Mark a raw job as processed.

        Args:
            url: Job URL

        Returns:
            True if successful
        """
        try:
            result = self.client.table('raw_jobs').update({
                'processed': True
            }).eq('url', url).execute()

            return True

        except Exception as e:
            logger.error(f"Failed to mark job as processed: {e}")
            return False
