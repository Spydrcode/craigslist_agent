"""Enhanced Orchestrator with RAG Integration."""

import logging
from typing import Dict, Any, List, Optional

from .orchestrator import Orchestrator
from .rag_integration import RAGIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestratorRAG(Orchestrator):
    """
    Enhanced orchestrator with RAG capabilities.

    Extends the base Orchestrator to include:
    - Vector database storage for semantic search
    - Relational database storage for structured queries
    - Historical context retrieval
    - ML-ready data pipeline
    """

    def __init__(
        self,
        web_search_tool=None,
        data_dir: str = "data/leads",
        enable_vector_db: bool = True,
        enable_relational_db: bool = True
    ):
        """
        Initialize RAG-enabled orchestrator.

        Args:
            web_search_tool: Optional web search function
            data_dir: Directory for file storage
            enable_vector_db: Enable Pinecone vector storage
            enable_relational_db: Enable Supabase relational storage
        """
        # Initialize base orchestrator
        super().__init__(web_search_tool=web_search_tool, data_dir=data_dir)

        # Initialize RAG integration
        self.rag = RAGIntegration(
            use_vector_db=enable_vector_db,
            use_relational_db=enable_relational_db
        )

        logger.info("OrchestratorRAG initialized with RAG capabilities")

    def process_posting(self, posting_html: str, posting_url: str) -> Dict[str, Any]:
        """
        Process a single job posting through the complete pipeline with RAG.

        Enhances base processing with:
        - RAG-powered company research
        - Similar lead retrieval
        - Vector and relational DB storage
        - Historical context

        Args:
            posting_html: Raw HTML of the posting
            posting_url: URL of the posting

        Returns:
            Fully processed lead data with RAG insights
        """
        logger.info(f"Processing posting with RAG: {posting_url}")

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

        # Step 2: Research (enhanced with RAG)
        if self.rag.enable_semantic_search():
            # Find similar companies before researching
            data = self.rag.enhance_research_with_rag(data)
            logger.info("Enhanced research with RAG insights")

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

            # Get conversion insights from similar leads
            if self.rag.enable_structured_queries():
                conversion_insights = self.rag.get_conversion_insights(data)
                data['conversion_insights'] = conversion_insights
                logger.info("Added conversion insights from historical data")

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

        # Step 6: Store (file system)
        data = self._run_with_retry(
            self.storer.store,
            data,
            step_name="storage"
        )

        # Step 7: Store in RAG databases
        if self.rag.enable_semantic_search():
            vector_success = self.rag.store_lead_in_vector_db(data)
            data['vector_db_stored'] = vector_success

        if self.rag.enable_structured_queries():
            db_success = self.rag.store_lead_in_relational_db(data)
            data['relational_db_stored'] = db_success

        logger.info(
            f"Processing complete with RAG. "
            f"Lead ID: {data.get('lead_id')}, "
            f"Tier: {tier}, "
            f"Score: {data.get('score')}"
        )

        return data

    def find_similar_leads(
        self,
        lead_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find leads similar to a given lead using semantic search.

        Args:
            lead_id: ID of the reference lead
            top_k: Number of similar leads to return

        Returns:
            List of similar leads with scores
        """
        if not self.rag.enable_semantic_search():
            logger.warning("Semantic search not enabled")
            return []

        lead = self.get_lead(lead_id)
        if not lead:
            logger.warning(f"Lead {lead_id} not found")
            return []

        return self.rag.find_similar_leads(lead, top_k=top_k)

    def semantic_search_leads(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search leads using natural language query.

        Examples:
        - "restaurant companies in Phoenix struggling with seasonal staffing"
        - "retail businesses with high forecasting pain scores"

        Args:
            query: Natural language search query
            filters: Optional metadata filters (tier, location, etc.)
            top_k: Number of results to return

        Returns:
            List of matching leads
        """
        if not self.rag.enable_semantic_search():
            logger.warning("Semantic search not enabled")
            return []

        from models import SearchQuery
        search_query = SearchQuery(
            query_text=query,
            top_k=top_k,
            filter_metadata=filters,
            min_score=0.6
        )

        results = self.rag.vector_agent.search_similar_jobs(search_query)

        logger.info(f"Semantic search for '{query}' returned {len(results)} results")
        return results

    def get_ml_training_data(
        self,
        include_features: List[str] = None,
        min_tier: int = 1,
        max_tier: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get processed leads in ML-ready format for model training.

        Useful for:
        - Training scoring models
        - Predicting conversion probability
        - Optimizing value propositions

        Args:
            include_features: List of features to include
            min_tier: Minimum tier to include
            max_tier: Maximum tier to include

        Returns:
            List of leads with selected features
        """
        all_leads = self.get_all_leads()

        # Filter by tier
        filtered = [
            lead for lead in all_leads
            if min_tier <= lead.get('tier', 5) <= max_tier
        ]

        # Extract features
        if include_features:
            training_data = []
            for lead in filtered:
                features = {
                    feat: lead.get(feat) for feat in include_features
                }
                features['lead_id'] = lead.get('lead_id')
                training_data.append(features)

            return training_data

        return filtered

    def get_rag_status(self) -> Dict[str, Any]:
        """
        Get RAG system status and capabilities.

        Returns:
            Status dictionary
        """
        status = {
            'semantic_search_enabled': self.rag.enable_semantic_search(),
            'structured_queries_enabled': self.rag.enable_structured_queries(),
            'vector_db': 'available' if self.rag.vector_agent else 'not configured',
            'relational_db': 'available' if self.rag.db_agent else 'not configured'
        }

        # Get vector DB stats if available
        if self.rag.vector_agent:
            try:
                vector_stats = self.rag.vector_agent.get_index_stats()
                status['vector_db_stats'] = vector_stats
            except Exception as e:
                logger.error(f"Failed to get vector DB stats: {e}")

        # Get relational DB stats if available
        if self.rag.db_agent:
            try:
                db_stats = self.rag.db_agent.get_stats()
                status['relational_db_stats'] = db_stats
            except Exception as e:
                logger.error(f"Failed to get DB stats: {e}")

        return status
