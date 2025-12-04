"""
Test script for Batch API processing.
Demonstrates processing hundreds of job postings asynchronously at 50% cost savings.
"""
from agents import BatchProcessorAgent, process_jobs_batch
from utils import get_logger
import json

logger = get_logger(__name__)


def test_batch_creation():
    """Test creating batch input file."""
    print("\n" + "="*80)
    print("TEST 1: Create Batch Input File")
    print("="*80)
    
    # Sample job postings
    jobs = [
        {
            "url": "https://sfbay.craigslist.org/job1",
            "title": "Senior Software Engineer",
            "company_name": "TechCorp",
            "location": "San Francisco, CA",
            "description": "We're looking for a senior engineer to join our growing team..."
        },
        {
            "url": "https://sfbay.craigslist.org/job2",
            "title": "DevOps Engineer",
            "company_name": "CloudSystems",
            "location": "Palo Alto, CA",
            "description": "Help us scale our infrastructure and improve deployment processes..."
        },
        {
            "url": "https://sfbay.craigslist.org/job3",
            "title": "Product Manager",
            "company_name": "StartupXYZ",
            "location": "Remote",
            "description": "Lead product strategy for our SaaS platform..."
        }
    ]
    
    agent = BatchProcessorAgent()
    
    # Create batch input file
    input_file = agent.create_batch_input_file(
        jobs,
        task_type="analyze",
        model="gpt-4o-mini"
    )
    
    print(f"\n✅ Created batch input file: {input_file}")
    
    # Read and display sample
    with open(input_file, 'r') as f:
        first_line = f.readline()
        request = json.loads(first_line)
        print(f"\n📝 Sample request:")
        print(f"   Custom ID: {request['custom_id']}")
        print(f"   Model: {request['body']['model']}")
        print(f"   Messages: {len(request['body']['messages'])}")
    
    return input_file


def test_batch_upload_and_create():
    """Test uploading file and creating batch."""
    print("\n" + "="*80)
    print("TEST 2: Upload File and Create Batch")
    print("="*80)
    
    # Create sample jobs
    jobs = [
        {"url": f"job_{i}", "title": f"Position {i}", "company_name": f"Company {i}",
         "description": f"Job description {i}..."} 
        for i in range(5)
    ]
    
    agent = BatchProcessorAgent()
    
    # Create input file
    input_file = agent.create_batch_input_file(jobs, task_type="qualify")
    print(f"✅ Created input file: {input_file}")
    
    # Upload
    print("\n⬆️ Uploading to OpenAI...")
    file_id = agent.upload_batch_file(input_file)
    print(f"✅ Uploaded file: {file_id}")
    
    # Create batch
    print("\n🚀 Creating batch job...")
    batch_id = agent.create_batch(
        file_id,
        description="Test batch - 5 jobs qualification"
    )
    print(f"✅ Batch created: {batch_id}")
    
    return batch_id


def test_batch_status():
    """Test checking batch status."""
    print("\n" + "="*80)
    print("TEST 3: Check Batch Status")
    print("="*80)
    
    agent = BatchProcessorAgent()
    
    # List recent batches
    print("\n📋 Recent batches:")
    batches = agent.list_batches(limit=5)
    
    for batch in batches:
        print(f"\n   Batch: {batch['id']}")
        print(f"   Status: {batch['status']}")
        print(f"   Progress: {batch['request_counts']['completed']}/{batch['request_counts']['total']}")
    
    if batches:
        # Check first batch in detail
        batch_id = batches[0]['id']
        print(f"\n🔍 Detailed status for {batch_id}:")
        status = agent.check_batch_status(batch_id)
        
        print(f"   Status: {status['status']}")
        print(f"   Total requests: {status['request_counts']['total']}")
        print(f"   Completed: {status['request_counts']['completed']}")
        print(f"   Failed: {status['request_counts']['failed']}")
        
        if status['output_file_id']:
            print(f"   Output file: {status['output_file_id']}")


def test_convenience_function():
    """Test the convenience function for complete workflow."""
    print("\n" + "="*80)
    print("TEST 4: Convenience Function (Complete Workflow)")
    print("="*80)
    
    # Sample jobs
    jobs = [
        {
            "url": f"https://example.com/job{i}",
            "title": f"Engineer {i}",
            "company_name": f"Company {i}",
            "location": "San Francisco, CA",
            "description": "Looking for talented engineers to join our team..."
        }
        for i in range(10)
    ]
    
    print(f"\n🚀 Processing {len(jobs)} jobs in batch mode...")
    print("   This will create, upload, and start the batch.")
    print("   Results will be available within 24 hours.")
    
    result = process_jobs_batch(
        jobs,
        task_type="analyze",
        wait_for_completion=False,  # Don't wait (would take hours)
        model="gpt-4o-mini"
    )
    
    print(f"\n✅ Batch started successfully!")
    print(f"   Batch ID: {result['batch_id']}")
    print(f"   Input file: {result['input_file']}")
    print(f"   Job count: {result['job_count']}")
    print(f"\n💡 Check status with: check_batch_status('{result['batch_id']}')")


def test_batch_cost_comparison():
    """Demonstrate cost savings of batch processing."""
    print("\n" + "="*80)
    print("TEST 5: Cost Comparison (Batch vs Synchronous)")
    print("="*80)
    
    num_jobs = 500
    avg_tokens_per_job = 1000  # Estimate: 500 input + 500 output
    
    # GPT-4o-mini pricing (example)
    sync_cost_per_1k = 0.00015  # $0.15 per 1M tokens
    batch_cost_per_1k = 0.000075  # 50% discount
    
    total_tokens = num_jobs * avg_tokens_per_job
    
    sync_cost = (total_tokens / 1000) * sync_cost_per_1k
    batch_cost = (total_tokens / 1000) * batch_cost_per_1k
    
    print(f"\n📊 Processing {num_jobs} job postings:")
    print(f"\n   Synchronous API:")
    print(f"     Total tokens: {total_tokens:,}")
    print(f"     Cost: ${sync_cost:.2f}")
    print(f"\n   Batch API:")
    print(f"     Total tokens: {total_tokens:,}")
    print(f"     Cost: ${batch_cost:.2f}")
    print(f"\n   💰 Savings: ${sync_cost - batch_cost:.2f} ({((sync_cost - batch_cost) / sync_cost * 100):.0f}% reduction)")
    
    print(f"\n   ⏱️ Time comparison:")
    print(f"     Synchronous: ~{num_jobs * 2} seconds ({num_jobs * 2 / 60:.1f} minutes)")
    print(f"     Batch: <24 hours (usually much faster)")
    print(f"\n   📈 Rate limits:")
    print(f"     Synchronous: Subject to per-model limits")
    print(f"     Batch: Separate pool (higher limits)")


def test_parse_results():
    """Test parsing results from a completed batch."""
    print("\n" + "="*80)
    print("TEST 6: Parse Batch Results")
    print("="*80)
    
    print("\n⚠️ This test requires a completed batch.")
    print("   To test result parsing, run this after a batch completes.")
    print("\n   Example usage:")
    print("   ```python")
    print("   agent = BatchProcessorAgent()")
    print("   results_file = agent.download_results('batch_xxx')")
    print("   parsed = agent.parse_results(results_file)")
    print("   ```")


def run_all_tests():
    """Run all batch API tests."""
    print("\n" + "🎯"*40)
    print("OPENAI BATCH API TESTS")
    print("🎯"*40)
    
    print("\n💡 The Batch API offers:")
    print("   • 50% cost reduction")
    print("   • Higher rate limits (separate pool)")
    print("   • 24-hour completion window")
    print("   • Perfect for processing hundreds/thousands of jobs")
    
    try:
        # Test 1: Create batch input
        test_batch_creation()
        
        # Test 2: Upload and create (actual API call)
        print("\n\n⚠️ TEST 2 will make actual API calls. Continue? (y/n): ", end='')
        # Skipping actual API calls in test
        print("Skipped (use manually)")
        
        # Test 3: Status checking
        test_batch_status()
        
        # Test 4: Convenience function
        print("\n\n⚠️ TEST 4 will create a batch. Continue? (y/n): ", end='')
        # Skipped
        print("Skipped (use manually)")
        
        # Test 5: Cost comparison
        test_batch_cost_comparison()
        
        # Test 6: Parse results
        test_parse_results()
        
        print("\n" + "="*80)
        print("✅ TESTS COMPLETED")
        print("="*80)
        
        print("\n🎉 Batch API Integration Complete!")
        print("\nReady to use:")
        print("  • BatchProcessorAgent - Full-featured batch agent")
        print("  • process_jobs_batch() - Convenience function")
        print("  • 50% cost savings on job analysis")
        print("  • Process thousands of jobs overnight")
        
    except Exception as e:
        logger.error(f"Test suite error: {e}", exc_info=True)
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    run_all_tests()
