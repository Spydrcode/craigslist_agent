"""
Observable Orchestrator with Real-time Progress Tracking
NEW: Signal-based growth detection (NOT direct lead extraction from Craigslist)
"""
from orchestrator_simple import SimpleProspectingOrchestrator
from agent_progress import PipelineProgress, set_current_progress, clear_current_progress
from typing import Dict, Any, List
from utils import get_logger
from models_enhanced import CompanyProfile, ProspectLead, JobPostingEnhanced
from models import JobSignal, ExternalCompany
from datetime import datetime
import json
import uuid

logger = get_logger(__name__)


class ObservableOrchestrator(SimpleProspectingOrchestrator):
    """
    Enhanced orchestrator with real-time progress tracking.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress: PipelineProgress = None

    def find_prospects(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Find prospects using NEW SIGNAL-BASED WORKFLOW:

        PHASE 1 (SIGNAL EXTRACTION - 1-2 minutes):
          1. Quick scan Craigslist job postings (titles + descriptions)
          2. Extract industry/job signals (NO company names/contacts)
          3. Aggregate signals by industry + location

        PHASE 2 (EXTERNAL DISCOVERY - 2-3 minutes):
          4. Use web search to find real companies in those industries
          5. Search job boards for companies currently hiring

        PHASE 3 (GROWTH SCORING - 3-5 minutes):
          6. Score each company 0-100 based on:
             - Hiring velocity (job postings across boards)
             - Review activity (recent reviews)
             - Web activity (blog posts, news)
             - Expansion signals (funding, locations)
          7. Return top-scoring companies

        OUTPUT: List of growing companies (NOT direct Craigslist leads)
        """
        # Create progress tracker
        self.progress = PipelineProgress()
        set_current_progress(self.progress)

        # Define pipeline stages (NEW SIGNAL-BASED WORKFLOW)
        scraper_agent = self.progress.add_agent("scraper", "Scanning Craigslist for job signals")
        signal_agent = self.progress.add_agent("signal_extractor", "Extracting industry signals")
        external_agent = self.progress.add_agent("external_search", "Finding companies via web search")
        scoring_agent = self.progress.add_agent("growth_scorer", "Scoring companies for growth")
        save_agent = self.progress.add_agent("saver", "Saving results")

        try:
            self.progress.start()

            # ================================================================
            # PHASE 1: SIGNAL EXTRACTION FROM CRAIGSLIST (1-2 minutes)
            # ================================================================

            city = kwargs.get('city', 'sfbay')
            category = kwargs.get('category', 'sof')
            max_pages = kwargs.get('max_pages', 2)
            max_signals = kwargs.get('max_jobs', 50)  # Renamed to max_signals for clarity

            # STAGE 1: Scrape Craigslist for Job Postings (as signal source)
            scraper_agent.start(message=f"Scanning Craigslist {city}/{category} for job signals...")
            logger.info(f"PHASE 1 - Stage 1: Scraping Craigslist for signals")

            from agents.scraper_agent import ScraperAgent
            from models import ScraperConfig

            # Get full job details (need descriptions for signal extraction)
            scraper_config = ScraperConfig(
                city=city,
                category=category,
                max_pages=max_pages,
                quick_scan_only=False,  # Need full descriptions for signal extraction
                max_jobs_to_analyze=max_signals
            )
            scraper = ScraperAgent(config=scraper_config)

            raw_jobs = scraper.scrape_listings(keywords=kwargs.get('keywords'))
            scraper_agent.complete(result=len(raw_jobs), message=f"Scraped {len(raw_jobs)} job postings")
            self.progress.notify()

            if not raw_jobs:
                scraper_agent.fail("No job postings found")
                self.progress.notify()
                return {'success': False, 'error': 'No job postings found', 'companies': [], 'signals': []}

            # STAGE 2: Extract Signals from Job Postings
            signal_agent.start(total_items=len(raw_jobs), message="Extracting industry/job signals...")
            logger.info(f"PHASE 1 - Stage 2: Extracting signals from {len(raw_jobs)} postings")

            job_signals = []
            for idx, raw_job in enumerate(raw_jobs, 1):
                signal_agent.update(current=idx, message=f"Extracting signals {idx}/{len(raw_jobs)}...")
                self.progress.notify()

                try:
                    signal = self.parser_agent.extract_job_signal(raw_job, use_ai=self.use_ai_parsing)
                    job_signals.append(signal)
                except Exception as e:
                    logger.error(f"Signal extraction failed for {raw_job.url}: {e}")
                    continue

            signal_agent.complete(
                result=len(job_signals),
                message=f"Extracted {len(job_signals)} industry signals"
            )
            self.progress.notify()

            if not job_signals:
                signal_agent.fail("No signals extracted")
                self.progress.notify()
                return {'success': False, 'error': 'Signal extraction failed', 'companies': [], 'signals': []}

            # Log signal summary
            industries = list(set(s.industry for s in job_signals))
            logger.info(f"Signal Summary: {len(job_signals)} signals across {len(industries)} industries: {industries[:5]}")

            # ================================================================
            # PHASE 2: EXTERNAL COMPANY DISCOVERY (2-3 minutes)
            # ================================================================

            external_agent.start(message="Searching for companies via web search...")
            logger.info(f"PHASE 2: Finding companies in detected industries")

            from agents.external_search_agent import ExternalSearchAgent
            external_searcher = ExternalSearchAgent(
                client_agent=self.parser_agent.client,
                use_web_search=True
            )

            # Find companies based on signals
            discovered_companies = external_searcher.find_companies_from_signals(
                signals=job_signals,
                max_companies_per_industry=10
            )

            external_agent.complete(
                result=len(discovered_companies),
                message=f"Found {len(discovered_companies)} companies"
            )
            self.progress.notify()

            if not discovered_companies:
                external_agent.fail("No companies found")
                self.progress.notify()
                return {
                    'success': True,  # Still success - we got signals
                    'error': 'No companies found via external search',
                    'companies': [],
                    'signals': [s.dict() for s in job_signals]
                }

            # ================================================================
            # PHASE 3: GROWTH SCORING (3-5 minutes)
            # ================================================================

            scoring_agent.start(total_items=len(discovered_companies), message="Scoring companies for growth...")
            logger.info(f"PHASE 3: Scoring {len(discovered_companies)} companies")

            from agents.growth_scoring_agent import GrowthScoringAgent
            growth_scorer = GrowthScoringAgent(
                client_agent=self.parser_agent.client,
                use_web_search=True
            )

            # Score all companies
            scored_companies = []
            for idx, company_data in enumerate(discovered_companies, 1):
                scoring_agent.update(
                    current=idx,
                    message=f"Scoring {company_data.get('company_name', 'Unknown')}..."
                )
                self.progress.notify()

            # Batch scoring
            scored_companies = growth_scorer.score_companies(discovered_companies)

            scoring_agent.complete(
                result=len(scored_companies),
                message=f"Scored {len(scored_companies)} companies"
            )
            self.progress.notify()

            # Get top companies (min score 30)
            top_companies = growth_scorer.get_top_companies(
                scored_companies,
                min_score=30.0,
                top_n=20  # Return top 20
            )

            logger.info(f"Found {len(top_companies)} high-growth companies (score >= 30)")

            # ================================================================
            # SAVE RESULTS
            # ================================================================

            save_agent.start(message="Saving results...")
            
            # Save signals and companies
            results = {
                'success': True,
                'signals': [s.dict() for s in job_signals],
                'companies': [c.dict() for c in scored_companies],
                'top_companies': [c.dict() for c in top_companies],
                'stats': {
                    'total_signals': len(job_signals),
                    'industries_detected': len(industries),
                    'companies_found': len(discovered_companies),
                    'companies_scored': len(scored_companies),
                    'high_growth_companies': len(top_companies),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }

            # Save to file
            self._save_signal_results(results)

            save_agent.complete(message="Results saved")
            self.progress.notify()

            self.progress.complete()
            self.progress.notify()

            return results

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            self.progress.fail(str(e))
            self.progress.notify()
            return {'success': False, 'error': str(e), 'companies': [], 'signals': []}

        finally:
            clear_current_progress()

    def _save_signal_results(self, results: Dict[str, Any]):
        """Save signal and company results to files."""
        import os
        from pathlib import Path
        
        output_dir = Path("data/signals")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Save full results
        results_file = output_dir / f"signal_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {results_file}")

            # STAGE 5: Growth Analysis (on parsed jobs)
            growth_agent.start(total_items=len(parsed_companies_data), message="Analyzing growth signals...")
            logger.info(f"PHASE 2 - Stage 5: Growth analysis on {len(parsed_companies_data)} companies")

            companies_with_growth = []
            for i, company_data in enumerate(parsed_companies_data, 1):
                growth_agent.update(current=i, message=f"Analyzing {company_data['company_score'].company_name}...")
                self.progress.notify()

                company_score = company_data['company_score']
                parsed_jobs = company_data['parsed_jobs']

                growth_signals = self.growth_analyzer.analyze_multiple_postings(
                    parsed_jobs,
                    company_score.company_name
                )

                # Try to get a better company name from parsed jobs
                # Parser agent may have extracted actual company name from job description
                better_company_name = company_score.company_name
                for job in parsed_jobs:
                    if hasattr(job, 'company_name') and job.company_name and job.company_name != 'Unknown' and len(job.company_name) > 2:
                        # Found a real company name, use it
                        better_company_name = job.company_name
                        logger.info(f"Using parsed company name '{better_company_name}' instead of '{company_score.company_name}'")
                        break

                company_profile = CompanyProfile(
                    name=better_company_name,
                    growth_signals=growth_signals
                )
                companies_with_growth.append({
                    'profile': company_profile,
                    'jobs': parsed_jobs,
                    'velocity_score': company_score  # Keep original velocity score
                })

            growth_agent.complete(
                result=len(companies_with_growth),
                message=f"Analyzed {len(companies_with_growth)} companies"
            )
            self.progress.notify()

            # STAGE 6: Company Research (skipped if disabled)
            if self.use_company_research:
                research_agent.start(total_items=len(companies_with_growth), message="Researching companies...")
                logger.info(f"PHASE 2 - Stage 6: Researching {len(companies_with_growth)} companies")
                # Research implementation here (optional deep dive)
                research_agent.complete(message="Research completed")
            else:
                research_agent.skip("Company research disabled")
            self.progress.notify()

            # STAGE 7: Create Prospects & Service Matching
            matcher_agent.start(total_items=len(companies_with_growth), message="Matching services...")
            logger.info(f"PHASE 2 - Stage 7: Service matching for {len(companies_with_growth)} companies")

            prospects = []
            for i, company_data in enumerate(companies_with_growth, 1):
                matcher_agent.update(current=i, message=f"Matching services for {company_data['profile'].name}...")
                self.progress.notify()

                # Include the hiring velocity score in the prospect
                velocity_score = company_data['velocity_score']
                
                # Convert ParsedJobPosting to JobPostingEnhanced
                enhanced_jobs = []
                for parsed_job in company_data['jobs']:
                    enhanced_job = JobPostingEnhanced(
                        title=parsed_job.title,
                        url=parsed_job.url,
                        description=parsed_job.description,
                        company_name=company_data['profile'].name,  # Use company name from profile
                        location=parsed_job.location,
                        posted_date=parsed_job.posted_date if parsed_job.posted_date else None,
                        skills_required=parsed_job.skills or [],
                        pain_points=parsed_job.pain_points or [],
                        technologies=[],  # ParsedJobPosting doesn't have technologies field
                        salary_min=parsed_job.salary_min,
                        salary_max=parsed_job.salary_max,
                        salary_text=parsed_job.salary_text,
                        is_remote=parsed_job.is_remote,
                        is_hybrid=parsed_job.is_hybrid,
                        is_onsite=parsed_job.is_onsite,
                        scraped_at=parsed_job.parsed_at if parsed_job.parsed_at else datetime.utcnow()
                    )
                    enhanced_jobs.append(enhanced_job)

                # Create prospect with initial data
                prospect = ProspectLead(
                    lead_id=str(uuid.uuid4()),
                    company_profile=company_data['profile'],
                    job_postings=enhanced_jobs,
                    service_opportunities=[],  # Will be filled by service matcher
                    lead_score=velocity_score.total_score,  # Start with hiring velocity score
                    priority_tier=velocity_score.tier  # Use tier from velocity scoring
                )

                # Identify service opportunities (expects ProspectLead object)
                opportunities = self.service_matcher.identify_opportunities(prospect)
                prospect.service_opportunities = opportunities

                prospects.append(prospect)

            matcher_agent.complete(message="Service matching completed")
            self.progress.notify()

            # STAGE 8: ML Scoring
            ml_scoring_agent.start(total_items=len(prospects), message="Scoring leads...")
            logger.info(f"PHASE 2 - Stage 8: ML scoring for {len(prospects)} companies")

            # Score all prospects with ML (will adjust the velocity score)
            scored_prospects = self.ml_scorer.batch_score_leads(prospects)

            # Sort by score (highest first) - already scored by hiring velocity
            scored_prospects.sort(key=lambda p: p.lead_score, reverse=True)

            # Filter by minimum score if specified
            min_score = kwargs.get('min_lead_score', 40.0)
            qualified_prospects = [p for p in scored_prospects if p.lead_score >= min_score]

            ml_scoring_agent.complete(
                result=len(qualified_prospects),
                message=f"Scored {len(qualified_prospects)} qualified leads"
            )
            self.progress.notify()

            logger.info(f"PHASE 2 COMPLETE: {len(qualified_prospects)} qualified prospects")

            # STAGE 9: Save Results
            save_agent.start(message="Saving results...")

            # Save to files
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = self.output_dir / f"prospects_{timestamp}.json"
            csv_file = self.output_dir / f"prospects_{timestamp}.csv"
            stats_file = self.output_dir / f"stats_{timestamp}.json"

            # Save JSON
            with open(output_file, 'w') as f:
                json.dump(
                    [p.dict() for p in qualified_prospects],
                    f,
                    indent=2,
                    default=str
                )

            # Save CSV
            self._save_to_csv(qualified_prospects, csv_file)

            # Save stats with new two-phase metrics
            stats = {
                'timestamp': timestamp,
                'workflow': 'two_phase_hiring_velocity',
                'phase_1': {
                    'jobs_scanned': len(raw_jobs),
                    'companies_found': len(promising_companies),
                    'companies_with_3plus_jobs': len(promising_companies),
                    'companies_scored': len(scored_companies)
                },
                'phase_2': {
                    'top_companies_analyzed': len(top_companies),
                    'companies_parsed': len(parsed_companies_data),
                    'companies_with_growth': len(companies_with_growth),
                    'qualified_prospects': len(qualified_prospects)
                },
                'filters': {
                    'min_company_jobs': 3,
                    'max_companies_to_analyze': max_companies_to_analyze,
                    'min_lead_score': min_score
                },
                'top_prospect': {
                    'company': qualified_prospects[0].company_profile.name if qualified_prospects else None,
                    'score': qualified_prospects[0].lead_score if qualified_prospects else 0,
                    'job_count': len(qualified_prospects[0].job_postings) if qualified_prospects else 0
                } if qualified_prospects else None
            }

            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)

            save_agent.complete(message=f"Saved to {output_file.name}")
            self.progress.notify()

            self.progress.complete()

            return {
                'success': True,
                'prospects': qualified_prospects,
                'stats': stats
            }

        except Exception as e:
            logger.error(f"Pipeline error: {e}", exc_info=True)
            # Mark current agent as failed
            for agent in self.progress.agents:
                if agent.status.value == "running":
                    agent.fail(str(e))
            self.progress.notify()

            return {
                'success': False,
                'error': str(e),
                'prospects': [],
                'stats': {}
            }

        finally:
            clear_current_progress()


    def _group_by_company(self, jobs):
        """Group jobs by company name."""
        from collections import defaultdict
        company_jobs = defaultdict(list)

        for job in jobs:
            company_name = job.company if job.company else "Unknown Company"
            company_jobs[company_name].append(job)

        return dict(company_jobs)


    def _save_to_csv(self, prospects, filename):
        """Save prospects to CSV."""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Lead ID', 'Company', 'Score', 'Priority', 'Growth Stage',
                'Growth Score', 'Jobs', 'Opportunities'
            ])

            # Data
            for p in prospects:
                writer.writerow([
                    p.lead_id,
                    p.company_profile.name,
                    round(p.lead_score, 1),
                    p.priority_tier,
                    p.company_profile.growth_signals.growth_stage,
                    round(p.company_profile.growth_signals.growth_score, 2),
                    len(p.job_postings),
                    len(p.service_opportunities)
                ])


import uuid
