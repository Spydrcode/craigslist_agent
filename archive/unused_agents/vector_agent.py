"""
Vector Agent for managing embeddings and semantic search.
Integrates with Pinecone for vector storage and similarity queries.
"""
from typing import List, Dict, Any, Optional, Tuple
import time
from pinecone import Pinecone, ServerlessSpec

from config import Config
from utils import get_logger, generate_job_id
from models import ParsedJobPosting, JobEmbedding, SearchQuery
from agents.client_agent import ClientAgent

logger = get_logger(__name__)


class VectorAgent:
    """Agent for vector embeddings and semantic search using Pinecone."""

    def __init__(
        self,
        client_agent: Optional[ClientAgent] = None,
        index_name: Optional[str] = None
    ):
        """
        Initialize the Vector Agent.

        Args:
            client_agent: ClientAgent for generating embeddings
            index_name: Pinecone index name (defaults to config)
        """
        self.client = client_agent or ClientAgent()
        self.index_name = index_name or Config.PINECONE_INDEX_NAME

        # Initialize Pinecone
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)

        # Get or create index
        self.index = self._initialize_index()

        logger.info(f"VectorAgent initialized with index: {self.index_name}")

    def _initialize_index(self):
        """
        Initialize Pinecone index, creating if it doesn't exist.

        Returns:
            Pinecone index instance
        """
        try:
            # Check if index exists
            existing_indexes = self.pc.list_indexes()

            if self.index_name not in [idx.name for idx in existing_indexes]:
                logger.info(f"Creating new Pinecone index: {self.index_name}")

                # Create index with serverless spec
                self.pc.create_index(
                    name=self.index_name,
                    dimension=Config.EMBEDDING_DIMENSION,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=Config.PINECONE_ENVIRONMENT
                    )
                )

                # Wait for index to be ready
                logger.info("Waiting for index to be ready...")
                time.sleep(5)

            # Connect to index
            index = self.pc.Index(self.index_name)

            logger.info(f"Connected to Pinecone index: {self.index_name}")
            return index

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone index: {e}")
            raise

    def embed_job(
        self,
        job: ParsedJobPosting,
        embed_pain_points: bool = True
    ) -> JobEmbedding:
        """
        Generate embeddings for a job posting.

        Args:
            job: Parsed job posting
            embed_pain_points: Whether to also embed pain points separately

        Returns:
            JobEmbedding object
        """
        logger.info(f"Generating embeddings for job: {job.title}")

        try:
            # Prepare text for embedding
            # Combine title and description for main embedding
            main_text = f"{job.title}\n\n{job.description}"

            # Generate embeddings
            texts_to_embed = [main_text]

            if embed_pain_points and job.pain_points:
                pain_points_text = "\n".join(job.pain_points)
                texts_to_embed.append(pain_points_text)

            embeddings = self.client.get_embeddings(texts_to_embed)

            # Create JobEmbedding with metadata (filter out None values for Pinecone)
            metadata = {
                'title': job.title,
                'location': job.location or '',
                'category': job.category or '',
                'is_remote': job.is_remote,
                'is_hybrid': job.is_hybrid,
                'skills': job.skills[:20] if job.skills else [],  # Limit for metadata size
                'pain_points': job.pain_points[:10] if job.pain_points else [],
                'url': job.url,
            }

            # Add optional fields only if they're not None
            if job.salary_min is not None:
                metadata['salary_min'] = job.salary_min
            if job.salary_max is not None:
                metadata['salary_max'] = job.salary_max
            if job.posted_date is not None:
                metadata['posted_date'] = job.posted_date
            if job.relevance_score is not None:
                metadata['relevance_score'] = job.relevance_score

            job_embedding = JobEmbedding(
                job_id=generate_job_id(job.url),
                url=job.url,
                title=job.title,
                description_embedding=embeddings[0],
                pain_points_embedding=embeddings[1] if len(embeddings) > 1 else None,
                metadata=metadata
            )

            logger.info(f"Generated embeddings for: {job.title}")
            return job_embedding

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def upsert_job(self, job_embedding: JobEmbedding) -> bool:
        """
        Upload job embedding to Pinecone.

        Args:
            job_embedding: Job embedding to upload

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Upserting job to Pinecone: {job_embedding.title}")

        try:
            # Prepare vector for upsert
            vector = {
                'id': job_embedding.job_id,
                'values': job_embedding.description_embedding,
                'metadata': job_embedding.metadata
            }

            # Upsert to index
            self.index.upsert(vectors=[vector])

            logger.info(f"Successfully upserted job: {job_embedding.title}")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert job: {e}")
            return False

    def upsert_jobs(
        self,
        jobs: List[ParsedJobPosting],
        batch_size: int = 100
    ) -> int:
        """
        Upload multiple job embeddings to Pinecone in batches.

        Args:
            jobs: List of parsed job postings
            batch_size: Number of vectors to upsert per batch

        Returns:
            Number of successfully uploaded jobs
        """
        logger.info(f"Upserting {len(jobs)} jobs to Pinecone")

        success_count = 0

        # Process in batches
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]

            try:
                # Generate embeddings for batch
                job_embeddings = []
                for job in batch:
                    try:
                        embedding = self.embed_job(job)
                        job_embeddings.append(embedding)
                    except Exception as e:
                        logger.error(f"Failed to embed job {job.url}: {e}")
                        continue

                # Prepare vectors
                vectors = [
                    {
                        'id': emb.job_id,
                        'values': emb.description_embedding,
                        'metadata': emb.metadata
                    }
                    for emb in job_embeddings
                ]

                # Upsert batch
                if vectors:
                    self.index.upsert(vectors=vectors)
                    success_count += len(vectors)

                    logger.info(
                        f"Upserted batch {i // batch_size + 1}: "
                        f"{len(vectors)} jobs"
                    )

            except Exception as e:
                logger.error(f"Failed to upsert batch: {e}")
                continue

        logger.info(
            f"Successfully upserted {success_count}/{len(jobs)} jobs"
        )

        return success_count

    def search_similar_jobs(
        self,
        query: SearchQuery
    ) -> List[Dict[str, Any]]:
        """
        Search for similar jobs using semantic search.

        Args:
            query: Search query with text and parameters

        Returns:
            List of matching jobs with scores
        """
        logger.info(f"Searching for jobs similar to: '{query.query_text}'")

        try:
            # Generate embedding for query
            query_embedding = self.client.get_embeddings([query.query_text])[0]

            # Build filter if provided
            filter_dict = query.filter_metadata or {}

            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=query.top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )

            # Format results
            matches = []
            for match in results.matches:
                if match.score >= query.min_score:
                    matches.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': match.metadata
                    })

            logger.info(f"Found {len(matches)} matching jobs")
            return matches

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def find_similar_to_job(
        self,
        job_id: str,
        top_k: int = 10,
        min_score: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find jobs similar to a specific job.

        Args:
            job_id: ID of the reference job
            top_k: Number of results to return
            min_score: Minimum similarity score

        Returns:
            List of similar jobs
        """
        logger.info(f"Finding jobs similar to: {job_id}")

        try:
            # Fetch the job vector
            fetch_result = self.index.fetch(ids=[job_id])

            if job_id not in fetch_result.vectors:
                logger.warning(f"Job {job_id} not found in index")
                return []

            job_vector = fetch_result.vectors[job_id].values

            # Search for similar jobs
            results = self.index.query(
                vector=job_vector,
                top_k=top_k + 1,  # +1 to exclude the query job itself
                include_metadata=True
            )

            # Filter results
            matches = []
            for match in results.matches:
                # Skip the query job itself
                if match.id == job_id:
                    continue

                if match.score >= min_score:
                    matches.append({
                        'id': match.id,
                        'score': match.score,
                        'metadata': match.metadata
                    })

            logger.info(f"Found {len(matches)} similar jobs")
            return matches[:top_k]

        except Exception as e:
            logger.error(f"Failed to find similar jobs: {e}")
            return []

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a job by ID from Pinecone.

        Args:
            job_id: Job ID to retrieve

        Returns:
            Job data or None if not found
        """
        try:
            fetch_result = self.index.fetch(ids=[job_id])

            if job_id in fetch_result.vectors:
                return {
                    'id': job_id,
                    'metadata': fetch_result.vectors[job_id].metadata
                }

            return None

        except Exception as e:
            logger.error(f"Failed to fetch job {job_id}: {e}")
            return None

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job from Pinecone.

        Args:
            job_id: Job ID to delete

        Returns:
            True if successful
        """
        try:
            self.index.delete(ids=[job_id])
            logger.info(f"Deleted job: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False

    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the Pinecone index.

        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()

            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'namespaces': stats.namespaces,
            }

        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}

    def search_by_criteria(
        self,
        criteria: Dict[str, Any],
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search jobs by specific criteria (skills, location, etc.).

        Args:
            criteria: Dictionary of search criteria
            top_k: Number of results to return

        Returns:
            List of matching jobs
        """
        logger.info(f"Searching by criteria: {criteria}")

        # Build query text from criteria
        query_parts = []

        if 'skills' in criteria:
            skills = ', '.join(criteria['skills'])
            query_parts.append(f"Looking for jobs requiring: {skills}")

        if 'job_type' in criteria:
            query_parts.append(f"Job type: {criteria['job_type']}")

        if 'industry' in criteria:
            query_parts.append(f"Industry: {criteria['industry']}")

        query_text = '. '.join(query_parts)

        # Build metadata filters
        filters = {}

        if 'location' in criteria:
            filters['location'] = criteria['location']

        if 'is_remote' in criteria:
            filters['is_remote'] = criteria['is_remote']

        if 'min_salary' in criteria and criteria['min_salary']:
            filters['salary_min'] = {'$gte': criteria['min_salary']}

        # Create search query
        search_query = SearchQuery(
            query_text=query_text,
            top_k=top_k,
            filter_metadata=filters if filters else None,
            min_score=0.6
        )

        return self.search_similar_jobs(search_query)
