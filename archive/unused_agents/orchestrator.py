"""Orchestrator - Coordinates the multi-agent workflow."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .extractor import ExtractorAgent
from .researcher import ResearcherAgent
from .scorer import ScorerAgent
from .analyzer import AnalyzerAgent
from .writer import WriterAgent
from .storer import StorerAgent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates the workflow between all agents."""

    def __init__(self, web_search_tool=None, data_dir: str = "data/leads"):
        self.extractor = ExtractorAgent()
        self.researcher = ResearcherAgent(web_search_tool=web_search_tool)
        self.scorer = ScorerAgent()
        self.analyzer = AnalyzerAgent()
        self.writer = WriterAgent()
        self.storer = StorerAgent(data_dir=data_dir)

        self.max_retries = 3

    def process_posting(self, posting_html: str, posting_url: str) -> Dict[str, Any]:
        """
        Process a single job posting through the complete pipeline.

        Args:
            posting_html: Raw HTML of the posting
            posting_url: URL of the posting

        Returns:
            Fully processed lead data
        """
        logger.info(f"Processing posting: {posting_url}")

        # Step 1: Extract
        data = self._run_with_retry(
            self.extractor.extract,
            posting_html,
            posting_url,
            step_name="extraction"
        )

        if data.get('extraction_status') == 'error':
            logger.error(f"Extraction failed: {data.get('error_message')}")
            return data

        # Step 2: Research
        data = self._run_with_retry(
            self.researcher.research,
            data,
            step_name="research"
        )

        # Validate company after research
        data = self.researcher.validate_company(data)

        # Step 3: Score
        data = self._run_with_retry(
            self.scorer.score,
            data,
            step_name="scoring"
        )

        # Step 4: Analyze (skip if score < 10)
        if data.get('score', 0) >= 10:
            data = self._run_with_retry(
                self.analyzer.analyze,
                data,
                step_name="analysis"
            )
        else:
            logger.info(f"Skipping analysis - score too low: {data.get('score')}")
            data['analysis_status'] = 'skipped'
            data['analysis_reason'] = 'score_below_threshold'

        # Step 5: Write (skip if tier > 3)
        tier = data.get('tier', 5)
        if tier <= 3:
            data = self._run_with_retry(
                self.writer.write,
                data,
                step_name="writing"
            )
        else:
            logger.info(f"Skipping writing - tier too low: {tier}")
            data['writing_status'] = 'skipped'
            data['writing_reason'] = 'tier_below_threshold'

        # Step 6: Store
        data = self._run_with_retry(
            self.storer.store,
            data,
            step_name="storage"
        )

        logger.info(f"Processing complete. Lead ID: {data.get('lead_id')}, Tier: {tier}, Score: {data.get('score')}")

        return data

    def process_batch(self, postings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process multiple postings in batch.

        Args:
            postings: List of dicts with 'html' and 'url' keys

        Returns:
            List of processed leads
        """
        results = []
        total = len(postings)

        logger.info(f"Processing batch of {total} postings")

        for i, posting in enumerate(postings, 1):
            logger.info(f"Processing {i}/{total}")

            try:
                result = self.process_posting(
                    posting.get('html', ''),
                    posting.get('url', '')
                )
                results.append(result)

            except Exception as e:
                logger.error(f"Failed to process posting {posting.get('url')}: {e}")
                results.append({
                    'posting_url': posting.get('url'),
                    'processing_status': 'error',
                    'error': str(e)
                })

        logger.info(f"Batch processing complete. Processed {len(results)}/{total}")

        return results

    def _run_with_retry(self, func, *args, step_name: str = "step") -> Any:
        """Run a function with retry logic."""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                result = func(*args)
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"{step_name} attempt {attempt + 1} failed: {e}")

                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying {step_name}...")
                else:
                    logger.error(f"{step_name} failed after {self.max_retries} attempts")

        # Return error result
        if args:
            base_data = args[0] if isinstance(args[0], dict) else {}
        else:
            base_data = {}

        return {
            **base_data,
            f"{step_name}_status": "error",
            f"{step_name}_error": str(last_error)
        }

    def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a lead by ID."""
        return self.storer.get_lead(lead_id)

    def get_all_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve all leads with optional filters."""
        return self.storer.get_all_leads(filters)

    def update_lead_status(self, lead_id: str, status: str, notes: str = None) -> bool:
        """Update lead status."""
        return self.storer.update_lead_status(lead_id, status, notes)

    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics from stored leads."""
        return self.storer.get_analytics()

    def generate_bulk_scripts(self, lead_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate call scripts for multiple leads."""
        results = []

        for lead_id in lead_ids:
            lead = self.get_lead(lead_id)
            if not lead:
                results.append({
                    'lead_id': lead_id,
                    'status': 'error',
                    'error': 'Lead not found'
                })
                continue

            # If script doesn't exist, generate it
            if not lead.get('call_script'):
                # Re-run writer
                lead = self.writer.write(lead)
                # Update stored lead
                self.storer.store(lead)

            results.append({
                'lead_id': lead_id,
                'company_name': lead.get('company_name'),
                'call_script': lead.get('call_script'),
                'status': 'success'
            })

        return results

    def generate_bulk_emails(self, lead_ids: List[str]) -> List[Dict[str, Any]]:
        """Generate email templates for multiple leads."""
        results = []

        for lead_id in lead_ids:
            lead = self.get_lead(lead_id)
            if not lead:
                results.append({
                    'lead_id': lead_id,
                    'status': 'error',
                    'error': 'Lead not found'
                })
                continue

            # If email doesn't exist, generate it
            if not lead.get('email_template'):
                # Re-run writer
                lead = self.writer.write(lead)
                # Update stored lead
                self.storer.store(lead)

            results.append({
                'lead_id': lead_id,
                'company_name': lead.get('company_name'),
                'email_template': lead.get('email_template'),
                'status': 'success'
            })

        return results

    def export_leads_csv(self, lead_ids: List[str] = None) -> str:
        """Export leads to CSV format."""
        import csv
        from io import StringIO

        # Get leads
        if lead_ids:
            leads = [self.get_lead(lid) for lid in lead_ids if self.get_lead(lid)]
        else:
            leads = self.get_all_leads()

        # Create CSV in memory
        output = StringIO()
        if not leads:
            return ""

        # Define fields
        fields = [
            'lead_id', 'company_name', 'job_title', 'location', 'industry',
            'score', 'tier', 'employee_count', 'is_local', 'posting_url',
            'status', 'value_proposition'
        ]

        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()

        for lead in leads:
            row = {field: lead.get(field, '') for field in fields}
            writer.writerow(row)

        return output.getvalue()
