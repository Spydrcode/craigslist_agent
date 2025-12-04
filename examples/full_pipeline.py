"""
Example: Complete pipeline with all agents.
Demonstrates scraping, parsing, vector storage, and database storage.
"""
import sys
sys.path.append('..')

from orchestrator import Orchestrator
from utils import setup_logger

# Setup logging
logger = setup_logger(__name__)


def main():
    """Run complete pipeline example."""
    logger.info("Starting full pipeline example")

    # Initialize orchestrator with all features enabled
    orchestrator = Orchestrator(
        use_ai_parsing=True,
        use_vector_storage=True,
        use_database_storage=True
    )

    # Define search criteria for relevance scoring
    criteria = {
        'required_skills': ['python', 'machine learning', 'tensorflow'],
        'preferred_location': 'remote',
        'experience_level': 'senior',
    }

    # Run complete pipeline
    print("\n" + "=" * 80)
    print("RUNNING COMPLETE JOB SCRAPING PIPELINE")
    print("=" * 80)

    result = orchestrator.run_pipeline(
        city="sfbay",
        category="sof",
        keywords=["machine learning", "AI"],
        max_pages=2,
        criteria=criteria
    )

    # Check results
    if not result['success']:
        print(f"\nPipeline failed: {result.get('error')}")
        return

    # Display statistics
    print("\n" + "=" * 80)
    print("PIPELINE RESULTS")
    print("=" * 80)

    stats = result['stats']
    print(f"\nJobs Scraped: {stats.get('jobs_scraped', 0)}")
    print(f"Jobs Parsed: {stats.get('jobs_parsed', 0)}")
    print(f"Embeddings Stored: {stats.get('embeddings_stored', 0)}")
    print(f"Database Records: {stats.get('database_records', 0)}")

    if 'avg_relevance' in stats:
        print(f"\nAverage Relevance Score: {stats['avg_relevance']:.2f}")
        print(f"High Relevance Jobs (>0.7): {stats.get('high_relevance_count', 0)}")

    # Show top jobs
    if 'jobs' in result:
        jobs = result['jobs']
        top_jobs = sorted(
            jobs,
            key=lambda x: x.relevance_score or 0,
            reverse=True
        )[:5]

        print("\n" + "=" * 80)
        print("TOP 5 MOST RELEVANT JOBS")
        print("=" * 80)

        for i, job in enumerate(top_jobs, 1):
            print(f"\n{i}. {job.title}")
            print(f"   Relevance: {job.relevance_score:.2f}" if job.relevance_score else "")
            print(f"   URL: {job.url}")
            print(f"   Location: {job.location}")
            print(f"   Remote: {job.is_remote}")
            print(f"   Skills: {', '.join(job.skills[:5])}" if job.skills else "")
            print(f"   Pain Points: {len(job.pain_points)}")

    # Demonstrate semantic search
    print("\n" + "=" * 80)
    print("SEMANTIC SEARCH EXAMPLE")
    print("=" * 80)

    search_results = orchestrator.search_jobs(
        query="Senior engineer experienced with neural networks and deep learning",
        top_k=5,
        use_semantic_search=True
    )

    print(f"\nFound {len(search_results)} matching jobs:")
    for i, result in enumerate(search_results, 1):
        metadata = result.get('metadata', {})
        print(f"\n{i}. {metadata.get('title', 'Unknown')}")
        print(f"   Match Score: {result.get('score', 0):.2f}")
        print(f"   Location: {metadata.get('location', 'N/A')}")

    # Market analysis
    print("\n" + "=" * 80)
    print("JOB MARKET ANALYSIS")
    print("=" * 80)

    analysis = orchestrator.analyze_job_market(city="sfbay", category="sof")

    if 'error' not in analysis:
        print(f"\nTotal Jobs in Database: {analysis.get('total_jobs', 0)}")
        print(f"Remote Jobs: {analysis.get('remote_jobs', 0)}")

        if 'top_skills' in analysis:
            print("\nTop 5 In-Demand Skills:")
            for skill, count in analysis['top_skills'][:5]:
                print(f"  {skill}: {count}")

    print("\n" + "=" * 80)
    print("PIPELINE COMPLETE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
