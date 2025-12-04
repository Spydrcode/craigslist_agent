"""
MCP Server Test Script

This script creates sample lead and job data, then starts the MCP server
for testing with ChatGPT.
"""

import sys
from pathlib import Path
from utils.mcp_data_manager import MCPDataManager


def create_sample_data():
    """Create sample lead and job data for testing."""
    
    print("Creating sample data for MCP server...")
    
    mcp = MCPDataManager()
    
    # Sample leads with various scenarios
    sample_leads = [
        {
            'lead_id': 'lead-001',
            'company_name': 'CloudTech Solutions',
            'lead_score': 92.0,
            'priority': 'HOT',
            'job_count': 15,
            'pain_points': [
                'Legacy monolith needs migration to microservices',
                'AWS infrastructure not optimized for cost',
                'CI/CD pipeline manual and slow'
            ],
            'opportunities': [
                {
                    'service': 'Cloud Migration & Optimization',
                    'estimated_value': '$100K-200K',
                    'confidence': 'very high'
                },
                {
                    'service': 'DevOps Automation',
                    'estimated_value': '$50K-75K',
                    'confidence': 'high'
                }
            ],
            'growth_stage': 'SCALING',
            'tech_stack': ['Python', 'React', 'AWS', 'PostgreSQL'],
            'source_url': 'https://sfbay.craigslist.org/example1'
        },
        {
            'lead_id': 'lead-002',
            'company_name': 'FinanceAI Corp',
            'lead_score': 88.0,
            'priority': 'HOT',
            'job_count': 10,
            'pain_points': [
                'Need to modernize trading platform',
                'Real-time data processing challenges',
                'Compliance and security requirements'
            ],
            'opportunities': [
                {
                    'service': 'Platform Modernization',
                    'estimated_value': '$150K-250K',
                    'confidence': 'high'
                }
            ],
            'growth_stage': 'FUNDED',
            'tech_stack': ['Java', 'Kafka', 'Redis', 'Docker'],
            'source_url': 'https://newyork.craigslist.org/example2'
        },
        {
            'lead_id': 'lead-003',
            'company_name': 'HealthData Analytics',
            'lead_score': 75.0,
            'priority': 'QUALIFIED',
            'job_count': 7,
            'pain_points': [
                'Data pipeline reliability issues',
                'ML model deployment challenges',
                'Scaling data warehouse'
            ],
            'opportunities': [
                {
                    'service': 'Data Engineering',
                    'estimated_value': '$75K-125K',
                    'confidence': 'medium'
                }
            ],
            'growth_stage': 'GROWING',
            'tech_stack': ['Python', 'Airflow', 'Snowflake', 'TensorFlow'],
            'source_url': 'https://boston.craigslist.org/example3'
        },
        {
            'lead_id': 'lead-004',
            'company_name': 'E-commerce Plus',
            'lead_score': 82.0,
            'priority': 'HOT',
            'job_count': 12,
            'pain_points': [
                'Checkout process slow during peak traffic',
                'Search functionality needs improvement',
                'Mobile experience subpar'
            ],
            'opportunities': [
                {
                    'service': 'Performance Optimization',
                    'estimated_value': '$60K-100K',
                    'confidence': 'high'
                },
                {
                    'service': 'Mobile App Development',
                    'estimated_value': '$80K-150K',
                    'confidence': 'medium'
                }
            ],
            'growth_stage': 'SCALING',
            'tech_stack': ['Node.js', 'React', 'MongoDB', 'Elasticsearch'],
            'source_url': 'https://seattle.craigslist.org/example4'
        },
        {
            'lead_id': 'lead-005',
            'company_name': 'SaaS Startup Inc',
            'lead_score': 68.0,
            'priority': 'POTENTIAL',
            'job_count': 5,
            'pain_points': [
                'Need to build core product features',
                'Seeking technical co-founder/lead',
                'Infrastructure setup needed'
            ],
            'opportunities': [
                {
                    'service': 'MVP Development',
                    'estimated_value': '$50K-100K',
                    'confidence': 'medium'
                }
            ],
            'growth_stage': 'STARTUP',
            'tech_stack': ['Python', 'Vue.js', 'PostgreSQL'],
            'source_url': 'https://austin.craigslist.org/example5'
        }
    ]
    
    # Sample job postings
    sample_jobs = [
        {
            'job_id': 'job-001',
            'title': 'Senior Backend Engineer',
            'company': 'CloudTech Solutions',
            'location': 'San Francisco, CA',
            'description': 'We are looking for an experienced backend engineer to help migrate our monolithic application to microservices. You will work on AWS infrastructure optimization and build CI/CD pipelines.',
            'requirements': [
                '5+ years Python/Django',
                'AWS experience (EC2, Lambda, RDS)',
                'Kubernetes and Docker',
                'Microservices architecture'
            ],
            'url': 'https://sfbay.craigslist.org/job1',
            'posted_date': '2024-01-15'
        },
        {
            'job_id': 'job-002',
            'title': 'DevOps Engineer',
            'company': 'CloudTech Solutions',
            'location': 'San Francisco, CA (Remote OK)',
            'description': 'Join our DevOps team to automate infrastructure and improve deployment processes. Help us achieve zero-downtime deployments and optimize costs.',
            'requirements': [
                'Terraform/CloudFormation',
                'Jenkins or GitLab CI',
                'AWS certified preferred',
                'Infrastructure as Code experience'
            ],
            'url': 'https://sfbay.craigslist.org/job2',
            'posted_date': '2024-01-16'
        },
        {
            'job_id': 'job-003',
            'title': 'Java Trading Platform Developer',
            'company': 'FinanceAI Corp',
            'location': 'New York, NY',
            'description': 'Build and modernize our real-time trading platform. Work with cutting-edge technology in high-frequency trading.',
            'requirements': [
                '7+ years Java',
                'Low-latency systems',
                'Kafka/messaging systems',
                'Financial domain experience'
            ],
            'url': 'https://newyork.craigslist.org/job3',
            'posted_date': '2024-01-14'
        },
        {
            'job_id': 'job-004',
            'title': 'Data Engineer',
            'company': 'HealthData Analytics',
            'location': 'Boston, MA',
            'description': 'Build reliable data pipelines for healthcare analytics. Work with large-scale data processing and ML infrastructure.',
            'requirements': [
                'Python/Scala',
                'Airflow or similar',
                'Snowflake or BigQuery',
                'Healthcare data experience a plus'
            ],
            'url': 'https://boston.craigslist.org/job4',
            'posted_date': '2024-01-17'
        },
        {
            'job_id': 'job-005',
            'title': 'Full Stack Engineer',
            'company': 'E-commerce Plus',
            'location': 'Seattle, WA',
            'description': 'Help scale our e-commerce platform for millions of users. Focus on performance optimization and mobile experience.',
            'requirements': [
                'Node.js backend',
                'React or React Native',
                'MongoDB/NoSQL',
                'E-commerce experience'
            ],
            'url': 'https://seattle.craigslist.org/job5',
            'posted_date': '2024-01-16'
        }
    ]
    
    # Save all data
    leads_saved = mcp.save_leads_bulk(sample_leads)
    jobs_saved = mcp.save_jobs_bulk(sample_jobs)
    
    print(f"\nSaved {leads_saved} leads")
    print(f"Saved {jobs_saved} jobs")
    
    # Show stats
    stats = mcp.get_stats()
    print(f"\nMCP Data Ready:")
    print(f"  Total Leads: {stats['leads_count']}")
    print(f"  Total Jobs: {stats['jobs_count']}")
    print(f"  Leads Dir: {stats['leads_dir']}")
    print(f"  Jobs Dir: {stats['jobs_dir']}")
    print(f"  Data Size: {stats['total_size_mb']:.2f} MB")
    
    return True


def start_mcp_server():
    """Start the MCP server."""
    print("\n" + "="*60)
    print("Starting MCP Server...")
    print("="*60)
    print("\nServer will be available at: http://localhost:8001/sse/")
    print("\nTo connect in ChatGPT:")
    print("  1. Go to Settings → Connectors")
    print("  2. Add MCP server URL: http://localhost:8001/sse/")
    print("  3. Enable tools: search, fetch, get_top_leads")
    print("\nExample queries in ChatGPT:")
    print('  "Find all leads with cloud migration needs"')
    print('  "Show me companies with scores above 80"')
    print('  "What are the top 5 hottest leads?"')
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Import and run server
    from mcp_server import main
    main()


if __name__ == "__main__":
    print("MCP Server Test Setup")
    print("="*60)
    
    # Create sample data
    success = create_sample_data()
    
    if not success:
        print("\nFailed to create sample data")
        sys.exit(1)
    
    # Ask user if they want to start server
    print("\n" + "="*60)
    response = input("\nStart MCP server now? (y/n): ").lower()
    
    if response == 'y':
        start_mcp_server()
    else:
        print("\nSample data created. You can start the server later with:")
        print("  python mcp_server.py")
        print("\nServer URL: http://localhost:8001/sse/")
