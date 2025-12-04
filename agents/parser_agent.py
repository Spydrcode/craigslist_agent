"""
Parser Agent for processing raw job postings.
Extracts structured data including skills, pain points, salary, and work arrangement.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from utils import get_logger, extract_salary_info, detect_work_arrangement, generate_job_id
from models import RawJobPosting, ParsedJobPosting, JobSignal
from agents.client_agent import ClientAgent

logger = get_logger(__name__)


class ParserAgent:
    """Agent for parsing and structuring job posting data."""

    def __init__(self, client_agent: Optional[ClientAgent] = None, use_structured_extraction: bool = True):
        """
        Initialize the Parser Agent.

        Args:
            client_agent: ClientAgent instance for AI-powered parsing
            use_structured_extraction: Use function calling for better data extraction
        """
        self.client = client_agent or ClientAgent()
        self.use_structured_extraction = use_structured_extraction
        logger.info(f"ParserAgent initialized (structured_extraction={use_structured_extraction})")

    def parse_job(
        self,
        raw_job: RawJobPosting,
        use_ai: bool = True
    ) -> ParsedJobPosting:
        """
        Parse a raw job posting into structured data.

        Args:
            raw_job: Raw job posting from scraper
            use_ai: Whether to use AI for advanced extraction

        Returns:
            Parsed job posting with structured data
        """
        logger.info(f"Parsing job: {raw_job.title}")

        # Start with basic information
        parsed_data = {
            'title': raw_job.title,
            'url': raw_job.url,
            'description': raw_job.description,
            'location': raw_job.location,
            'category': raw_job.category,
            'posted_date': raw_job.posted_date,
        }

        # Extract salary information using regex
        salary_min, salary_max, salary_text = extract_salary_info(
            raw_job.description
        )
        parsed_data['salary_min'] = salary_min
        parsed_data['salary_max'] = salary_max
        parsed_data['salary_text'] = salary_text

        # Detect work arrangement using keywords
        work_info = detect_work_arrangement(raw_job.description)
        parsed_data['is_remote'] = work_info['is_remote']
        parsed_data['is_hybrid'] = work_info['is_hybrid']
        parsed_data['is_onsite'] = work_info['is_onsite']

        # Use AI for advanced extraction if enabled
        if use_ai:
            try:
                # Extract company name first (critical for grouping)
                company_name = self._extract_company_name(raw_job.title, raw_job.description)
                parsed_data['company_name'] = company_name
                logger.info(f"Extracted company name: {company_name}")
                
                # PRIORITY: Use structured function calling if enabled
                if self.use_structured_extraction:
                    logger.info("Using structured function calling for data extraction")
                    company_data = self.client.extract_company_info_structured(
                        job_description=raw_job.description,
                        job_title=raw_job.title
                    )
                    
                    # Map structured data to parsed_data
                    parsed_data['pain_points'] = company_data.get('pain_points', [])
                    parsed_data['skills'] = company_data.get('hiring_volume_signals', [])  # Approximate mapping
                    
                    logger.info(f"AI extraction: {len(parsed_data['pain_points'])} pain points, {len(parsed_data['skills'])} skills")
                    
                else:
                    # FALLBACK: Use freeform extraction
                    # Extract pain points
                    pain_points = self.client.extract_pain_points(
                        raw_job.description
                    )
                    parsed_data['pain_points'] = pain_points

                    # Extract skills
                    skills_data = self.client.extract_skills(raw_job.description)
                    all_skills = (
                        skills_data.get('required', []) +
                        skills_data.get('nice_to_have', [])
                    )
                    parsed_data['skills'] = all_skills

                    logger.info(
                        f"AI extraction: {len(pain_points)} pain points, "
                        f"{len(all_skills)} skills"
                    )

            except Exception as e:
                logger.error(f"AI extraction failed: {e}")
                logger.error(f"AI extraction failed: {e}")
                parsed_data['pain_points'] = []
                parsed_data['skills'] = []
                parsed_data['company_name'] = 'Unknown'
        else:
            # Basic keyword extraction if AI not used
            parsed_data['pain_points'] = self._extract_pain_points_basic(
                raw_job.description
            )
            parsed_data['skills'] = self._extract_skills_basic(
                raw_job.description
            )
            parsed_data['company_name'] = self._extract_company_name(raw_job.title, raw_job.description)

        # Create ParsedJobPosting
        parsed_job = ParsedJobPosting(**parsed_data)

        logger.info(f"Successfully parsed job: {parsed_job.title}")
        return parsed_jobs

    def extract_job_signal(
        self,
        raw_job: RawJobPosting,
        use_ai: bool = True
    ) -> JobSignal:
        """
        Extract growth signals from job posting (NO company contact extraction).
        
        This method analyzes the job posting to identify industry trends and hiring signals,
        NOT to find company names or contact information.
        
        Args:
            raw_job: Raw job posting from scraper
            use_ai: Whether to use AI for classification (recommended)
            
        Returns:
            JobSignal with industry, category, urgency, and growth indicators
        """
        logger.info(f"Extracting signals from: {raw_job.title}")
        
        signal_data = {
            'job_url': raw_job.url,
            'job_title': raw_job.title,
            'posted_date': raw_job.posted_date,
            'location': raw_job.location,
        }
        
        if use_ai:
            try:
                # Use AI to extract comprehensive signals
                extraction_prompt = f"""Analyze this job posting and extract hiring signals (NOT company information).

Job Title: {raw_job.title}
Location: {raw_job.location}
Description: {raw_job.description[:1500]}

Extract the following signals:
1. industry: What industry/sector is this? (e.g., "Technology", "Healthcare", "Construction", "Finance")
2. job_category: What type of role? (e.g., "Software Engineering", "Sales", "Marketing", "Operations")
3. urgency_level: How urgent is this hire? (Options: "high", "medium", "low")
   - high: Immediate hire, urgent, ASAP, fast-growing team
   - medium: Standard hiring timeline
   - low: Exploratory, future need
4. num_roles: How many positions? (Extract number or default to 1)
5. seniority_level: Experience level? (Options: "junior", "mid", "senior", "executive")
6. growth_indicators: List any growth signals (e.g., ["expanding team", "new office", "scaling", "funded"])
7. required_skills: Top 5-7 key skills mentioned

Return a JSON object with these exact fields. Be specific and accurate."""

                response = self.client.client.chat.completions.create(
                    model=self.client.model,
                    messages=[{"role": "user", "content": extraction_prompt}],
                    temperature=0,
                    response_format={"type": "json_object"}
                )
                
                import json
                ai_signals = json.loads(response.choices[0].message.content)
                
                # Map AI response to signal_data
                signal_data['industry'] = ai_signals.get('industry', 'Unknown')
                signal_data['job_category'] = ai_signals.get('job_category', 'Unknown')
                signal_data['urgency_level'] = ai_signals.get('urgency_level', 'medium')
                signal_data['num_roles'] = int(ai_signals.get('num_roles', 1))
                signal_data['seniority_level'] = ai_signals.get('seniority_level', 'mid')
                signal_data['growth_indicators'] = ai_signals.get('growth_indicators', [])
                signal_data['required_skills'] = ai_signals.get('required_skills', [])
                
                # Detect remote work
                work_info = detect_work_arrangement(raw_job.description)
                signal_data['is_remote'] = work_info['is_remote']
                
                logger.info(f"AI signals extracted: {signal_data['industry']} / {signal_data['job_category']}")
                
            except Exception as e:
                logger.error(f"AI signal extraction failed: {e}")
                # Fallback to basic extraction
                signal_data.update(self._extract_signals_basic(raw_job))
        else:
            # Basic keyword-based extraction
            signal_data.update(self._extract_signals_basic(raw_job))
        
        # Create JobSignal
        job_signal = JobSignal(**signal_data)
        logger.info(f"Signal extracted: {job_signal.industry} - {job_signal.job_category}")
        
        return job_signal
    
    def extract_signals_batch(
        self,
        raw_jobs: List[RawJobPosting],
        use_ai: bool = True
    ) -> List[JobSignal]:
        """
        Extract signals from multiple job postings.
        
        Args:
            raw_jobs: List of raw job postings
            use_ai: Whether to use AI
            
        Returns:
            List of JobSignal objects
        """
        logger.info(f"Extracting signals from {len(raw_jobs)} jobs")
        
        signals = []
        for idx, raw_job in enumerate(raw_jobs):
            try:
                logger.info(f"Processing job {idx + 1}/{len(raw_jobs)}")
                signal = self.extract_job_signal(raw_job, use_ai=use_ai)
                signals.append(signal)
            except Exception as e:
                logger.error(f"Failed to extract signal from {raw_job.url}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(signals)} signals")
        return signals
    
    def _extract_signals_basic(self, raw_job: RawJobPosting) -> Dict[str, Any]:
        """
        Basic signal extraction using keywords (fallback).
        
        Args:
            raw_job: Raw job posting
            
        Returns:
            Dictionary with basic signal data
        """
        title_lower = raw_job.title.lower()
        desc_lower = raw_job.description.lower() if raw_job.description else ""
        
        # Industry classification (basic)
        industry = "Unknown"
        if any(word in title_lower + desc_lower for word in ['software', 'developer', 'engineer', 'tech', 'data']):
            industry = "Technology"
        elif any(word in title_lower + desc_lower for word in ['sales', 'account', 'business development']):
            industry = "Sales & Business Development"
        elif any(word in title_lower + desc_lower for word in ['healthcare', 'medical', 'nurse', 'doctor']):
            industry = "Healthcare"
        elif any(word in title_lower + desc_lower for word in ['construction', 'contractor', 'builder']):
            industry = "Construction"
        
        # Job category
        job_category = "Unknown"
        if 'engineer' in title_lower:
            job_category = "Engineering"
        elif any(word in title_lower for word in ['sales', 'account']):
            job_category = "Sales"
        elif any(word in title_lower for word in ['market', 'growth']):
            job_category = "Marketing"
        elif any(word in title_lower for word in ['manager', 'director', 'lead']):
            job_category = "Management"
        
        # Urgency detection
        urgency_level = "medium"
        if any(word in desc_lower for word in ['urgent', 'immediate', 'asap', 'quickly']):
            urgency_level = "high"
        elif any(word in desc_lower for word in ['future', 'pipeline', 'potential']):
            urgency_level = "low"
        
        # Seniority detection
        seniority_level = "mid"
        if any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal', 'staff']):
            seniority_level = "senior"
        elif any(word in title_lower for word in ['junior', 'jr', 'entry', 'associate']):
            seniority_level = "junior"
        elif any(word in title_lower for word in ['director', 'vp', 'chief', 'executive', 'head of']):
            seniority_level = "executive"
        
        # Growth indicators
        growth_indicators = []
        growth_keywords = {
            'expanding team': ['expanding', 'growing team', 'scaling'],
            'new office': ['new office', 'new location'],
            'funded': ['series a', 'series b', 'funding', 'funded'],
            'rapid growth': ['rapid growth', 'fast-growing', 'high-growth'],
        }
        for indicator, keywords in growth_keywords.items():
            if any(kw in desc_lower for kw in keywords):
                growth_indicators.append(indicator)
        
        # Detect work arrangement
        work_info = detect_work_arrangement(raw_job.description)
        
        return {
            'industry': industry,
            'job_category': job_category,
            'urgency_level': urgency_level,
            'num_roles': 1,
            'seniority_level': seniority_level,
            'growth_indicators': growth_indicators,
            'required_skills': [],
            'is_remote': work_info['is_remote'],
        }

    def parse_jobs(
        self,
        raw_jobs: List[RawJobPosting],
        use_ai: bool = True
    ) -> List[ParsedJobPosting]:
        """
        Parse multiple job postings.

        Args:
            raw_jobs: List of raw job postings
            use_ai: Whether to use AI for extraction

        Returns:
            List of parsed job postings
        """
        logger.info(f"Parsing {len(raw_jobs)} jobs")

        parsed_jobs = []

        for idx, raw_job in enumerate(raw_jobs):
            try:
                logger.info(f"Parsing job {idx + 1}/{len(raw_jobs)}")
                parsed_job = self.parse_job(raw_job, use_ai=use_ai)
                parsed_jobs.append(parsed_job)

            except Exception as e:
                logger.error(
                    f"Failed to parse job {raw_job.url}: {e}"
                )
                continue

        logger.info(
            f"Successfully parsed {len(parsed_jobs)}/{len(raw_jobs)} jobs"
        )

        return parsed_jobs

    def score_job_relevance(
        self,
        parsed_job: ParsedJobPosting,
        criteria: Dict[str, Any]
    ) -> float:
        """
        Score job relevance based on criteria.

        Args:
            parsed_job: Parsed job posting
            criteria: Criteria for scoring (skills, location, etc.)

        Returns:
            Relevance score (0.0 to 1.0)
        """
        logger.info(f"Scoring relevance for: {parsed_job.title}")

        try:
            score = self.client.score_relevance(
                parsed_job.description,
                criteria
            )

            logger.info(f"Relevance score: {score:.2f}")
            return score

        except Exception as e:
            logger.error(f"Failed to score relevance: {e}")
            return 0.5

    def enrich_job(
        self,
        parsed_job: ParsedJobPosting,
        criteria: Optional[Dict[str, Any]] = None
    ) -> ParsedJobPosting:
        """
        Enrich a parsed job with additional AI analysis.

        Args:
            parsed_job: Parsed job posting
            criteria: Optional criteria for relevance scoring

        Returns:
            Enriched job posting
        """
        logger.info(f"Enriching job: {parsed_job.title}")

        try:
            # Get comprehensive analysis
            analysis = self.client.analyze_job_posting(
                parsed_job.url,
                parsed_job.description,
                criteria
            )

            # Update parsed job with analysis
            parsed_job.pain_points = analysis.pain_points
            parsed_job.skills = (
                analysis.required_skills +
                analysis.nice_to_have_skills
            )
            parsed_job.relevance_score = analysis.relevance_score

            logger.info("Job enrichment completed")

        except Exception as e:
            logger.error(f"Failed to enrich job: {e}")

        return parsed_job

    def _extract_pain_points_basic(self, description: str) -> List[str]:
        """
        Basic pain point extraction using keywords (fallback when AI not used).

        Args:
            description: Job description text

        Returns:
            List of potential pain points
        """
        pain_point_keywords = [
            'challenge', 'problem', 'issue', 'difficulty',
            'pain point', 'bottleneck', 'struggling',
            'need to improve', 'looking to solve'
        ]

        pain_points = []
        description_lower = description.lower()

        for keyword in pain_point_keywords:
            if keyword in description_lower:
                # Extract sentence containing keyword
                sentences = description.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        pain_points.append(sentence.strip())
                        break

        return pain_points[:5]  # Limit to top 5

    def _extract_skills_basic(self, description: str) -> List[str]:
        """
        Basic skill extraction using common tech keywords.

        Args:
            description: Job description text

        Returns:
            List of identified skills
        """
        # Common technical skills
        skill_keywords = [
            # Languages
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go',
            'rust', 'typescript', 'php', 'swift', 'kotlin',

            # Frameworks
            'react', 'angular', 'vue', 'django', 'flask', 'fastapi',
            'spring', 'express', 'nextjs', 'node.js',

            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
            'elasticsearch', 'dynamodb',

            # Cloud
            'aws', 'azure', 'gcp', 'google cloud', 'docker',
            'kubernetes', 'terraform',

            # Other
            'git', 'api', 'rest', 'graphql', 'microservices',
            'machine learning', 'ml', 'ai', 'data science',
        ]

        description_lower = description.lower()
        found_skills = []

        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())

        return list(set(found_skills))  # Remove duplicates

    def _extract_company_name(self, title: str, description: str) -> str:
        """
        Extract company name from job title or description.
        
        Args:
            title: Job title
            description: Job description
            
        Returns:
            Company name or 'Unknown'
        """
        import re
        
        # Pattern 1: "Company Name - Job Title" or "Company Name: Job Title"
        title_patterns = [
            r'^([A-Z][A-Za-z0-9\s&.,\'-]+?)(?:\s*[-:]\s*)',  # Company - Title
            r'^(.+?)\s+(?:is hiring|seeks|looking for)',  # Company is hiring...
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, title)
            if match:
                company = match.group(1).strip()
                # Filter out generic titles
                if len(company) > 2 and not any(word in company.lower() for word in ['hiring', 'wanted', 'needed', 'looking']):
                    return company
        
        # Pattern 2: Look for "at Company Name" in description
        at_company_match = re.search(r'\bat\s+([A-Z][A-Za-z0-9\s&.,\'-]{2,40}?)(?:\s+(?:in|is|located|based|seeks))', description)
        if at_company_match:
            return at_company_match.group(1).strip()
        
        # Pattern 3: "Company Name is seeking/hiring"
        seeking_match = re.search(r'^([A-Z][A-Za-z0-9\s&.,\'-]{2,40}?)\s+(?:is|are)\s+(?:seeking|hiring|looking)', description)
        if seeking_match:
            return seeking_match.group(1).strip()
        
        # Pattern 4: Use AI extraction as last resort
        try:
            prompt = f"""Extract the company name from this job posting. Return ONLY the company name, nothing else.
If no company name is found, return "Unknown".

Job Title: {title}

Job Description (first 500 chars):
{description[:500]}

Company Name:"""
            
            response = self.client.client.chat.completions.create(
                model=self.client.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=50
            )
            
            company_name = response.choices[0].message.content.strip()
            if company_name and company_name != "Unknown" and len(company_name) > 2:
                return company_name
                
        except Exception as e:
            logger.debug(f"AI company extraction failed: {e}")
        
        return "Unknown"

    def batch_parse_with_progress(
        self,
        raw_jobs: List[RawJobPosting],
        use_ai: bool = True,
        batch_size: int = 10
    ) -> List[ParsedJobPosting]:
        """
        Parse jobs in batches with progress reporting.

        Args:
            raw_jobs: List of raw jobs
            use_ai: Whether to use AI
            batch_size: Number of jobs per batch

        Returns:
            List of parsed jobs
        """
        logger.info(
            f"Starting batch parsing of {len(raw_jobs)} jobs "
            f"(batch size: {batch_size})"
        )

        parsed_jobs = []
        total = len(raw_jobs)

        for i in range(0, total, batch_size):
            batch = raw_jobs[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total + batch_size - 1) // batch_size

            logger.info(
                f"Processing batch {batch_num}/{total_batches} "
                f"({len(batch)} jobs)"
            )

            batch_results = self.parse_jobs(batch, use_ai=use_ai)
            parsed_jobs.extend(batch_results)

            logger.info(
                f"Batch {batch_num} complete. "
                f"Total parsed: {len(parsed_jobs)}/{total}"
            )

        return parsed_jobs
