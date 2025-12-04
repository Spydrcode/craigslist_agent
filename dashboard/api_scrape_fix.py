# REPLACEMENT FOR /api/scrape endpoint in leads_app.py
# This uses the ObservableOrchestrator properly with agent progress tracking

@app.route('/api/scrape', methods=['POST'])
def api_scrape_jobs():
    """Scrape jobs from Craigslist using the full orchestrator pipeline with real-time agent progress."""
    logger.info("=== SCRAPE ENDPOINT HIT ===")

    try:
        logger.info("Step 1: Initializing orchestrator...")
        if not init_agents():
            return jsonify({'success': False, 'error': 'Failed to initialize orchestrator'}), 200

        if not orchestrator:
            return jsonify({'success': False, 'error': 'Orchestrator not available'}), 200

        logger.info("Step 2: Getting request data...")
        data = request.get_json()
        city = data.get('city', 'phoenix')
        category = data.get('category', 'sof')
        keywords = data.get('keywords', [])
        max_pages = data.get('max_pages', 2)
        max_jobs = data.get('max_jobs', 30)  # Limit number of jobs to analyze deeply

        logger.info(f"Running full orchestrator pipeline: {city}/{category}, max_pages={max_pages}, max_jobs={max_jobs}")

        # Run the full ObservableOrchestrator pipeline
        # This will automatically update progress via agent_progress module
        result = orchestrator.find_prospects(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages,
            max_jobs=max_jobs
        )

        if not result.get('success'):
            logger.error(f"Orchestrator failed: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'jobs': []
            }), 200

        # Extract prospects from orchestrator result
        prospects = result.get('prospects', [])
        stats = result.get('stats', {})

        logger.info(f"Orchestrator completed: {len(prospects)} prospects found")

        # Convert prospects to dashboard format
        dashboard_jobs = []
        for prospect in prospects:
            # Extract company profile
            company_profile = prospect.get('company_profile', {})
            company_name = company_profile.get('name', 'Unknown Company')

            # Extract first job posting for display
            job_postings = prospect.get('job_postings', [])
            first_job = job_postings[0] if job_postings else {}

            # Map priority tier
            priority = prospect.get('priority_tier', 'MEDIUM')
            tier_map = {
                'URGENT': 'TIER 1',
                'HIGH': 'TIER 2',
                'MEDIUM': 'TIER 3',
                'LOW': 'TIER 4'
            }
            tier = tier_map.get(priority, 'TIER 3')

            # Get growth signals
            growth_signals = company_profile.get('growth_signals', {})
            growth_score = growth_signals.get('growth_score', 0)
            growth_stage = growth_signals.get('growth_stage', 'Unknown')

            # Create dashboard job entry
            dashboard_jobs.append({
                'title': first_job.get('title', company_name),
                'url': first_job.get('url', ''),
                'location': first_job.get('location', ''),
                'date': first_job.get('posted_date', 'Recent'),
                'compensation': first_job.get('salary_text', ''),
                'company': company_name,
                'tier': tier,
                'score': int(prospect.get('lead_score', 0)),
                'qualification_score': int(prospect.get('lead_score', 0)),
                'qualification_reason': f"{priority} - Score: {prospect.get('lead_score', 0)}/100. Growth stage: {growth_stage}",
                'pain_points': [pp.get('description', '') for pp in first_job.get('pain_points', [])[:3]],
                'value_prop': f"{len(job_postings)} jobs posted. Growth score: {growth_score:.2f}",
                'description': first_job.get('description', '')[:500] if first_job.get('description') else company_name,
                'job_count': len(job_postings),
                'growth_indicators': [growth_stage]
            })

        logger.info(f"Returning {len(dashboard_jobs)} prospects to dashboard")

        return jsonify({
            'success': True,
            'jobs': dashboard_jobs,
            'total_scraped': stats.get('phase_1', {}).get('jobs_scanned', 0),
            'qualified_count': len(dashboard_jobs),
            'pages_scraped': max_pages,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"ERROR in scrape: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 200
