"""
Client Agent for AI/LLM interactions.
Wraps OpenAI GPT API for reasoning tasks like parsing, analysis, and scoring.
"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import tiktoken

from config import Config
from utils import get_logger
from models import JobAnalysis

logger = get_logger(__name__)


class ClientAgent:
    """Agent for interacting with OpenAI GPT API with conversation state management."""

    def __init__(self, model: Optional[str] = None, conversation_id: Optional[str] = None):
        """
        Initialize the Client Agent.

        Args:
            model: OpenAI model to use (defaults to Config.OPENAI_MODEL)
            conversation_id: Optional conversation ID for persistent state
        """
        self.model = model or Config.OPENAI_MODEL
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Conversation state management
        self.conversation_id = conversation_id
        self.previous_response_id: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.total_tokens_used = 0

        logger.info(f"ClientAgent initialized with model: {self.model}")
        if conversation_id:
            logger.info(f"Using conversation: {conversation_id}")

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text."""
        return len(self.encoding.encode(text))
    
    def create_conversation(self) -> str:
        """
        Create a new conversation for persistent state management.
        
        Returns:
            Conversation ID
        """
        try:
            conversation = self.client.conversations.create()
            self.conversation_id = conversation.id
            logger.info(f"Created new conversation: {self.conversation_id}")
            return self.conversation_id
        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history and reset state."""
        self.conversation_history = []
        self.previous_response_id = None
        self.total_tokens_used = 0
        logger.info("Conversation history cleared")
    
    def estimate_context_usage(self, messages: List[Dict[str, str]], max_context: int = 128000) -> Dict[str, Any]:
        """
        Estimate context window usage for a set of messages.
        
        Args:
            messages: List of message dictionaries
            max_context: Maximum context window for model (default: 128k for GPT-4)
        
        Returns:
            Dictionary with usage statistics
        """
        total_tokens = sum(self.count_tokens(msg.get('content', '')) for msg in messages)
        usage_percent = (total_tokens / max_context) * 100
        tokens_remaining = max_context - total_tokens
        
        return {
            'total_tokens': total_tokens,
            'max_context': max_context,
            'usage_percent': round(usage_percent, 2),
            'tokens_remaining': tokens_remaining,
            'at_risk': usage_percent > 80,  # Warning if using >80% of context
            'recommendation': 'Consider summarizing or truncating history' if usage_percent > 80 else 'Context usage healthy'
        }
    
    def truncate_conversation_history(self, keep_recent: int = 10) -> List[Dict[str, str]]:
        """
        Truncate conversation history to prevent context window overflow.
        Keeps system message and most recent N messages.
        
        Args:
            keep_recent: Number of recent messages to keep
        
        Returns:
            Truncated conversation history
        """
        if len(self.conversation_history) <= keep_recent + 1:
            return self.conversation_history
        
        # Keep system message (if exists) and recent messages
        system_messages = [msg for msg in self.conversation_history if msg.get('role') == 'system']
        recent_messages = self.conversation_history[-keep_recent:]
        
        truncated = system_messages + recent_messages
        logger.info(f"Truncated conversation history from {len(self.conversation_history)} to {len(truncated)} messages")
        
        return truncated

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        store: bool = False,
        use_conversation: bool = False,
        previous_response_id: Optional[str] = None
    ) -> str:
        """
        Make a call to the OpenAI API with retry logic and conversation state management.

        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            response_format: Optional response format specification
            tools: Optional list of tools (for function calling, web search, etc.)
            tool_choice: Optional tool choice strategy
            store: Store response for 30 days (default False for privacy)
            use_conversation: Use conversation_id for persistent state
            previous_response_id: Chain to previous response for context

        Returns:
            API response content
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if response_format:
                kwargs["response_format"] = response_format
                
            if tools:
                kwargs["tools"] = tools
                
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
            
            # Conversation state management
            if store:
                kwargs["store"] = True
            
            if use_conversation and self.conversation_id:
                kwargs["conversation"] = self.conversation_id
            
            if previous_response_id or self.previous_response_id:
                kwargs["previous_response_id"] = previous_response_id or self.previous_response_id

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            
            # Track response ID for chaining
            if hasattr(response, 'id'):
                self.previous_response_id = response.id
            
            # Update conversation history
            self.conversation_history.extend(messages)
            if content:
                self.conversation_history.append({"role": "assistant", "content": content})
            
            # Track token usage
            if hasattr(response, 'usage'):
                tokens_used = response.usage.total_tokens
                self.total_tokens_used += tokens_used
                logger.debug(f"API call successful. Tokens used: {tokens_used} (Total: {self.total_tokens_used})")

            return content

        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    def extract_pain_points(self, job_description: str) -> List[str]:
        """
        Extract pain points and problems the company is trying to solve.

        Args:
            job_description: Full job description text

        Returns:
            List of identified pain points
        """
        logger.info("Extracting pain points from job description")

        prompt = f"""
        Analyze the following job description and identify the key pain points,
        problems, or challenges the company is trying to solve by hiring for this role.

        Focus on:
        - Business problems mentioned
        - Technical challenges
        - Growth or scaling issues
        - Team gaps or needs

        Job Description:
        {job_description}

        Return ONLY a JSON array of pain points as strings. Example:
        ["Need to scale infrastructure", "Legacy codebase modernization"]
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing job descriptions and identifying business pain points."
            },
            {"role": "user", "content": prompt}
        ]

        try:
            response = self._call_api(
                messages,
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            # Parse JSON response
            data = json.loads(response)

            # Handle different possible JSON structures
            if isinstance(data, list):
                pain_points = data
            elif "pain_points" in data:
                pain_points = data["pain_points"]
            elif "painPoints" in data:
                pain_points = data["painPoints"]
            else:
                # Try to extract from first key
                pain_points = list(data.values())[0] if data else []

            logger.info(f"Extracted {len(pain_points)} pain points")
            return pain_points

        except Exception as e:
            logger.error(f"Failed to extract pain points: {e}")
            return []

    def extract_skills(
        self,
        job_description: str
    ) -> Dict[str, List[str]]:
        """
        Extract required and nice-to-have skills from job description.

        Args:
            job_description: Full job description text

        Returns:
            Dictionary with 'required' and 'nice_to_have' skill lists
        """
        logger.info("Extracting skills from job description")

        prompt = f"""
        Analyze this job description and extract skills into two categories:
        1. Required skills (must-haves, requirements)
        2. Nice-to-have skills (preferred, bonus, nice-to-haves)

        Job Description:
        {job_description}

        Return a JSON object with this structure:
        {{
            "required": ["skill1", "skill2"],
            "nice_to_have": ["skill3", "skill4"]
        }}
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert at parsing job requirements and extracting skills."
            },
            {"role": "user", "content": prompt}
        ]

        try:
            response = self._call_api(
                messages,
                temperature=0.2,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            skills = json.loads(response)

            # Ensure expected keys exist
            if "required" not in skills:
                skills["required"] = []
            if "nice_to_have" not in skills:
                skills["nice_to_have"] = []

            logger.info(
                f"Extracted {len(skills['required'])} required skills, "
                f"{len(skills['nice_to_have'])} nice-to-have skills"
            )

            return skills

        except Exception as e:
            logger.error(f"Failed to extract skills: {e}")
            return {"required": [], "nice_to_have": []}

    def analyze_work_arrangement(self, job_description: str) -> str:
        """
        Determine work arrangement (remote, hybrid, onsite).

        Args:
            job_description: Full job description text

        Returns:
            Work arrangement: "remote", "hybrid", or "onsite"
        """
        logger.info("Analyzing work arrangement")

        prompt = f"""
        Based on this job description, determine the work arrangement.

        Job Description:
        {job_description}

        Respond with ONLY one word: "remote", "hybrid", or "onsite"
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing job requirements."
            },
            {"role": "user", "content": prompt}
        ]

        try:
            response = self._call_api(
                messages,
                temperature=0.1,
                max_tokens=10
            )

            arrangement = response.strip().lower()

            if arrangement not in ["remote", "hybrid", "onsite"]:
                arrangement = "onsite"  # Default

            logger.info(f"Work arrangement: {arrangement}")
            return arrangement

        except Exception as e:
            logger.error(f"Failed to analyze work arrangement: {e}")
            return "onsite"

    def score_relevance(
        self,
        job_description: str,
        criteria: Dict[str, Any]
    ) -> float:
        """
        Score job relevance based on custom criteria.

        Args:
            job_description: Full job description text
            criteria: Dictionary of criteria (e.g., required_skills, preferred_location)

        Returns:
            Relevance score (0.0 to 1.0)
        """
        logger.info("Scoring job relevance")

        criteria_text = "\n".join([f"- {k}: {v}" for k, v in criteria.items()])

        prompt = f"""
        Score this job posting's relevance based on the following criteria.
        Return a score from 0.0 to 1.0, where 1.0 is a perfect match.

        Criteria:
        {criteria_text}

        Job Description:
        {job_description}

        Return ONLY a JSON object with a "score" field (float between 0.0 and 1.0).
        Example: {{"score": 0.85}}
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert at evaluating job match quality."
            },
            {"role": "user", "content": prompt}
        ]

        try:
            response = self._call_api(
                messages,
                temperature=0.2,
                max_tokens=50,
                response_format={"type": "json_object"}
            )

            data = json.loads(response)
            score = float(data.get("score", 0.5))

            # Ensure score is in valid range
            score = max(0.0, min(1.0, score))

            logger.info(f"Relevance score: {score:.2f}")
            return score

        except Exception as e:
            logger.error(f"Failed to score relevance: {e}")
            return 0.5  # Default mid-range score

    def generate_summary(self, job_description: str, max_length: int = 200) -> str:
        """
        Generate a concise summary of the job posting.

        Args:
            job_description: Full job description text
            max_length: Maximum length of summary in characters

        Returns:
            Summary text
        """
        logger.info("Generating job summary")

        prompt = f"""
        Create a concise summary of this job posting in {max_length} characters or less.
        Focus on the role, key responsibilities, and main requirements.

        Job Description:
        {job_description}
        """

        messages = [
            {
                "role": "system",
                "content": "You are an expert at summarizing job descriptions."
            },
            {"role": "user", "content": prompt}
        ]

        try:
            response = self._call_api(
                messages,
                temperature=0.3,
                max_tokens=100
            )

            summary = response.strip()
            logger.info("Summary generated successfully")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return job_description[:max_length] + "..."

    def analyze_job_posting(
        self,
        job_url: str,
        job_description: str,
        criteria: Optional[Dict[str, Any]] = None
    ) -> JobAnalysis:
        """
        Perform comprehensive analysis of a job posting.

        Args:
            job_url: URL of the job posting
            job_description: Full job description text
            criteria: Optional criteria for relevance scoring

        Returns:
            JobAnalysis object with all extracted information
        """
        logger.info(f"Performing comprehensive analysis for job: {job_url}")

        # Extract all information
        pain_points = self.extract_pain_points(job_description)
        skills = self.extract_skills(job_description)
        work_arrangement = self.analyze_work_arrangement(job_description)
        summary = self.generate_summary(job_description)

        # Calculate relevance score if criteria provided
        relevance_score = 0.5
        if criteria:
            relevance_score = self.score_relevance(job_description, criteria)

        analysis = JobAnalysis(
            job_url=job_url,
            pain_points=pain_points,
            required_skills=skills.get("required", []),
            nice_to_have_skills=skills.get("nice_to_have", []),
            work_arrangement=work_arrangement,
            relevance_score=relevance_score,
            summary=summary
        )

        logger.info("Job analysis completed successfully")
        return analysis
    
    def research_company_web(self, company_name: str, context: str = "") -> Dict[str, Any]:
        """
        Research a company using web search to gather additional intelligence.
        
        Args:
            company_name: Name of the company to research
            context: Additional context (e.g., job posting, location)
            
        Returns:
            Dictionary with company research findings
        """
        logger.info(f"Researching company via web search: {company_name}")
        
        # Enable web search tool
        tools = [{"type": "web_search"}]
        
        messages = [
            {
                "role": "system",
                "content": """You are a B2B sales researcher. Research companies to determine if they need workforce analytics and forecasting software.
                
Focus on finding:
1. Company size (number of employees)
2. Revenue and growth trajectory
3. Hiring patterns and job postings volume
4. Industry and business model
5. Locations and expansion signals
6. Technology stack and HR systems used
7. Decision makers (HR, Ops, Finance leaders)
8. Recent news about hiring, layoffs, or workforce challenges"""
            },
            {
                "role": "user",
                "content": f"""Research this company: {company_name}

Context: {context}

Provide a structured report with:
- Company overview (size, industry, revenue)
- Hiring signals (are they actively hiring? How many positions?)
- Growth indicators (expanding, stable, or contracting?)
- Workforce challenges (any mentioned pain points?)
- Decision maker names and titles (if available)
- Likelihood they need workforce forecasting (0-10 score with reasoning)"""
            }
        ]
        
        try:
            response_text = self._call_api(
                messages=messages,
                temperature=0.3,
                max_tokens=1500,
                tools=tools,
                tool_choice="auto"  # Let model decide when to search
            )
            
            # Parse the response into structured data
            result = {
                "company_name": company_name,
                "research_summary": response_text,
                "researched_at": "now",
                "source": "web_search"
            }
            
            logger.info(f"Web research completed for {company_name}")
            return result
            
        except Exception as e:
            logger.error(f"Web research failed for {company_name}: {e}")
            return {
                "company_name": company_name,
                "error": str(e),
                "researched_at": "now"
            }
    
    def extract_company_info_structured(self, job_description: str, job_title: str = "") -> Dict[str, Any]:
        """
        Extract company information using structured function calling.
        
        Args:
            job_description: Full job posting text
            job_title: Job title for context
            
        Returns:
            Structured company information
        """
        logger.info("Extracting company info via function calling")
        
        # Define the function schema
        tools = [{
            "type": "function",
            "function": {
                "name": "extract_company_data",
                "description": "Extract structured company information from a job posting",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Name of the hiring company"
                        },
                        "company_size": {
                            "type": "string",
                            "enum": ["1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5000+", "unknown"],
                            "description": "Estimated company size"
                        },
                        "industry": {
                            "type": "string",
                            "description": "Primary industry or sector"
                        },
                        "hiring_volume_signals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Signals indicating high-volume hiring (e.g., 'multiple positions', 'hiring event')"
                        },
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Workforce challenges or pain points mentioned"
                        },
                        "growth_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Signs of company growth (expansion, new locations, etc.)"
                        },
                        "forecasta_fit_score": {
                            "type": "integer",
                            "description": "Score 0-10 indicating likelihood company needs workforce forecasting software",
                            "minimum": 0,
                            "maximum": 10
                        },
                        "forecasta_fit_reasoning": {
                            "type": "string",
                            "description": "Brief explanation of the fit score"
                        }
                    },
                    "required": ["company_name", "industry", "forecasta_fit_score", "forecasta_fit_reasoning"]
                }
            }
        }]
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing job postings to identify companies that need workforce analytics and forecasting software."
            },
            {
                "role": "user",
                "content": f"""Analyze this job posting and extract company information:

Job Title: {job_title}

Job Description:
{job_description[:3000]}

Extract all relevant company details and assess if they're a good fit for workforce forecasting software (Forecasta)."""
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "extract_company_data"}},
                temperature=0.3
            )
            
            # Parse function call result
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            logger.info(f"Extracted company: {function_args.get('company_name', 'Unknown')}, Fit score: {function_args.get('forecasta_fit_score', 0)}/10")
            return function_args
            
        except Exception as e:
            logger.error(f"Structured extraction failed: {e}")
            return {
                "company_name": "Unknown",
                "industry": "Unknown",
                "forecasta_fit_score": 0,
                "forecasta_fit_reasoning": f"Extraction failed: {str(e)}"
            }
    
    def generate_image(self, prompt: str, size: str = "1024x1024", quality: str = "standard") -> Dict[str, Any]:
        """
        Generate an image using DALL-E.
        
        Args:
            prompt: Description of the image to generate
            size: Image size ("1024x1024", "1792x1024", "1024x1792")
            quality: Image quality ("standard" or "hd")
            
        Returns:
            Dictionary with image URL and metadata
        """
        logger.info(f"Generating image: {prompt[:50]}...")
        
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1
            )
            
            image_url = response.data[0].url
            revised_prompt = response.data[0].revised_prompt
            
            logger.info(f"Image generated successfully")
            return {
                "url": image_url,
                "revised_prompt": revised_prompt,
                "original_prompt": prompt,
                "size": size,
                "quality": quality
            }
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "error": str(e),
                "original_prompt": prompt
            }
    
    def generate_hiring_trend_visualization(self, company_name: str, job_count: int, time_period: str = "month") -> Dict[str, Any]:
        """
        Generate a visual representation of hiring trends.
        
        Args:
            company_name: Name of the company
            job_count: Number of jobs posted
            time_period: Time period ("week", "month", "quarter")
            
        Returns:
            Dictionary with image URL
        """
        logger.info(f"Generating hiring trend visualization for {company_name}")
        
        prompt = f"""Create a professional business chart showing hiring trends for {company_name}.
        
The chart should show:
- Company name: {company_name}
- {job_count} job postings in the last {time_period}
- Upward trending line graph
- Clean, modern design with blue and green colors
- Professional business style suitable for a sales presentation
- Include axis labels and data points"""
        
        return self.generate_image(prompt, size="1792x1024", quality="hd")
    
    def generate_company_logo_concept(self, company_name: str, industry: str) -> Dict[str, Any]:
        """
        Generate a conceptual logo for a company (useful for presentations when actual logo unavailable).
        
        Args:
            company_name: Name of the company
            industry: Company's industry
            
        Returns:
            Dictionary with image URL
        """
        logger.info(f"Generating logo concept for {company_name}")
        
        prompt = f"""Create a simple, professional logo concept for {company_name}, a company in the {industry} industry.

Style requirements:
- Minimalist and modern
- Clean lines
- Professional color scheme
- Suitable for business presentations
- No text, just the symbol/icon
- White or light background"""
        
        return self.generate_image(prompt, size="1024x1024", quality="standard")
    
    def analyze_hiring_data_with_code(self, job_postings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Use Code Interpreter to analyze hiring data and generate insights.
        
        Args:
            job_postings: List of job posting dictionaries with dates, titles, locations, etc.
            
        Returns:
            Dictionary with analysis results and insights
        """
        logger.info(f"Analyzing {len(job_postings)} job postings with Code Interpreter")
        
        # Prepare data summary for analysis
        data_summary = {
            "total_jobs": len(job_postings),
            "by_location": {},
            "by_date": {},
            "titles": []
        }
        
        for job in job_postings:
            # Count by location
            loc = job.get('location', 'Unknown')
            data_summary["by_location"][loc] = data_summary["by_location"].get(loc, 0) + 1
            
            # Count by date
            date = job.get('posted_date', job.get('date', 'Unknown'))
            if date and date != 'Unknown':
                data_summary["by_date"][date] = data_summary["by_date"].get(date, 0) + 1
            
            # Collect titles
            data_summary["titles"].append(job.get('title', ''))
        
        # Use Code Interpreter tool to analyze
        tools = [{"type": "code_interpreter"}]
        
        messages = [
            {
                "role": "system",
                "content": """You are a data analyst specializing in workforce analytics. 
                Analyze job posting data to identify hiring patterns, trends, and insights.
                Use Python code to calculate statistics and generate insights."""
            },
            {
                "role": "user",
                "content": f"""Analyze this hiring data and provide insights:

Total Jobs: {data_summary['total_jobs']}

Jobs by Location:
{', '.join([f'{loc}: {count}' for loc, count in sorted(data_summary['by_location'].items(), key=lambda x: x[1], reverse=True)[:10]])}

Job Titles (sample):
{', '.join(data_summary['titles'][:20])}

Please provide:
1. Hiring velocity (jobs per day/week)
2. Geographic distribution analysis
3. Most common job titles/roles
4. Growth signals (is hiring accelerating?)
5. Workforce analytics needs assessment (0-10 score)
6. Recommended Forecasta solutions based on patterns

Use code to calculate precise statistics."""
            }
        ]
        
        try:
            response_text = self._call_api(
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                tools=tools,
                tool_choice="auto"
            )
            
            logger.info("Code Interpreter analysis completed")
            return {
                "analysis": response_text,
                "data_summary": data_summary,
                "analyzed_jobs": len(job_postings)
            }
            
        except Exception as e:
            logger.error(f"Code Interpreter analysis failed: {e}")
            return {
                "error": str(e),
                "data_summary": data_summary
            }
    
    def calculate_forecasta_roi(self, company_size: int, avg_salary: float, turnover_rate: float = 0.25) -> Dict[str, Any]:
        """
        Calculate ROI for Forecasta using Code Interpreter.
        
        Args:
            company_size: Number of employees
            avg_salary: Average salary per employee
            turnover_rate: Annual turnover rate (default 25%)
            
        Returns:
            Dictionary with ROI calculations and projections
        """
        logger.info(f"Calculating Forecasta ROI for company with {company_size} employees")
        
        tools = [{"type": "code_interpreter"}]
        
        messages = [
            {
                "role": "system",
                "content": "You are a financial analyst calculating ROI for workforce analytics software."
            },
            {
                "role": "user",
                "content": f"""Calculate the ROI for Forecasta workforce analytics software:

Company Metrics:
- Employees: {company_size}
- Average Salary: ${avg_salary:,.2f}
- Current Turnover Rate: {turnover_rate * 100}%

Forecasta Benefits:
- Reduces turnover by 15-20% through predictive insights
- Improves hiring efficiency (30% faster time-to-hire)
- Optimizes staffing levels (5-10% labor cost savings)
- Prevents overstaffing/understaffing costs

Forecasta Pricing:
- Base: $500/month
- Per Employee: $2-5/employee/month (depending on company size)

Using Python, calculate:
1. Total annual cost of Forecasta
2. Annual savings from reduced turnover
3. Annual savings from optimized staffing
4. Net ROI (percentage and dollar amount)
5. Payback period (months)
6. 3-year projected value

Provide detailed calculations with code."""
            }
        ]
        
        try:
            response_text = self._call_api(
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                tools=tools,
                tool_choice="auto"
            )
            
            logger.info("ROI calculation completed")
            return {
                "roi_analysis": response_text,
                "inputs": {
                    "company_size": company_size,
                    "avg_salary": avg_salary,
                    "turnover_rate": turnover_rate
                }
            }
            
        except Exception as e:
            logger.error(f"ROI calculation failed: {e}")
            return {
                "error": str(e)
            }

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI's embedding model.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")

        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )

            embeddings = [item.embedding for item in response.data]

            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
