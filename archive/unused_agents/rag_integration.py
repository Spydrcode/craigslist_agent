"""
RAG Integration Layer
Connects the new lead qualification agents with existing VectorAgent and DatabaseAgent.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from .client_agent import ClientAgent
from .vector_agent import VectorAgent
from .database_agent import DatabaseAgent
from .researcher import ResearcherAgent
from utils import get_logger

logger = get_logger(__name__)


class RAGIntegration:
    """
    Integrates RAG capabilities into the lead qualification system.
    Provides semantic search, historical context, and ML-ready data storage.
    """

    def __init__(
        self,
        use_vector_db: bool = True,
        use_relational_db: bool = True
    ):
        """
        Initialize RAG integration.

        Args:
            use_vector_db: Enable Pinecone vector storage
            use_relational_db: Enable Supabase relational storage
        """
        self.client_agent = ClientAgent()

        self.vector_agent = None
        if use_vector_db:
            try:
                self.vector_agent = VectorAgent(client_agent=self.client_agent)
                logger.info("VectorAgent initialized for RAG")
            except Exception as e:
                logger.warning(f"VectorAgent initialization failed: {e}")

        self.db_agent = None
        if use_relational_db:
            try:
                self.db_agent = DatabaseAgent()
                logger.info("DatabaseAgent initialized for RAG")
            except Exception as e:
                logger.warning(f"DatabaseAgent initialization failed: {e}")

    def enhance_research_with_rag(
        self,
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance ResearcherAgent output with RAG-powered insights.

        Finds similar companies we've processed before and retrieves
        their characteristics to improve company profiling.

        Args:
            extracted_data: Output from ExtractorAgent

        Returns:
            Enhanced data with RAG insights
        """
        if not self.vector_agent:
            return extracted_data

        company_name = extracted_data.get('company_name')
        if not company_name:
            return extracted_data

        try:
            # Search for similar companies in vector DB
            query_text = f"{company_name} {extracted_data.get('job_title', '')} {extracted_data.get('location', '')}"

            from models import SearchQuery
            search_query = SearchQuery(
                query_text=query_text,
                top_k=5,
                min_score=0.7
            )

            similar_jobs = self.vector_agent.search_similar_jobs(search_query)

            if similar_jobs:
                # Extract insights from similar jobs
                similar_companies = [
                    match['metadata'].get('title', '') for match in similar_jobs
                ]

                # Average employee count from similar companies
                avg_size = self._estimate_company_size_from_similar(similar_jobs)

                # Most common industry
                common_industry = self._identify_common_industry(similar_jobs)

                logger.info(
                    f"Found {len(similar_jobs)} similar companies for RAG enhancement"
                )

                return {
                    **extracted_data,
                    'rag_similar_companies': similar_companies,
                    'rag_estimated_size': avg_size,
                    'rag_suggested_industry': common_industry,
                    'rag_confidence': similar_jobs[0]['score'] if similar_jobs else 0.0
                }

            return extracted_data

        except Exception as e:
            logger.error(f"RAG enhancement failed: {e}")
            return extracted_data

    def _estimate_company_size_from_similar(
        self,
        similar_jobs: List[Dict[str, Any]]
    ) -> Optional[int]:
        """Estimate company size from similar jobs."""
        sizes = []
        for job in similar_jobs:
            # This would require salary data or other indicators
            # For now, return None - implement logic based on your metadata
            pass
        return None

    def _identify_common_industry(
        self,
        similar_jobs: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Identify most common industry from similar jobs."""
        industries = {}
        for job in similar_jobs:
            industry = job.get('metadata', {}).get('category')
            if industry:
                industries[industry] = industries.get(industry, 0) + 1

        if industries:
            return max(industries, key=industries.get)
        return None

    def store_lead_in_vector_db(self, lead_data: Dict[str, Any]) -> bool:
        """
        Store processed lead in vector database for future RAG queries.

        Args:
            lead_data: Fully processed lead from orchestrator

        Returns:
            True if successful
        """
        if not self.vector_agent:
            return False

        try:
            # Create embedding text from lead
            embedding_text = self._create_lead_embedding_text(lead_data)

            # Generate embedding
            embeddings = self.client_agent.get_embeddings([embedding_text])

            # Prepare metadata
            metadata = {
                'lead_id': lead_data.get('lead_id'),
                'company_name': lead_data.get('company_name', ''),
                'location': lead_data.get('location', ''),
                'industry': lead_data.get('company_industry', ''),
                'tier': lead_data.get('tier'),
                'score': lead_data.get('score'),
                'is_local': lead_data.get('is_local', False),
                'pain_points': lead_data.get('pain_points', [])[:5],  # Limit size
                'url': lead_data.get('posting_url', ''),
                'processed_at': datetime.utcnow().isoformat()
            }

            # Upsert to Pinecone
            from models import JobEmbedding
            lead_embedding = JobEmbedding(
                job_id=lead_data.get('lead_id'),
                url=lead_data.get('posting_url', ''),
                title=lead_data.get('company_name', 'Unknown'),
                description_embedding=embeddings[0],
                metadata=metadata
            )

            success = self.vector_agent.upsert_job(lead_embedding)

            if success:
                logger.info(f"Stored lead in vector DB: {lead_data.get('company_name')}")

            return success

        except Exception as e:
            logger.error(f"Failed to store lead in vector DB: {e}")
            return False

    def _create_lead_embedding_text(self, lead_data: Dict[str, Any]) -> str:
        """Create text representation for embedding."""
        parts = []

        if lead_data.get('company_name'):
            parts.append(f"Company: {lead_data['company_name']}")

        if lead_data.get('job_title'):
            parts.append(f"Position: {lead_data['job_title']}")

        if lead_data.get('company_industry'):
            parts.append(f"Industry: {lead_data['company_industry']}")

        if lead_data.get('value_proposition'):
            parts.append(f"Value: {lead_data['value_proposition']}")

        pain_points = lead_data.get('pain_points', [])
        if pain_points:
            pain_text = ', '.join([p.get('description', '') for p in pain_points])
            parts.append(f"Pain Points: {pain_text}")

        return ' | '.join(parts)

    def store_lead_in_relational_db(self, lead_data: Dict[str, Any]) -> bool:
        """
        Store processed lead in Supabase for structured queries.

        Args:
            lead_data: Fully processed lead from orchestrator

        Returns:
            True if successful
        """
        if not self.db_agent:
            return False

        try:
            # Transform lead data to match your database schema
            # You'll need to create a new table in Supabase for leads
            # or adapt the existing jobs table

            lead_record = {
                'lead_id': lead_data.get('lead_id'),
                'company_name': lead_data.get('company_name'),
                'job_title': lead_data.get('job_title'),
                'location': lead_data.get('location'),
                'industry': lead_data.get('company_industry'),
                'tier': lead_data.get('tier'),
                'score': lead_data.get('score'),
                'is_local': lead_data.get('is_local'),
                'posting_url': lead_data.get('posting_url'),
                'value_proposition': lead_data.get('value_proposition'),
                'status': lead_data.get('status', 'new'),
                'processed_at': datetime.utcnow().isoformat()
            }

            # Insert into database
            # Note: You'll need to create this table in Supabase first
            result = self.db_agent.client.table('qualified_leads').upsert(
                lead_record,
                on_conflict='lead_id'
            ).execute()

            logger.info(f"Stored lead in database: {lead_data.get('company_name')}")
            return True

        except Exception as e:
            logger.error(f"Failed to store lead in database: {e}")
            return False

    def find_similar_leads(
        self,
        lead_data: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar leads we've processed before.

        Useful for:
        - Identifying patterns in successful conversions
        - Finding similar companies for market research
        - Training ML models on similar lead characteristics

        Args:
            lead_data: Current lead to find matches for
            top_k: Number of similar leads to return

        Returns:
            List of similar leads with scores
        """
        if not self.vector_agent:
            return []

        try:
            embedding_text = self._create_lead_embedding_text(lead_data)

            from models import SearchQuery
            search_query = SearchQuery(
                query_text=embedding_text,
                top_k=top_k,
                min_score=0.6
            )

            similar = self.vector_agent.search_similar_jobs(search_query)

            logger.info(f"Found {len(similar)} similar leads")
            return similar

        except Exception as e:
            logger.error(f"Failed to find similar leads: {e}")
            return []

    def get_conversion_insights(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get insights about conversion probability based on historical data.

        Queries database for similar leads that converted to see patterns.

        Args:
            lead_data: Current lead

        Returns:
            Insights dictionary
        """
        if not self.db_agent:
            return {}

        try:
            # Find similar leads that closed won
            # This requires the database to have conversion tracking

            insights = {
                'similar_conversions': 0,
                'avg_conversion_time_days': None,
                'common_objections': [],
                'recommended_approach': None
            }

            # Query for similar tier/industry leads
            tier = lead_data.get('tier')
            industry = lead_data.get('company_industry')

            if tier and industry:
                # This is a placeholder - implement actual query
                result = self.db_agent.client.table('qualified_leads').select('*').eq(
                    'tier', tier
                ).eq(
                    'industry', industry
                ).eq(
                    'status', 'closed_won'
                ).execute()

                if result.data:
                    insights['similar_conversions'] = len(result.data)

            return insights

        except Exception as e:
            logger.error(f"Failed to get conversion insights: {e}")
            return {}

    def enable_semantic_search(self) -> bool:
        """
        Check if semantic search is available.

        Returns:
            True if vector DB is configured
        """
        return self.vector_agent is not None

    def enable_structured_queries(self) -> bool:
        """
        Check if structured queries are available.

        Returns:
            True if relational DB is configured
        """
        return self.db_agent is not None
