"""
Batch Processor Agent using OpenAI's Batch API.
Processes hundreds/thousands of job postings asynchronously at 50% cost reduction.
"""
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from openai import OpenAI

from config import Config
from utils import get_logger

logger = get_logger(__name__)


class BatchProcessorAgent:
    """
    Agent for processing large volumes of job postings using OpenAI Batch API.
    
    Benefits:
    - 50% cost reduction compared to synchronous API
    - Higher rate limits (separate pool)
    - 24-hour completion window
    - Process thousands of jobs overnight
    """
    
    def __init__(self, output_dir: str = "output/batches"):
        """
        Initialize Batch Processor Agent.
        
        Args:
            output_dir: Directory for batch files and results
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"BatchProcessorAgent initialized (output_dir={output_dir})")
    
    def create_batch_input_file(
        self,
        job_postings: List[Dict[str, Any]],
        task_type: str = "analyze",
        model: str = "gpt-4o-mini"
    ) -> str:
        """
        Create .jsonl batch input file from job postings.
        
        Args:
            job_postings: List of job posting dictionaries
            task_type: Type of task (analyze, qualify, extract_pain_points, etc.)
            model: OpenAI model to use
        
        Returns:
            Path to created .jsonl file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"batch_input_{task_type}_{timestamp}.jsonl"
        
        logger.info(f"Creating batch input file: {filename}")
        
        with open(filename, 'w') as f:
            for idx, job in enumerate(job_postings):
                custom_id = f"{task_type}_{job.get('url', f'job_{idx}')}"
                
                # Build request based on task type
                if task_type == "analyze":
                    messages = self._build_analysis_messages(job)
                elif task_type == "qualify":
                    messages = self._build_qualification_messages(job)
                elif task_type == "extract_pain_points":
                    messages = self._build_pain_point_messages(job)
                elif task_type == "parse":
                    messages = self._build_parse_messages(job)
                else:
                    raise ValueError(f"Unknown task_type: {task_type}")
                
                # Create batch request line
                request = {
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.3,
                        "response_format": {"type": "json_object"}
                    }
                }
                
                f.write(json.dumps(request) + '\n')
        
        logger.info(f"Created batch input with {len(job_postings)} requests")
        return str(filename)
    
    def _build_analysis_messages(self, job: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages for complete job analysis."""
        prompt = f"""Analyze this job posting for Forecasta (workforce analytics platform):

Company: {job.get('company_name', 'Unknown')}
Title: {job.get('title', 'Unknown')}
Location: {job.get('location', 'Unknown')}
Description: {job.get('description', 'N/A')[:2000]}

Provide:
1. Qualification tier (TIER 1-5, where TIER 1 = best fit)
2. Pain points (workforce challenges this company faces)
3. Company size estimate
4. Industry
5. Forecasta fit score (0-100)
6. Recommended next steps

Format as JSON with keys: tier, pain_points, company_size, industry, fit_score, next_steps"""
        
        return [
            {"role": "system", "content": "You are an expert sales analyst for workforce analytics software."},
            {"role": "user", "content": prompt}
        ]
    
    def _build_qualification_messages(self, job: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages for quick qualification."""
        prompt = f"""Qualify this company as a sales lead (quick analysis):

Company: {job.get('company_name', 'Unknown')}
Title: {job.get('title', 'Unknown')}
Description: {job.get('description', 'N/A')[:1500]}

Return JSON:
- qualified: true/false
- tier: TIER 1-5 (if qualified)
- reason: brief explanation"""
        
        return [
            {"role": "system", "content": "You are a sales qualification expert."},
            {"role": "user", "content": prompt}
        ]
    
    def _build_pain_point_messages(self, job: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages for pain point extraction."""
        prompt = f"""Extract workforce pain points from this job posting:

{job.get('description', 'N/A')[:2000]}

Return JSON array of pain points as strings.
Focus on: turnover, scaling, hiring challenges, retention, optimization needs."""
        
        return [
            {"role": "system", "content": "You are an expert at identifying business pain points."},
            {"role": "user", "content": prompt}
        ]
    
    def _build_parse_messages(self, job: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages for structured parsing."""
        prompt = f"""Parse this job posting into structured data:

{job.get('description', 'N/A')[:2000]}

Return JSON:
- title: job title
- company: company name
- location: location
- required_skills: array of required skills
- nice_to_have_skills: array of preferred skills
- salary_range: if mentioned
- work_arrangement: remote/hybrid/onsite
- experience_years: required years"""
        
        return [
            {"role": "system", "content": "You are an expert job posting parser."},
            {"role": "user", "content": prompt}
        ]
    
    def upload_batch_file(self, input_file: str) -> str:
        """
        Upload batch input file to OpenAI.
        
        Args:
            input_file: Path to .jsonl input file
        
        Returns:
            File ID
        """
        logger.info(f"Uploading batch file: {input_file}")
        
        with open(input_file, 'rb') as f:
            file_obj = self.client.files.create(
                file=f,
                purpose="batch"
            )
        
        logger.info(f"File uploaded: {file_obj.id}")
        return file_obj.id
    
    def create_batch(
        self,
        input_file_id: str,
        endpoint: str = "/v1/chat/completions",
        description: Optional[str] = None
    ) -> str:
        """
        Create a batch processing job.
        
        Args:
            input_file_id: ID of uploaded input file
            endpoint: API endpoint to use
            description: Optional batch description
        
        Returns:
            Batch ID
        """
        logger.info(f"Creating batch with input file: {input_file_id}")
        
        metadata = {}
        if description:
            metadata['description'] = description
        
        batch = self.client.batches.create(
            input_file_id=input_file_id,
            endpoint=endpoint,
            completion_window="24h",
            metadata=metadata if metadata else None
        )
        
        logger.info(f"Batch created: {batch.id} (status: {batch.status})")
        return batch.id
    
    def check_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Check the status of a batch.
        
        Args:
            batch_id: Batch ID
        
        Returns:
            Batch status information
        """
        batch = self.client.batches.retrieve(batch_id)
        
        return {
            'id': batch.id,
            'status': batch.status,
            'created_at': batch.created_at,
            'completed_at': batch.completed_at,
            'failed_at': batch.failed_at,
            'expired_at': batch.expired_at,
            'request_counts': {
                'total': batch.request_counts.total,
                'completed': batch.request_counts.completed,
                'failed': batch.request_counts.failed
            },
            'output_file_id': batch.output_file_id,
            'error_file_id': batch.error_file_id
        }
    
    def wait_for_batch(
        self,
        batch_id: str,
        check_interval: int = 60,
        max_wait: int = 86400
    ) -> Dict[str, Any]:
        """
        Wait for batch to complete (blocking).
        
        Args:
            batch_id: Batch ID
            check_interval: Seconds between status checks
            max_wait: Maximum seconds to wait (default 24h)
        
        Returns:
            Final batch status
        """
        logger.info(f"Waiting for batch {batch_id} to complete...")
        
        start_time = time.time()
        
        while True:
            status = self.check_batch_status(batch_id)
            
            logger.info(f"Batch {batch_id}: {status['status']} "
                       f"({status['request_counts']['completed']}/{status['request_counts']['total']} completed)")
            
            if status['status'] in ['completed', 'failed', 'expired', 'cancelled']:
                logger.info(f"Batch {batch_id} finished with status: {status['status']}")
                return status
            
            elapsed = time.time() - start_time
            if elapsed > max_wait:
                logger.warning(f"Batch {batch_id} exceeded max wait time ({max_wait}s)")
                return status
            
            time.sleep(check_interval)
    
    def download_results(self, batch_id: str) -> str:
        """
        Download batch results to local file.
        
        Args:
            batch_id: Batch ID
        
        Returns:
            Path to downloaded results file
        """
        status = self.check_batch_status(batch_id)
        
        if not status['output_file_id']:
            raise ValueError(f"Batch {batch_id} has no output file (status: {status['status']})")
        
        logger.info(f"Downloading results from batch {batch_id}")
        
        # Download results
        file_response = self.client.files.content(status['output_file_id'])
        
        # Save to file
        output_file = self.output_dir / f"batch_output_{batch_id}.jsonl"
        with open(output_file, 'w') as f:
            f.write(file_response.text)
        
        logger.info(f"Results saved to: {output_file}")
        
        # Download error file if exists
        if status['error_file_id']:
            logger.info(f"Downloading error file from batch {batch_id}")
            error_response = self.client.files.content(status['error_file_id'])
            error_file = self.output_dir / f"batch_errors_{batch_id}.jsonl"
            with open(error_file, 'w') as f:
                f.write(error_response.text)
            logger.info(f"Errors saved to: {error_file}")
        
        return str(output_file)
    
    def parse_results(self, results_file: str) -> List[Dict[str, Any]]:
        """
        Parse batch results file into structured data.
        
        Args:
            results_file: Path to results .jsonl file
        
        Returns:
            List of parsed results
        """
        logger.info(f"Parsing results from: {results_file}")
        
        results = []
        with open(results_file, 'r') as f:
            for line in f:
                if line.strip():
                    result = json.loads(line)
                    
                    # Extract key data
                    parsed = {
                        'custom_id': result.get('custom_id'),
                        'status_code': result['response']['status_code'],
                        'success': result['error'] is None,
                    }
                    
                    if parsed['success']:
                        # Parse response content
                        content = result['response']['body']['choices'][0]['message']['content']
                        try:
                            parsed['data'] = json.loads(content)
                        except json.JSONDecodeError:
                            parsed['data'] = {'raw_content': content}
                        
                        # Add usage stats
                        parsed['tokens_used'] = result['response']['body']['usage']['total_tokens']
                    else:
                        parsed['error'] = result['error']
                    
                    results.append(parsed)
        
        logger.info(f"Parsed {len(results)} results")
        return results
    
    def cancel_batch(self, batch_id: str) -> Dict[str, Any]:
        """
        Cancel a running batch.
        
        Args:
            batch_id: Batch ID
        
        Returns:
            Updated batch status
        """
        logger.info(f"Cancelling batch {batch_id}")
        
        batch = self.client.batches.cancel(batch_id)
        
        return {
            'id': batch.id,
            'status': batch.status
        }
    
    def list_batches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent batches.
        
        Args:
            limit: Number of batches to return
        
        Returns:
            List of batch summaries
        """
        batches = self.client.batches.list(limit=limit)
        
        return [{
            'id': b.id,
            'status': b.status,
            'created_at': b.created_at,
            'request_counts': {
                'total': b.request_counts.total,
                'completed': b.request_counts.completed,
                'failed': b.request_counts.failed
            }
        } for b in batches.data]


# Convenience function for complete batch workflow
def process_jobs_batch(
    job_postings: List[Dict[str, Any]],
    task_type: str = "analyze",
    wait_for_completion: bool = False,
    model: str = "gpt-4o-mini"
) -> Dict[str, Any]:
    """
    Process job postings in batch mode (complete workflow).
    
    Args:
        job_postings: List of job posting dictionaries
        task_type: Type of analysis (analyze, qualify, parse, etc.)
        wait_for_completion: If True, blocks until batch completes
        model: Model to use (gpt-4o-mini recommended for cost)
    
    Returns:
        Batch information and results (if wait_for_completion=True)
    """
    agent = BatchProcessorAgent()
    
    # Step 1: Create input file
    logger.info(f"Creating batch for {len(job_postings)} jobs (task: {task_type})")
    input_file = agent.create_batch_input_file(job_postings, task_type, model)
    
    # Step 2: Upload
    file_id = agent.upload_batch_file(input_file)
    
    # Step 3: Create batch
    batch_id = agent.create_batch(
        file_id,
        description=f"{task_type} for {len(job_postings)} jobs"
    )
    
    result = {
        'batch_id': batch_id,
        'input_file': input_file,
        'file_id': file_id,
        'job_count': len(job_postings),
        'task_type': task_type
    }
    
    # Step 4: Wait for completion (optional)
    if wait_for_completion:
        logger.info("Waiting for batch to complete (this may take up to 24 hours)...")
        final_status = agent.wait_for_batch(batch_id)
        result['final_status'] = final_status
        
        # Step 5: Download results
        if final_status['status'] == 'completed':
            results_file = agent.download_results(batch_id)
            parsed_results = agent.parse_results(results_file)
            
            result['results_file'] = results_file
            result['results'] = parsed_results
            result['success_count'] = sum(1 for r in parsed_results if r['success'])
            result['error_count'] = sum(1 for r in parsed_results if not r['success'])
    
    return result
