"""
Flask-based Lead Analysis Dashboard for Forecasta.
Interactive web interface for viewing, filtering, and managing qualified leads.
Runs on http://localhost:3000
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, jsonify, request, send_file
from flask_sock import Sock
import json
import glob
import requests
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from utils import get_logger

logger = get_logger(__name__)

# Import current agents
from agents import (
    ClientAgent,
    ScraperAgent,
    ParserAgent,
    CompanyResearchAgent,
    ConversationalLeadAgent,
    BatchProcessorAgent,
    DeepResearchAgent,
    FileSearchAgent,
    VisualizationAgent,
    EnhancedCompanyScoringAgent,
)

# Import legacy compatibility layer for old dashboard code
from agents.legacy_compat import (
    LeadAnalysisAgent,
    VectorAgent,
    DatabaseAgent,
    JobQualifierAgent,
)

# Try to import orchestrator (ObservableOrchestrator first for progress tracking)
try:
    from orchestrator_observable import ObservableOrchestrator as Orchestrator
    ORCHESTRATOR_AVAILABLE = True
    print("Using ObservableOrchestrator with real-time progress tracking")
except ImportError:
    try:
        from orchestrator_simple import SimpleProspectingOrchestrator as Orchestrator
        ORCHESTRATOR_AVAILABLE = True
        print("Warning: Using SimpleProspectingOrchestrator (no progress tracking)")
    except ImportError:
        ORCHESTRATOR_AVAILABLE = False
        print("Warning: No orchestrator available")
        Orchestrator = None

# RAG is deprecated - set to False
RAG_AVAILABLE = False

app = Flask(__name__)
app.config['SECRET_KEY'] = 'forecasta-lead-analysis-2025'
sock = Sock(app)

# WebSocket clients for real-time updates
websocket_clients = []

# Global error handlers to ensure JSON responses
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    logger.error(traceback.format_exc())
    return jsonify({'success': False, 'error': str(e)}), 500

# Initialize agents
client_agent = None
scraper_agent = None
parser_agent = None
research_agent = None
conversational_agent = None
batch_agent = None
deep_research_agent = None
orchestrator = None
company_scorer = None  # NEW: Enhanced company scoring
lead_analysis_agent = None  # Legacy compatibility
vector_agent = None  # Legacy compatibility  
database_agent = None  # Legacy compatibility
job_qualifier = None  # Legacy compatibility

def init_agents():
    """Initialize all agents lazily."""
    global client_agent, scraper_agent, parser_agent, research_agent
    global conversational_agent, batch_agent, deep_research_agent, orchestrator
    global company_scorer, lead_analysis_agent, vector_agent, database_agent, job_qualifier
    
    try:
        if not client_agent:
            print("Initializing ClientAgent...")
            client_agent = ClientAgent()
            print("✓ ClientAgent initialized")
            
        if not scraper_agent:
            print("Initializing ScraperAgent...")
            scraper_agent = ScraperAgent()
            print("✓ ScraperAgent initialized")
            
        if not parser_agent:
            print("Initializing ParserAgent...")
            parser_agent = ParserAgent(client_agent)
            print("✓ ParserAgent initialized")
            
        if not research_agent:
            print("Initializing CompanyResearchAgent...")
            research_agent = CompanyResearchAgent(client_agent)
            print("✓ CompanyResearchAgent initialized")
        
        if not company_scorer:
            print("Initializing EnhancedCompanyScoringAgent...")
            company_scorer = EnhancedCompanyScoringAgent()
            print("✓ EnhancedCompanyScoringAgent initialized")
        
        # Legacy compatibility agents
        if not lead_analysis_agent:
            print("Initializing LeadAnalysisAgent (legacy compat)...")
            lead_analysis_agent = LeadAnalysisAgent()
            print("✓ LeadAnalysisAgent initialized")
            
        if not vector_agent:
            vector_agent = VectorAgent()
            
        if not database_agent:
            database_agent = DatabaseAgent()
            
        if not job_qualifier:
            job_qualifier = JobQualifierAgent()
            
        # OpenAI enhanced agents (optional)
        try:
            if not conversational_agent:
                conversational_agent = ConversationalLeadAgent()
                print("✓ ConversationalLeadAgent initialized")
        except Exception as e:
            print(f"Warning: ConversationalLeadAgent failed: {e}")
            
        try:
            if not batch_agent:
                batch_agent = BatchProcessorAgent()
                print("✓ BatchProcessorAgent initialized")
        except Exception as e:
            print(f"Warning: BatchProcessorAgent failed: {e}")
            
        try:
            if not deep_research_agent:
                deep_research_agent = DeepResearchAgent()
                print("✓ DeepResearchAgent initialized")
        except Exception as e:
            print(f"Warning: DeepResearchAgent failed: {e}")
            
        try:
            if not orchestrator and ORCHESTRATOR_AVAILABLE:
                orchestrator = Orchestrator(
                    use_ai_parsing=True,
                    use_company_research=True,
                    output_dir="output/prospects"
                )
                print("✓ Orchestrator initialized")
        except Exception as e:
            print(f"Warning: Orchestrator failed to initialize: {e}")
            
        return True
    except Exception as e:
        print(f"CRITICAL Error initializing agents: {e}")
        print(traceback.format_exc())
        return False

# Paths
LEADS_DIR = Path(__file__).parent.parent / 'output' / 'leads'
LEADS_DIR.mkdir(parents=True, exist_ok=True)
CLIENTS_DIR = Path('data/clients')
CLIENTS_DIR.mkdir(parents=True, exist_ok=True)


def cleanup_old_data():
    """Clean up old client data and temporary files on server restart."""
    try:
        # Clear all_clients.json on restart
        all_clients_file = CLIENTS_DIR / 'all_clients.json'
        if all_clients_file.exists():
            all_clients_file.unlink()
            logger.info("Cleared all_clients.json on server restart")
        
        # Optional: Clear individual client files (uncomment if needed)
        # for client_file in CLIENTS_DIR.glob('client_*.json'):
        #     client_file.unlink()
        #     logger.info(f"Deleted old client file: {client_file.name}")
        
        logger.info("✅ Data cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Run cleanup on server start
cleanup_old_data()


# ============================================================================
# WEBSOCKET ENDPOINTS - Real-Time Agent Progress
# ============================================================================

@sock.route('/ws/progress')
def websocket_progress(ws):
    """WebSocket endpoint for real-time progress updates."""
    websocket_clients.append(ws)
    try:
        while True:
            # Keep connection alive and send progress updates
            try:
                # Import here to avoid circular dependency
                from agent_progress import get_current_progress
                progress = get_current_progress()

                if progress:
                    # Convert PipelineProgress object to dict
                    progress_dict = progress.to_dict()
                    ws.send(json.dumps({
                        'type': 'progress',
                        'data': progress_dict
                    }))
                else:
                    # If no progress tracking available, send empty state
                    ws.send(json.dumps({
                        'type': 'progress',
                        'data': {
                            'agents': [],
                            'overall_progress': 0,
                            'completed_agents': 0,
                            'total_agents': 0
                        }
                    }))
            except Exception as e:
                logger.error(f"Error sending progress: {e}")
                # Send empty state on error
                ws.send(json.dumps({
                    'type': 'progress',
                    'data': {
                        'agents': [],
                        'overall_progress': 0,
                        'completed_agents': 0,
                        'total_agents': 0
                    }
                }))

            # Send updates every 500ms
            import time
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if ws in websocket_clients:
            websocket_clients.remove(ws)


def broadcast_progress(progress_data):
    """Broadcast progress to all connected WebSocket clients."""
    dead_clients = []
    for client in websocket_clients:
        try:
            client.send(json.dumps(progress_data))
        except:
            dead_clients.append(client)
    
    # Remove dead connections
    for client in dead_clients:
        websocket_clients.remove(client)


# ============================================================================
# CORE ENDPOINTS
# ============================================================================

def load_all_leads():
    """Load all lead JSON files from output directory."""
    leads = []
    json_files = glob.glob(str(LEADS_DIR / 'lead_*.json'))
    
    for filepath in json_files:
        try:
            with open(filepath, 'r') as f:
                lead = json.load(f)
                # Add filepath for reference
                lead['_filepath'] = filepath
                leads.append(lead)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    
    # Sort by created timestamp (newest first)
    leads.sort(key=lambda x: x.get('created_timestamp', ''), reverse=True)
    return leads


def get_lead_stats(leads):
    """Calculate statistics from leads."""
    total = len(leads)
    if total == 0:
        return {
            'total': 0,
            'tier_1': 0,
            'tier_2': 0,
            'tier_3': 0,
            'tier_4': 0,
            'tier_5': 0,
            'avg_score': 0,
            'high_priority': 0,
            'by_industry': {},
            'by_status': {}
        }
    
    tier_1 = sum(1 for l in leads if l.get('lead_scoring', {}).get('tier') == 'TIER 1')
    tier_2 = sum(1 for l in leads if l.get('lead_scoring', {}).get('tier') == 'TIER 2')
    tier_3 = sum(1 for l in leads if l.get('lead_scoring', {}).get('tier') == 'TIER 3')
    tier_4 = sum(1 for l in leads if l.get('lead_scoring', {}).get('tier') == 'TIER 4')
    tier_5 = sum(1 for l in leads if l.get('lead_scoring', {}).get('tier') == 'TIER 5')
    
    scores = [l.get('lead_scoring', {}).get('final_score', 0) for l in leads]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    high_priority = tier_1 + tier_2
    
    # By industry
    by_industry = {}
    for lead in leads:
        industry = lead.get('business_signals', {}).get('industry', 'Unknown')
        by_industry[industry] = by_industry.get(industry, 0) + 1
    
    # By status
    by_status = {}
    for lead in leads:
        status = lead.get('outcome_tracking', {}).get('status', 'unknown')
        by_status[status] = by_status.get(status, 0) + 1
    
    return {
        'total': total,
        'tier_1': tier_1,
        'tier_2': tier_2,
        'tier_3': tier_3,
        'tier_4': tier_4,
        'tier_5': tier_5,
        'avg_score': round(avg_score, 1),
        'high_priority': high_priority,
        'by_industry': by_industry,
        'by_status': by_status
    }


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')


@app.route('/clients')
def clients_page():
    """Clients management page."""
    return render_template('clients.html')


@app.route('/api/leads')
def api_leads():
    """API endpoint to get all leads."""
    tier_filter = request.args.get('tier', None)
    status_filter = request.args.get('status', None)
    industry_filter = request.args.get('industry', None)
    
    leads = load_all_leads()
    
    # Apply filters
    if tier_filter:
        leads = [l for l in leads if l.get('lead_scoring', {}).get('tier') == tier_filter]
    
    if status_filter:
        leads = [l for l in leads if l.get('outcome_tracking', {}).get('status') == status_filter]
    
    if industry_filter:
        leads = [l for l in leads if l.get('business_signals', {}).get('industry') == industry_filter]
    
    return jsonify({
        'leads': leads,
        'count': len(leads)
    })


@app.route('/api/stats')
def api_stats():
    """API endpoint to get prospect statistics for dashboard."""
    try:
        # Load prospects from output directory
        prospects_dir = Path('output')
        prospect_files = list(prospects_dir.glob('prospects_*.json'))

        all_prospects = []

        # Load the most recent prospects file
        if prospect_files:
            prospect_files.sort(reverse=True)
            latest_file = prospect_files[0]
            try:
                with open(latest_file, 'r') as f:
                    prospects_data = json.load(f)
                    if isinstance(prospects_data, list):
                        all_prospects = prospects_data
                    elif isinstance(prospects_data, dict) and 'prospects' in prospects_data:
                        all_prospects = prospects_data['prospects']
            except Exception as e:
                logger.error(f"Error loading prospects: {e}")

        # If no prospects, try batch_results
        if not all_prospects:
            batch_dir = Path('output/batch_results')
            if batch_dir.exists():
                batch_files = list(batch_dir.glob('batch_prospects_*.json'))
                if batch_files:
                    batch_files.sort(reverse=True)
                    try:
                        with open(batch_files[0], 'r') as f:
                            batch_data = json.load(f)
                            if isinstance(batch_data, list):
                                all_prospects = batch_data
                    except Exception as e:
                        logger.error(f"Error loading batch: {e}")

        # Calculate stats in the format dashboard expects
        total_prospects = len(all_prospects)

        if total_prospects == 0:
            return jsonify({
                'total_prospects': 0,
                'urgent': 0,
                'high': 0,
                'avg_score': 0
            })

        # Count by priority tier (dashboard expects: urgent, high)
        urgent_count = sum(1 for p in all_prospects if p.get('priority_tier', '').lower() in ['urgent', 'tier 1', 'hot'])
        high_count = sum(1 for p in all_prospects if p.get('priority_tier', '').lower() in ['high', 'tier 2', 'qualified'])

        # Calculate average score
        scores = [p.get('lead_score', 0) for p in all_prospects if 'lead_score' in p]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 0

        return jsonify({
            'total_prospects': total_prospects,
            'urgent': urgent_count,
            'high': high_count,
            'avg_score': avg_score
        })

    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        return jsonify({
            'total_prospects': 0,
            'urgent': 0,
            'high': 0,
            'avg_score': 0
        })


@app.route('/api/lead/<lead_id>')
def api_lead_detail(lead_id):
    """API endpoint to get single lead details."""
    leads = load_all_leads()
    lead = next((l for l in leads if l.get('lead_id') == lead_id), None)
    
    if lead:
        return jsonify(lead)
    else:
        return jsonify({'error': 'Lead not found'}), 404


@app.route('/api/lead/<lead_id>/update', methods=['POST'])
def api_update_lead(lead_id):
    """API endpoint to update lead status/notes."""
    leads = load_all_leads()
    lead = next((l for l in leads if l.get('lead_id') == lead_id), None)
    
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    
    data = request.json
    
    # Update outcome tracking
    if 'status' in data:
        lead['outcome_tracking']['status'] = data['status']
    
    if 'notes' in data:
        if not isinstance(lead['outcome_tracking']['notes'], list):
            lead['outcome_tracking']['notes'] = []
        lead['outcome_tracking']['notes'].append({
            'text': data['notes'],
            'timestamp': datetime.utcnow().isoformat()
        })
    
    if 'contact_attempts' in data:
        lead['outcome_tracking']['contact_attempts'] = data['contact_attempts']
    
    if 'last_contact_date' in data:
        lead['outcome_tracking']['last_contact_date'] = data['last_contact_date']
    
    lead['last_updated'] = datetime.utcnow().isoformat()
    
    # Save back to file
    filepath = lead.get('_filepath')
    if filepath:
        with open(filepath, 'w') as f:
            # Remove _filepath before saving
            save_lead = {k: v for k, v in lead.items() if k != '_filepath'}
            json.dump(save_lead, f, indent=2)
    
    return jsonify({'success': True, 'lead': lead})


@app.route('/api/analyze', methods=['POST'])
def api_analyze_posting():
    """API endpoint to analyze a new job posting."""
    data = request.json
    posting_text = data.get('posting_text', '')
    posting_url = data.get('posting_url', '')
    company_name = data.get('company_name', '')
    job_title = data.get('job_title', '')

    if not posting_text:
        return jsonify({'error': 'posting_text is required'}), 400

    try:
        agent = LeadAnalysisAgent()
        result = agent.analyze_posting(
            posting_text=posting_text,
            posting_url=posting_url,
            enable_web_search=False,
            company_name=company_name,
            job_title=job_title
        )
        
        # Generate summary for next agent
        summary = generate_lead_summary(result)
        
        # Save to file
        lead_id = result['lead_id']
        company_name = result.get('company', {}).get('name', 'unknown')
        company_slug = company_name.lower().replace(' ', '_').replace('.', '')[:30]
        
        json_filename = f"lead_{company_slug}_{lead_id[:8]}.json"
        json_path = LEADS_DIR / json_filename
        
        with open(json_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Save summary
        md_filename = f"lead_{company_slug}_{lead_id[:8]}_summary.md"
        md_path = LEADS_DIR / md_filename
        
        with open(md_path, 'w') as f:
            f.write(summary)
        
        return jsonify({
            'success': True,
            'lead': result,
            'summary': summary,
            'saved_to': str(json_path)
        })
    
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def generate_lead_summary(analysis: Dict[str, Any]) -> str:
    """Generate a markdown summary from lead analysis."""
    company = analysis.get('company', {})
    job_details = analysis.get('job_details', {})
    scoring = analysis.get('lead_scoring', {})
    outreach = analysis.get('outreach_strategy', {})
    business_signals = analysis.get('business_signals', {})
    
    summary = f"""# Lead Analysis Summary

## Company Information
- **Name:** {company.get('name', 'Unknown')}
- **Industry:** {business_signals.get('industry') or company.get('industry', 'Unknown')}
- **Location:** {company.get('location', 'Unknown')}
- **Website:** {company.get('website', 'N/A')}

## Qualification Score
- **Overall Score:** {scoring.get('total_score', 0)}/100
- **Tier:** {scoring.get('tier', 'N/A')}
- **Final Score:** {scoring.get('final_score', scoring.get('total_score', 0))}

## Job Details
- **Title:** {job_details.get('title', 'N/A')}
- **Location:** {job_details.get('location', 'N/A')}
- **URL:** {job_details.get('url', 'N/A')}

### Required Skills
{chr(10).join(f'- {skill}' for skill in job_details.get('skills_required', [])) or '- None identified'}

### Pain Points Identified
{chr(10).join(f'- {pain}' for pain in job_details.get('pain_points', [])) or '- None identified'}

## Outreach Strategy

### Email Template
```
{outreach.get('email_template', 'No email template generated')}
```

### Call Script
```
{outreach.get('call_script', 'No call script generated')}
```

## Analysis Metadata
- **Analyzed At:** {analysis.get('analysis_metadata', {}).get('analyzed_at', 'N/A')}
- **Lead ID:** {analysis.get('lead_id', 'N/A')}
"""
    
    return summary


@app.route('/api/add-client', methods=['POST'])
def api_add_client():
    """Add a qualified lead as a client to the database."""
    data = request.json
    
    # Required fields
    company_name = data.get('company_name')
    tier = data.get('tier')
    score = data.get('score', 0)
    
    if not company_name or not tier:
        return jsonify({
            'success': False,
            'error': 'company_name and tier are required'
        }), 400
    
    try:
        # Generate client ID
        from datetime import datetime
        import uuid
        
        client_id = str(uuid.uuid4())
        added_date = datetime.now()
        
        # Prepare client data
        client_data = {
            'client_id': client_id,
            'company_name': company_name,
            'industry': data.get('industry'),
            'location': data.get('location'),
            'tier': tier,
            'score': score,
            'qualification_reason': data.get('qualification_reason'),
            'pain_points': data.get('pain_points', []),
            'growth_indicators': data.get('growth_indicators', []),
            'value_proposition': data.get('value_prop'),
            'job_count': data.get('job_count', 0),
            'source_url': data.get('url'),
            'source_description': data.get('description'),
            'email_draft': data.get('email_draft'),
            'call_script': data.get('call_script'),
            'outreach_status': 'NEW',
            'added_by': 'dashboard_user',
            'added_date': added_date.isoformat(),
            'notes': data.get('notes', '')
        }
        
        # Save to clients directory
        clients_dir = Path('data/clients')
        clients_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename from company name
        company_slug = company_name.lower().replace(' ', '_').replace('.', '').replace('/', '_').replace('\\', '_')[:30]
        client_file = clients_dir / f"client_{company_slug}_{client_id[:8]}.json"
        
        # Save client data
        with open(client_file, 'w') as f:
            json.dump(client_data, f, indent=2)
        
        # Also append to all_clients.json for easy listing
        all_clients_file = clients_dir / 'all_clients.json'
        all_clients = []
        
        if all_clients_file.exists():
            with open(all_clients_file, 'r') as f:
                all_clients = json.load(f)
        
        # Add summary entry
        all_clients.append({
            'client_id': client_id,
            'company_name': company_name,
            'tier': tier,
            'score': score,
            'added_date': added_date.isoformat(),
            'file': str(client_file)
        })
        
        with open(all_clients_file, 'w') as f:
            json.dump(all_clients, f, indent=2)
        
        logger.info(f"✅ Added client: {company_name} (ID: {client_id}, Tier: {tier})")
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'company_name': company_name,
            'tier': tier,
            'added_date': added_date.isoformat(),
            'message': f'Successfully added {company_name} as a {tier} client!',
            'file': str(client_file)
        })
            
    except Exception as e:
        logger.error(f"Error adding client: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clients')
def api_get_clients():
    """API endpoint to get all clients."""
    try:
        clients_dir = Path('data/clients')
        all_clients_file = clients_dir / 'all_clients.json'

        if not all_clients_file.exists():
            return jsonify({'success': True, 'clients': []})

        with open(all_clients_file, 'r') as f:
            clients = json.load(f)

        # Load full client details for each
        detailed_clients = []
        for client_summary in clients:
            client_file = Path(client_summary['file'])
            if client_file.exists():
                with open(client_file, 'r') as f:
                    client_data = json.load(f)
                    detailed_clients.append(client_data)

        return jsonify({
            'success': True,
            'clients': detailed_clients
        })

    except Exception as e:
        logger.error(f"Error fetching clients: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clients/clear', methods=['POST'])
def api_clear_clients():
    """Clear all client data."""
    try:
        clients_dir = Path('data/clients')
        
        # Delete all client files
        deleted_count = 0
        for client_file in clients_dir.glob('client_*.json'):
            client_file.unlink()
            deleted_count += 1
        
        # Delete all_clients.json
        all_clients_file = clients_dir / 'all_clients.json'
        if all_clients_file.exists():
            all_clients_file.unlink()
        
        logger.info(f"Cleared {deleted_count} client files")
        
        return jsonify({
            'success': True,
            'message': f'Cleared {deleted_count} clients',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        logger.error(f"Error clearing clients: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/industries')
def api_industries():
    """Get list of all industries."""
    leads = load_all_leads()
    industries = set()
    for lead in leads:
        industry = lead.get('business_signals', {}).get('industry')
        if industry:
            industries.add(industry)
    
    return jsonify(sorted(list(industries)))


@app.route('/api/export/csv')
def api_export_csv():
    """Export leads to CSV."""
    import csv
    import io
    
    leads = load_all_leads()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Lead ID', 'Company Name', 'Location', 'Industry', 'Tier', 'Score',
        'Status', 'Phone', 'Email', 'Website', 'Created', 'Pain Points'
    ])
    
    # Rows
    for lead in leads:
        company = lead.get('company', {})
        scoring = lead.get('lead_scoring', {})
        tracking = lead.get('outcome_tracking', {})
        signals = lead.get('business_signals', {})
        needs = lead.get('needs_analysis', {})
        
        pain_points = ', '.join([
            p.get('pain_category', '') 
            for p in needs.get('primary_pain_points', [])
        ])
        
        writer.writerow([
            lead.get('lead_id', ''),
            company.get('name', ''),
            company.get('location', ''),
            signals.get('industry', ''),
            scoring.get('tier', ''),
            scoring.get('final_score', 0),
            tracking.get('status', ''),
            company.get('contact', {}).get('phone', ''),
            company.get('contact', {}).get('email', ''),
            company.get('contact', {}).get('website', ''),
            lead.get('created_timestamp', ''),
            pain_points
        ])
    
    output.seek(0)
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=leads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    }


@app.route('/api/ping', methods=['GET', 'POST'])
def api_ping():
    """Simple endpoint to test server is responding."""
    print("PING ENDPOINT HIT!")
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200


@app.route('/api/craigslist/locations/flat', methods=['GET'])
def api_craigslist_locations():
    """Get all Craigslist locations/cities."""
    try:
        # Comprehensive list of major US Craigslist cities
        locations = [
            # California
            {"code": "sfbay", "name": "San Francisco Bay Area", "state": "California", "country": "USA"},
            {"code": "losangeles", "name": "Los Angeles", "state": "California", "country": "USA"},
            {"code": "sandiego", "name": "San Diego", "state": "California", "country": "USA"},
            {"code": "sacramento", "name": "Sacramento", "state": "California", "country": "USA"},
            {"code": "fresno", "name": "Fresno", "state": "California", "country": "USA"},
            {"code": "bakersfield", "name": "Bakersfield", "state": "California", "country": "USA"},
            {"code": "orangecounty", "name": "Orange County", "state": "California", "country": "USA"},
            {"code": "inlandempire", "name": "Inland Empire", "state": "California", "country": "USA"},
            {"code": "santabarbara", "name": "Santa Barbara", "state": "California", "country": "USA"},
            {"code": "sandiego", "name": "San Diego", "state": "California", "country": "USA"},
            
            # Texas
            {"code": "austin", "name": "Austin", "state": "Texas", "country": "USA"},
            {"code": "dallas", "name": "Dallas", "state": "Texas", "country": "USA"},
            {"code": "houston", "name": "Houston", "state": "Texas", "country": "USA"},
            {"code": "sanantonio", "name": "San Antonio", "state": "Texas", "country": "USA"},
            {"code": "elpaso", "name": "El Paso", "state": "Texas", "country": "USA"},
            
            # Florida
            {"code": "miami", "name": "Miami", "state": "Florida", "country": "USA"},
            {"code": "tampa", "name": "Tampa Bay", "state": "Florida", "country": "USA"},
            {"code": "orlando", "name": "Orlando", "state": "Florida", "country": "USA"},
            {"code": "jacksonville", "name": "Jacksonville", "state": "Florida", "country": "USA"},
            {"code": "fortlauderdale", "name": "Fort Lauderdale", "state": "Florida", "country": "USA"},
            
            # New York
            {"code": "newyork", "name": "New York City", "state": "New York", "country": "USA"},
            {"code": "buffalo", "name": "Buffalo", "state": "New York", "country": "USA"},
            {"code": "rochester", "name": "Rochester", "state": "New York", "country": "USA"},
            {"code": "albany", "name": "Albany", "state": "New York", "country": "USA"},
            {"code": "longisland", "name": "Long Island", "state": "New York", "country": "USA"},
            
            # Illinois
            {"code": "chicago", "name": "Chicago", "state": "Illinois", "country": "USA"},
            {"code": "peoria", "name": "Peoria", "state": "Illinois", "country": "USA"},
            
            # Pennsylvania
            {"code": "philadelphia", "name": "Philadelphia", "state": "Pennsylvania", "country": "USA"},
            {"code": "pittsburgh", "name": "Pittsburgh", "state": "Pennsylvania", "country": "USA"},
            
            # Washington
            {"code": "seattle", "name": "Seattle", "state": "Washington", "country": "USA"},
            {"code": "spokane", "name": "Spokane", "state": "Washington", "country": "USA"},
            
            # Oregon
            {"code": "portland", "name": "Portland", "state": "Oregon", "country": "USA"},
            {"code": "eugene", "name": "Eugene", "state": "Oregon", "country": "USA"},
            
            # Arizona
            {"code": "phoenix", "name": "Phoenix", "state": "Arizona", "country": "USA"},
            {"code": "tucson", "name": "Tucson", "state": "Arizona", "country": "USA"},
            
            # Colorado
            {"code": "denver", "name": "Denver", "state": "Colorado", "country": "USA"},
            {"code": "boulder", "name": "Boulder", "state": "Colorado", "country": "USA"},
            
            # Massachusetts
            {"code": "boston", "name": "Boston", "state": "Massachusetts", "country": "USA"},
            
            # Nevada
            {"code": "lasvegas", "name": "Las Vegas", "state": "Nevada", "country": "USA"},
            {"code": "reno", "name": "Reno", "state": "Nevada", "country": "USA"},
            
            # Georgia
            {"code": "atlanta", "name": "Atlanta", "state": "Georgia", "country": "USA"},
            
            # North Carolina
            {"code": "raleigh", "name": "Raleigh", "state": "North Carolina", "country": "USA"},
            {"code": "charlotte", "name": "Charlotte", "state": "North Carolina", "country": "USA"},
            
            # Michigan
            {"code": "detroit", "name": "Detroit", "state": "Michigan", "country": "USA"},
            
            # Minnesota
            {"code": "minneapolis", "name": "Minneapolis", "state": "Minnesota", "country": "USA"},
            
            # Missouri
            {"code": "stlouis", "name": "St. Louis", "state": "Missouri", "country": "USA"},
            {"code": "kansascity", "name": "Kansas City", "state": "Missouri", "country": "USA"},
            
            # Ohio
            {"code": "cleveland", "name": "Cleveland", "state": "Ohio", "country": "USA"},
            {"code": "columbus", "name": "Columbus", "state": "Ohio", "country": "USA"},
            {"code": "cincinnati", "name": "Cincinnati", "state": "Ohio", "country": "USA"},
        ]
        
        return jsonify({'success': True, 'locations': locations})
        
    except Exception as e:
        logger.error(f"Error loading locations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/craigslist/categories', methods=['GET'])
def api_craigslist_categories():
    """Get all Craigslist job categories."""
    try:
        # Craigslist job categories
        categories = [
            {"code": "jjj", "name": "All Jobs (No Filter)"},  # Special option to search all jobs
            {"code": "acc", "name": "Accounting / Finance"},
            {"code": "ofc", "name": "Admin / Office"},
            {"code": "egr", "name": "Architect / Engineering / CAD"},
            {"code": "med", "name": "Art / Media / Design"},
            {"code": "sci", "name": "Biotech / Science"},
            {"code": "bus", "name": "Business / Management"},
            {"code": "csr", "name": "Customer Service"},
            {"code": "edu", "name": "Education / Teaching"},
            {"code": "fbh", "name": "Food / Beverage / Hospitality"},
            {"code": "lab", "name": "General Labor"},
            {"code": "gov", "name": "Government"},
            {"code": "hea", "name": "Human Resources"},
            {"code": "hum", "name": "Human Services"},
            {"code": "lgl", "name": "Legal / Paralegal"},
            {"code": "mfg", "name": "Manufacturing"},
            {"code": "mar", "name": "Marketing / Advertising / PR"},
            {"code": "him", "name": "Medical / Health"},
            {"code": "npo", "name": "Nonprofit / Volunteer"},
            {"code": "rej", "name": "Real Estate"},
            {"code": "ret", "name": "Retail / Wholesale"},
            {"code": "sls", "name": "Sales"},
            {"code": "spa", "name": "Salon / Spa / Fitness"},
            {"code": "sec", "name": "Security"},
            {"code": "trd", "name": "Skilled Trade / Craft"},
            {"code": "sof", "name": "Software / QA / DBA / etc"},
            {"code": "sad", "name": "Systems / Networking"},
            {"code": "tch", "name": "Technical Support"},
            {"code": "trp", "name": "Transport"},
            {"code": "tfr", "name": "TV / Film / Video / Radio"},
            {"code": "web", "name": "Web / Info Design"},
            {"code": "wri", "name": "Writing / Editing"},
        ]
        
        return jsonify({'success': True, 'categories': categories})
        
    except Exception as e:
        logger.error(f"Error loading categories: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/prospects', methods=['GET'])
def api_prospects():
    """Get prospects from recent scraping results."""
    try:
        city = request.args.get('city')
        category = request.args.get('category')

        # Load prospects from output/prospects_*.json files (not output/leads/)
        prospects_dir = Path('output')
        prospect_files = list(prospects_dir.glob('prospects_*.json'))

        all_prospects = []

        # Load the most recent prospects file
        if prospect_files:
            # Sort by filename (timestamp) and get latest
            prospect_files.sort(reverse=True)
            latest_file = prospect_files[0]

            try:
                with open(latest_file, 'r') as f:
                    prospects_data = json.load(f)
                    # Handle both list and dict formats
                    if isinstance(prospects_data, list):
                        all_prospects = prospects_data
                    elif isinstance(prospects_data, dict) and 'prospects' in prospects_data:
                        all_prospects = prospects_data['prospects']
            except Exception as e:
                logger.error(f"Error loading prospects file {latest_file}: {e}")

        # If no prospects files found, try loading from batch_results
        if not all_prospects:
            batch_dir = Path('output/batch_results')
            if batch_dir.exists():
                batch_files = list(batch_dir.glob('batch_prospects_*.json'))
                if batch_files:
                    batch_files.sort(reverse=True)
                    latest_batch = batch_files[0]
                    try:
                        with open(latest_batch, 'r') as f:
                            batch_data = json.load(f)
                            if isinstance(batch_data, list):
                                all_prospects = batch_data
                            elif isinstance(batch_data, dict) and 'prospects' in batch_data:
                                all_prospects = batch_data['prospects']
                    except Exception as e:
                        logger.error(f"Error loading batch file {latest_batch}: {e}")

        # Filter by city/category if provided
        if city or category:
            filtered = []
            for prospect in all_prospects:
                match = True
                # Check in various possible locations
                prospect_location = prospect.get('location', '') or prospect.get('company_profile', {}).get('location', '')
                prospect_category = prospect.get('category', '')

                if city and city.lower() not in prospect_location.lower():
                    match = False
                if category and category.lower() != prospect_category.lower():
                    match = False
                if match:
                    filtered.append(prospect)
            all_prospects = filtered

        return jsonify({
            'success': True,
            'prospects': all_prospects,
            'total': len(all_prospects)
        })

    except Exception as e:
        logger.error(f"Error loading prospects: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e), 'prospects': []}, 500)


@app.route('/api/scrape', methods=['POST'])
def api_scrape_jobs():
    """
    NEW: Signal-based growth detection endpoint.
    
    Scrapes Craigslist for job signals → finds companies externally → scores growth.
    Returns discovered companies (NOT direct Craigslist leads).
    """
    logger.info("=== SIGNAL-BASED SCRAPE ENDPOINT HIT ===")

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
        max_jobs = data.get('max_jobs', 50)  # Max signals to extract

        logger.info(f"Running signal-based pipeline: {city}/{category}, max_pages={max_pages}, max_signals={max_jobs}")

        # Run the NEW signal-based orchestrator pipeline
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
                'jobs': [],
                'companies': [],
                'signals': []
            }), 200

        # Extract NEW data: signals and scored companies
        signals = result.get('signals', [])
        companies = result.get('companies', [])
        top_companies = result.get('top_companies', [])
        stats = result.get('stats', {})

        logger.info(f"Pipeline completed: {len(signals)} signals, {len(companies)} companies found, {len(top_companies)} high-growth")

        # Convert signals to dashboard display format (show as jobs for reference)
        dashboard_jobs = []
        for signal in signals[:30]:  # Show first 30 signals
            dashboard_jobs.append({
                'title': signal.get('job_title', 'Unknown'),
                'url': signal.get('job_url', ''),
                'location': signal.get('location', 'Unknown'),
                'date': signal.get('posted_date', 'Recent'),
                'compensation': '',
                'company': f"[SIGNAL] {signal.get('industry', 'Unknown')} - {signal.get('job_category', 'Unknown')}",
                'tier': 'SIGNAL',
                'score': 0,
                'description': f"Industry: {signal.get('industry')}, Category: {signal.get('job_category')}, Seniority: {signal.get('seniority_level')}, Urgency: {signal.get('urgency_level')}",
                'pain_points': signal.get('growth_indicators', []),
                'job_count': signal.get('num_roles', 1),
                'growth_stage': signal.get('industry', 'Unknown'),
                'is_signal': True
            })

        # Convert scored companies to dashboard format
        company_entries = []
        for company in top_companies:
            company_entries.append({
                'title': f"{company.get('company_name', 'Unknown')} - Growth Score: {company.get('growth_score', 0):.1f}",
                'url': company.get('website', ''),
                'location': company.get('location', 'Unknown'),
                'date': 'Discovered Externally',
                'compensation': '',
                'company': company.get('company_name', 'Unknown'),
                'tier': 'TIER 1' if company.get('growth_score', 0) >= 70 else 'TIER 2' if company.get('growth_score', 0) >= 50 else 'TIER 3',
                'score': company.get('growth_score', 0),
                'description': f"Industry: {company.get('industry')}, Source: {company.get('source')}",
                'pain_points': [],
                'job_count': company.get('signals', {}).get('hiring_velocity', {}).get('open_positions', 0),
                'growth_stage': company.get('industry', 'Unknown'),
                'is_company': True,
                'growth_signals': company.get('signals', {})
            })

        # Combine: Show companies first, then signals
        all_results = company_entries + dashboard_jobs

        logger.info(f"Returning {len(all_results)} items: {len(company_entries)} companies + {len(dashboard_jobs)} signals")

        return jsonify({
            'success': True,
            'jobs': all_results,  # Legacy name for compatibility
            'companies': company_entries,
            'signals': dashboard_jobs,
            'stats': {
                **stats,
                'total_results': len(all_results),
                'high_growth_companies': len(company_entries)
            }
        }), 200

    except Exception as e:
        logger.error(f"Scrape endpoint error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e), 'jobs': [], 'companies': [], 'signals': []}), 500
                'score': int(lead_score),
                'qualification_score': int(lead_score),
                'qualification_reason': f"{priority} - Score: {lead_score:.1f}/100. Growth stage: {growth_stage}",
                'pain_points': pain_points_list,
                'value_prop': f"{len(job_postings)} jobs posted. Growth score: {growth_score:.2f}",
                'description': first_job_description[:500] if first_job_description else company_name,
                'job_count': len(job_postings),
                'growth_indicators': [growth_stage]
            })

        logger.info(f"Converted {len(prospects)} prospects to {len(dashboard_jobs)} dashboard jobs")
        if dashboard_jobs:
            logger.info(f"Sample dashboard job: {list(dashboard_jobs[0].keys())}")

        # Extract stats
        phase_1_stats = stats.get('phase_1', {}) if stats else {}
        jobs_scanned = phase_1_stats.get('jobs_scanned', 0)

        return jsonify({
            'success': True,
            'jobs': dashboard_jobs,
            'total_scraped': jobs_scanned,
            'qualified_count': len(dashboard_jobs),
            'pages_scraped': max_pages,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"ERROR in scrape: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 200



@app.route('/api/scrape-single', methods=['POST'])
def api_scrape_single_job():
    """Scrape a single job's full details."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    try:
        job = scraper_agent.scrape_single_job(url)
        
        if job:
            return jsonify({
                'success': True,
                'job': {
                    'title': job.title,
                    'description': job.description,
                    'url': job.url,
                    'location': job.location,
                    'compensation': getattr(job, 'compensation', '')
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to scrape job'}), 500
            
    except Exception as e:
        logger.error(f"Single scrape error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PARSER AGENT ENDPOINTS
# ============================================================================

@app.route('/api/parse', methods=['POST'])
def api_parse_job():
    """Parse a job posting."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    job_text = data.get('job_text', '')
    
    if not job_text:
        return jsonify({'error': 'job_text is required'}), 400
    
    try:
        from models import RawJobPosting
        raw_job = RawJobPosting(
            title=data.get('title', 'Unknown'),
            url=data.get('url', ''),
            description=job_text,
            location=data.get('location', ''),
            category=data.get('category', ''),
            posted_date=datetime.now()
        )
        
        parsed_job = parser_agent.parse_job(raw_job, use_ai=True)
        
        return jsonify({
            'success': True,
            'parsed_job': {
                'title': parsed_job.title,
                'skills': parsed_job.skills,
                'pain_points': parsed_job.pain_points,
                'salary_min': parsed_job.salary_min,
                'salary_max': parsed_job.salary_max,
                'is_remote': parsed_job.is_remote,
                'is_hybrid': parsed_job.is_hybrid
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VECTOR SEARCH ENDPOINTS
# ============================================================================

@app.route('/api/vector/search', methods=['POST'])
def api_vector_search():
    """Search jobs using vector similarity."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    query = data.get('query', '')
    top_k = data.get('top_k', 5)
    
    if not query:
        return jsonify({'error': 'query is required'}), 400
    
    try:
        results = vector_agent.search_similar_jobs(query, top_k=top_k)
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# DATABASE QUERY ENDPOINTS
# ============================================================================

@app.route('/api/database/search', methods=['POST'])
def api_database_search():
    """Search jobs in database."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    keywords = data.get('keywords', [])
    location = data.get('location', None)
    min_salary = data.get('min_salary', None)
    is_remote = data.get('is_remote', None)
    limit = data.get('limit', 10)
    
    try:
        from models import SearchQuery
        query = SearchQuery(
            keywords=keywords,
            location=location,
            min_salary=min_salary,
            is_remote=is_remote,
            limit=limit
        )
        
        results = database_agent.search_jobs(query)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'jobs': [
                {
                    'title': job.title,
                    'company': getattr(job, 'company', 'Unknown'),
                    'location': job.location,
                    'salary_min': job.salary_min,
                    'salary_max': job.salary_max,
                    'skills': job.skills
                }
                for job in results
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/database/stats', methods=['GET'])
def api_database_stats():
    """Get database statistics."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    try:
        stats = database_agent.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RAG INTEGRATION ENDPOINTS
# ============================================================================

@app.route('/api/rag/query', methods=['POST'])
def api_rag_query():
    """Query using RAG (Retrieval Augmented Generation)."""
    if not RAG_AVAILABLE:
        return jsonify({'error': 'RAG integration not available'}), 503
    
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'question is required'}), 400
    
    try:
        answer = rag_integration.query(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FULL PIPELINE ENDPOINT
# ============================================================================

@app.route('/api/pipeline/run', methods=['POST'])
def api_run_pipeline():
    """Run the full scraping and analysis pipeline."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    city = data.get('city', 'sfbay')
    category = data.get('category', 'sof')
    keywords = data.get('keywords', [])
    max_pages = data.get('max_pages', 1)
    
    try:
        result = orchestrator.run_pipeline(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages
        )
        
        return jsonify({
            'success': True,
            'jobs_scraped': result.get('jobs_scraped', 0),
            'jobs_parsed': result.get('jobs_parsed', 0),
            'jobs_stored': result.get('jobs_stored', 0),
            'summary': result.get('summary', {})
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pipeline/analyze-and-qualify', methods=['POST'])
def api_pipeline_analyze_and_qualify():
    """Run scraping + lead qualification pipeline."""
    if not init_agents():
        return jsonify({'error': 'Failed to initialize agents'}), 500
    
    data = request.json
    city = data.get('city', 'sfbay')
    category = data.get('category', 'sof')
    keywords = data.get('keywords', [])
    max_pages = data.get('max_pages', 1)
    
    try:
        # Step 1: Scrape jobs
        from models import ScraperConfig
        config = ScraperConfig(
            city=city,
            category=category,
            keywords=keywords,
            max_pages=max_pages
        )
        scraper_agent.config = config
        raw_jobs = scraper_agent.scrape_listings(keywords=keywords)
        
        # Step 2: Analyze each job as a lead
        lead_agent = LeadAnalysisAgent()
        qualified_leads = []
        
        for raw_job in raw_jobs:
            try:
                lead_result = lead_agent.analyze_posting(
                    posting_text=raw_job.description,
                    posting_url=raw_job.url,
                    enable_web_search=False
                )
                
                # Only keep TIER 1-2 leads
                if lead_result['lead_scoring']['tier'] in ['TIER 1', 'TIER 2']:
                    # Save to file
                    lead_id = lead_result['lead_id']
                    company_name = lead_result.get('company', {}).get('name', 'unknown')
                    company_slug = company_name.lower().replace(' ', '_').replace('.', '')[:30]
                    
                    json_filename = f"lead_{company_slug}_{lead_id[:8]}.json"
                    json_path = LEADS_DIR / json_filename
                    
                    with open(json_path, 'w') as f:
                        json.dump(lead_result, f, indent=2)
                    
                    qualified_leads.append({
                        'company': company_name,
                        'tier': lead_result['lead_scoring']['tier'],
                        'score': lead_result['lead_scoring']['final_score']
                    })
            except Exception as e:
                print(f"Error analyzing job {raw_job.title}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'jobs_scraped': len(raw_jobs),
            'qualified_leads': len(qualified_leads),
            'leads': qualified_leads
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# AGENT STATUS ENDPOINT
# ============================================================================

@app.route('/api/agents/status')
def api_agents_status():
    """Get status of all agents with detailed information."""
    return jsonify({
        'agents': {
            # Core Agents
            'client_agent': {
                'initialized': client_agent is not None,
                'category': 'core',
                'description': 'Manages client data and configurations',
                'emoji': '👤'
            },
            'scraper_agent': {
                'initialized': scraper_agent is not None,
                'category': 'core',
                'description': 'Scrapes job postings from Craigslist',
                'emoji': '🔍'
            },
            'parser_agent': {
                'initialized': parser_agent is not None,
                'category': 'core',
                'description': 'Extracts structured data from job postings',
                'emoji': '📝'
            },
            'quick_filter_agent': {
                'initialized': True,
                'category': 'core',
                'description': 'Fast filtering of job postings',
                'emoji': '⚡'
            },
            'enhanced_company_scoring_agent': {
                'initialized': True,
                'category': 'core',
                'description': 'Advanced company scoring and ranking',
                'emoji': '⭐'
            },
            
            # Phase 2 Agents
            'growth_signal_analyzer_agent': {
                'initialized': True,
                'category': 'analysis',
                'description': 'Detects company growth signals',
                'emoji': '📈'
            },
            'company_research_agent': {
                'initialized': research_agent is not None,
                'category': 'analysis',
                'description': 'Deep research on companies',
                'emoji': '🔬'
            },
            'service_matcher_agent': {
                'initialized': True,
                'category': 'analysis',
                'description': 'Matches services to company needs',
                'emoji': '🎯'
            },
            'ml_scoring_agent': {
                'initialized': True,
                'category': 'analysis',
                'description': 'Machine learning-based lead scoring',
                'emoji': '🤖'
            },
            'outreach_agent': {
                'initialized': True,
                'category': 'engagement',
                'description': 'Generates personalized outreach content',
                'emoji': '📧'
            },
            
            # OpenAI Enhanced Agents
            'conversational_lead_agent': {
                'initialized': conversational_agent is not None,
                'category': 'openai',
                'description': 'Conversational State API - 58% token savings',
                'emoji': '💬',
                'feature': 'Conversation State API'
            },
            'batch_processor_agent': {
                'initialized': batch_agent is not None,
                'category': 'openai',
                'description': 'Batch API - 50% cost reduction',
                'emoji': '📦',
                'feature': 'Batch API'
            },
            'deep_research_agent': {
                'initialized': deep_research_agent is not None,
                'category': 'openai',
                'description': 'Deep Research with o3/o4-mini models',
                'emoji': '🧠',
                'feature': 'Deep Research'
            },
            'file_search_agent': {
                'initialized': True,
                'category': 'openai',
                'description': 'File search and knowledge retrieval',
                'emoji': '📚',
                'feature': 'File Search'
            },
            'visualization_agent': {
                'initialized': True,
                'category': 'openai',
                'description': 'Image generation and code interpreter',
                'emoji': '📊',
                'feature': 'Code Interpreter'
            },
        },
        'legacy_agents': {
            'lead_analysis_agent': lead_analysis_agent is not None,
            'vector_agent': vector_agent is not None,
            'database_agent': database_agent is not None,
        },
        'orchestrator': orchestrator is not None,
        'rag_available': RAG_AVAILABLE,
        'total_agents': 15,
        'initialized_count': sum([
            client_agent is not None,
            scraper_agent is not None,
            parser_agent is not None,
            research_agent is not None,
            conversational_agent is not None,
            batch_agent is not None,
            deep_research_agent is not None,
        ]) + 8  # Always-available agents
    })


# ============================================================================
# OPENAI ENHANCED AGENT ENDPOINTS
# ============================================================================

@app.route('/api/conversational/chat', methods=['POST'])
def api_conversational_chat():
    """
    Chat with a lead using Conversational State API (58% token savings).
    
    Expects JSON:
    {
        "lead_id": "abc123",
        "message": "Tell me about this opportunity",
        "conversation_id": "optional-existing-id"
    }
    """
    try:
        init_agents()
        if not conversational_agent:
            return jsonify({'success': False, 'error': 'Conversational agent not initialized'}), 500
            
        data = request.json
        lead_id = data.get('lead_id')
        message = data.get('message')
        conversation_id = data.get('conversation_id')
        
        if not lead_id or not message:
            return jsonify({'success': False, 'error': 'lead_id and message required'}), 400
        
        # Load lead data
        leads = load_all_leads()
        lead = next((l for l in leads if l.get('lead_id') == lead_id), None)
        
        if not lead:
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Chat with lead context
        result = conversational_agent.chat_about_lead(
            lead_data=lead,
            user_message=message,
            conversation_id=conversation_id
        )
        
        return jsonify({
            'success': True,
            'response': result.get('response'),
            'conversation_id': result.get('conversation_id'),
            'tokens_saved': result.get('tokens_saved', 0)
        })
        
    except Exception as e:
        logger.error(f"Conversational chat error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/submit', methods=['POST'])
def api_batch_submit():
    """
    Submit batch processing job (50% cost reduction).
    
    Expects JSON:
    {
        "lead_ids": ["id1", "id2", ...],
        "operation": "enrich" | "score" | "research",
        "priority": "low" | "normal" | "high"
    }
    """
    try:
        init_agents()
        if not batch_agent:
            return jsonify({'success': False, 'error': 'Batch agent not initialized'}), 500
            
        data = request.json
        lead_ids = data.get('lead_ids', [])
        operation = data.get('operation', 'enrich')
        priority = data.get('priority', 'normal')
        
        if not lead_ids:
            return jsonify({'success': False, 'error': 'lead_ids required'}), 400
        
        # Load leads
        all_leads = load_all_leads()
        leads_to_process = [l for l in all_leads if l.get('lead_id') in lead_ids]
        
        # Submit batch job
        batch_id = batch_agent.submit_batch(
            leads=leads_to_process,
            operation=operation,
            priority=priority
        )
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'lead_count': len(leads_to_process),
            'estimated_savings': '50%',
            'status': 'submitted'
        })
        
    except Exception as e:
        logger.error(f"Batch submit error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/status/<batch_id>', methods=['GET'])
def api_batch_status(batch_id):
    """Check status of batch processing job."""
    try:
        init_agents()
        if not batch_agent:
            return jsonify({'success': False, 'error': 'Batch agent not initialized'}), 500
        
        status = batch_agent.get_batch_status(batch_id)
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'status': status.get('status'),
            'completed': status.get('completed', 0),
            'total': status.get('total', 0),
            'progress': status.get('progress', 0)
        })
        
    except Exception as e:
        logger.error(f"Batch status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/research/deep', methods=['POST'])
def api_deep_research():
    """
    Perform deep research using o3/o4-mini models.
    
    Expects JSON:
    {
        "company_name": "TechCorp",
        "research_depth": "standard" | "comprehensive",
        "topics": ["growth", "technology", "hiring"]
    }
    """
    try:
        init_agents()
        if not deep_research_agent:
            return jsonify({'success': False, 'error': 'Deep research agent not initialized'}), 500
            
        data = request.json
        company_name = data.get('company_name')
        research_depth = data.get('research_depth', 'standard')
        topics = data.get('topics', ['general'])
        
        if not company_name:
            return jsonify({'success': False, 'error': 'company_name required'}), 400
        
        # Perform deep research
        research = deep_research_agent.research_company(
            company_name=company_name,
            depth=research_depth,
            topics=topics
        )
        
        return jsonify({
            'success': True,
            'company': company_name,
            'findings': research.get('findings'),
            'insights': research.get('insights'),
            'model': research.get('model', 'o3-mini'),
            'confidence': research.get('confidence', 0)
        })
        
    except Exception as e:
        logger.error(f"Deep research error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/filesearch/query', methods=['POST'])
def api_file_search():
    """
    Search uploaded files and knowledge base.
    
    Expects JSON:
    {
        "query": "What are the best practices for recruiting?",
        "file_ids": ["file_123", "file_456"],
        "max_results": 5
    }
    """
    try:
        data = request.json
        query = data.get('query')
        file_ids = data.get('file_ids', [])
        max_results = data.get('max_results', 5)
        
        if not query:
            return jsonify({'success': False, 'error': 'query required'}), 400
        
        # File search using FileSearchAgent (placeholder - implement based on your needs)
        results = [
            {
                'file_id': 'demo_file_1',
                'content': 'Sample search result',
                'relevance': 0.95
            }
        ]
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"File search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# VISUALIZATION ENDPOINTS (OpenAI Image Generation + Code Interpreter)
# ============================================================================

@app.route('/api/visualize/presentation', methods=['POST'])
def create_presentation():
    """
    Create a complete visual presentation package for a prospect.
    
    Expects JSON:
    {
        "company_name": "TechCorp",
        "industry": "Software",
        "job_count": 45,
        "employee_count": 500
    }
    """
    try:
        from agents import VisualizationAgent
        
        data = request.json
        company_name = data.get('company_name')
        industry = data.get('industry', 'Technology')
        job_count = data.get('job_count', 0)
        employee_count = data.get('employee_count')
        
        if not company_name:
            return jsonify({'success': False, 'error': 'company_name required'}), 400
        
        viz_agent = VisualizationAgent()
        result = viz_agent.create_prospect_presentation(
            company_name=company_name,
            industry=industry,
            job_count=job_count,
            employee_count=employee_count
        )
        
        return jsonify({
            'success': True,
            'company': result['company'],
            'assets': result['assets'],
            'output_dir': result['output_dir']
        })
        
    except Exception as e:
        logger.error(f"Presentation creation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/visualize/hiring-dashboard', methods=['POST'])
def create_hiring_dashboard():
    """
    Create a hiring patterns dashboard using Code Interpreter.
    
    Expects JSON:
    {
        "company_name": "TechCorp",
        "job_postings": [
            {"title": "...", "location": "...", "posted_date": "..."},
            ...
        ]
    }
    """
    try:
        from agents import VisualizationAgent
        
        data = request.json
        company_name = data.get('company_name')
        job_postings = data.get('job_postings', [])
        
        if not company_name or not job_postings:
            return jsonify({'success': False, 'error': 'company_name and job_postings required'}), 400
        
        viz_agent = VisualizationAgent()
        dashboard_path = viz_agent.visualize_hiring_patterns(job_postings, company_name)
        
        if dashboard_path:
            return jsonify({
                'success': True,
                'company': company_name,
                'dashboard_path': dashboard_path,
                'job_count': len(job_postings)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create dashboard'}), 500
        
    except Exception as e:
        logger.error(f"Dashboard creation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/visualize/roi', methods=['POST'])
def create_roi_visual():
    """
    Create visual ROI calculator using Code Interpreter.
    
    Expects JSON:
    {
        "company_name": "TechCorp",
        "company_size": 250,
        "avg_salary": 75000
    }
    """
    try:
        from agents import VisualizationAgent
        
        data = request.json
        company_name = data.get('company_name', 'Prospect')
        company_size = data.get('company_size', 100)
        avg_salary = data.get('avg_salary', 70000)
        
        viz_agent = VisualizationAgent()
        roi_path = viz_agent.create_roi_calculator_visual(
            company_size=company_size,
            avg_salary=avg_salary,
            company_name=company_name
        )
        
        if roi_path:
            return jsonify({
                'success': True,
                'company': company_name,
                'roi_visual_path': roi_path,
                'company_size': company_size,
                'avg_salary': avg_salary
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create ROI visual'}), 500
        
    except Exception as e:
        logger.error(f"ROI visual creation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/visualize/compare', methods=['POST'])
def create_comparison():
    """
    Create a comparison chart between two companies.
    
    Expects JSON:
    {
        "company_a": "TechCorp",
        "jobs_a": 45,
        "company_b": "StartupXYZ",
        "jobs_b": 12
    }
    """
    try:
        from agents import VisualizationAgent
        
        data = request.json
        company_a = data.get('company_a')
        jobs_a = data.get('jobs_a', 0)
        company_b = data.get('company_b')
        jobs_b = data.get('jobs_b', 0)
        
        if not company_a or not company_b:
            return jsonify({'success': False, 'error': 'Both companies required'}), 400
        
        viz_agent = VisualizationAgent()
        comparison_path = viz_agent.create_comparison_chart(
            company_a=company_a,
            jobs_a=jobs_a,
            company_b=company_b,
            jobs_b=jobs_b
        )
        
        if comparison_path:
            return jsonify({
                'success': True,
                'comparison_path': comparison_path,
                'companies': [company_a, company_b]
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create comparison'}), 500
        
    except Exception as e:
        logger.error(f"Comparison creation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/visualize/custom', methods=['POST'])
def create_custom_image():
    """
    Generate a custom image using DALL-E 3.
    
    Expects JSON:
    {
        "prompt": "Create a professional business infographic...",
        "size": "1024x1024",  // optional
        "quality": "hd"  // optional
    }
    """
    try:
        init_agents()
        
        data = request.json
        prompt = data.get('prompt')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'prompt required'}), 400
        
        result = client_agent.generate_image(prompt, size=size, quality=quality)
        
        if 'url' in result:
            return jsonify({
                'success': True,
                'image_url': result['url'],
                'revised_prompt': result.get('revised_prompt'),
                'size': size,
                'quality': quality
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')}), 500
        
    except Exception as e:
        logger.error(f"Custom image generation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# CONVERSATIONAL ANALYSIS ENDPOINTS (OpenAI Conversation State APIs)
# ============================================================================

@app.route('/api/conversation/start', methods=['POST'])
def start_conversation_analysis():
    """
    Start a multi-turn conversational analysis for a company.
    
    Expects JSON:
    {
        "company_name": "TechCorp",
        "job_count": 45,
        "industry": "Software",
        "company_size": 500,
        "avg_salary": 85000
    }
    """
    try:
        from agents import ConversationalLeadAgent
        
        data = request.json
        company_name = data.get('company_name')
        
        if not company_name:
            return jsonify({'success': False, 'error': 'company_name required'}), 400
        
        agent = ConversationalLeadAgent(create_conversation=True)
        
        initial_data = {
            'job_count': data.get('job_count', 0),
            'industry': data.get('industry', 'Unknown'),
            'company_size': data.get('company_size'),
            'avg_salary': data.get('avg_salary', 75000)
        }
        
        result = agent.start_company_analysis(company_name, initial_data)
        
        return jsonify({
            'success': True,
            'conversation_id': result['conversation_id'],
            'response_id': result['response_id'],
            'analysis': result['analysis']
        })
        
    except Exception as e:
        logger.error(f"Conversation start failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversation/ask', methods=['POST'])
def conversation_followup():
    """
    Ask a follow-up question in an existing conversation.
    
    Expects JSON:
    {
        "conversation_id": "conv_xxx",
        "question": "What are the top 3 pain points?"
    }
    """
    try:
        from agents import ConversationalLeadAgent, ClientAgent
        
        data = request.json
        conversation_id = data.get('conversation_id')
        question = data.get('question')
        
        if not conversation_id or not question:
            return jsonify({'success': False, 'error': 'conversation_id and question required'}), 400
        
        # Recreate agent with existing conversation
        client = ClientAgent(conversation_id=conversation_id)
        agent = ConversationalLeadAgent(client_agent=client)
        
        answer = agent.ask_followup_question(question)
        
        return jsonify({
            'success': True,
            'answer': answer,
            'conversation_id': conversation_id
        })
        
    except Exception as e:
        logger.error(f"Follow-up question failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversation/roi', methods=['POST'])
def conversation_calculate_roi():
    """
    Calculate ROI with conversation context.
    
    Expects JSON:
    {
        "conversation_id": "conv_xxx",
        "company_size": 250,
        "avg_salary": 75000
    }
    """
    try:
        from agents import ConversationalLeadAgent, ClientAgent
        
        data = request.json
        conversation_id = data.get('conversation_id')
        company_size = data.get('company_size', 100)
        avg_salary = data.get('avg_salary', 70000)
        
        if not conversation_id:
            return jsonify({'success': False, 'error': 'conversation_id required'}), 400
        
        client = ClientAgent(conversation_id=conversation_id)
        agent = ConversationalLeadAgent(client_agent=client)
        
        roi = agent.calculate_roi_in_context(company_size, avg_salary)
        
        return jsonify({
            'success': True,
            'roi': roi,
            'conversation_id': conversation_id
        })
        
    except Exception as e:
        logger.error(f"ROI calculation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversation/email', methods=['POST'])
def conversation_generate_email():
    """
    Generate personalized outreach email with conversation context.
    
    Expects JSON:
    {
        "conversation_id": "conv_xxx",
        "contact_name": "John Doe"  // optional
    }
    """
    try:
        from agents import ConversationalLeadAgent, ClientAgent
        
        data = request.json
        conversation_id = data.get('conversation_id')
        contact_name = data.get('contact_name')
        
        if not conversation_id:
            return jsonify({'success': False, 'error': 'conversation_id required'}), 400
        
        client = ClientAgent(conversation_id=conversation_id)
        agent = ConversationalLeadAgent(client_agent=client)
        
        email = agent.generate_outreach_email(contact_name)
        
        return jsonify({
            'success': True,
            'email': email,
            'conversation_id': conversation_id
        })
        
    except Exception as e:
        logger.error(f"Email generation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversation/summary', methods=['POST'])
def conversation_get_summary():
    """
    Get summary of entire conversation.
    
    Expects JSON:
    {
        "conversation_id": "conv_xxx"
    }
    """
    try:
        from agents import ConversationalLeadAgent, ClientAgent
        
        data = request.json
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return jsonify({'success': False, 'error': 'conversation_id required'}), 400
        
        client = ClientAgent(conversation_id=conversation_id)
        agent = ConversationalLeadAgent(client_agent=client)
        
        summary = agent.get_conversation_summary()
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/conversation/complete', methods=['POST'])
def conversation_complete_analysis():
    """
    Run complete conversational analysis workflow.
    
    Expects JSON:
    {
        "company_name": "TechCorp",
        "job_count": 45,
        "industry": "Software",
        "company_size": 500,
        "avg_salary": 85000,
        "generate_email": true  // optional
    }
    """
    try:
        from agents import analyze_lead_conversationally
        
        data = request.json
        company_name = data.get('company_name')
        
        if not company_name:
            return jsonify({'success': False, 'error': 'company_name required'}), 400
        
        initial_data = {
            'job_count': data.get('job_count', 0),
            'industry': data.get('industry', 'Unknown'),
            'company_size': data.get('company_size', 100),
            'avg_salary': data.get('avg_salary', 75000)
        }
        
        results = analyze_lead_conversationally(
            company_name=company_name,
            initial_data=initial_data,
            research_pain_points=True,
            calculate_roi=True,
            generate_email=data.get('generate_email', False)
        )
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Complete analysis failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# BATCH PROCESSING ENDPOINTS (OpenAI Batch API - 50% Cost Savings)
# ============================================================================

@app.route('/api/batch/create', methods=['POST'])
def batch_create():
    """
    Create a batch job for processing multiple jobs asynchronously.
    
    Expects JSON:
    {
        "jobs": [...],  // Array of job objects
        "task_type": "analyze",  // analyze, qualify, parse, extract_pain_points
        "model": "gpt-4o-mini"  // optional
    }
    
    Returns batch_id for tracking.
    """
    try:
        from agents import BatchProcessorAgent
        
        data = request.json
        jobs = data.get('jobs', [])
        task_type = data.get('task_type', 'analyze')
        model = data.get('model', 'gpt-4o-mini')
        
        if not jobs:
            return jsonify({'success': False, 'error': 'jobs array required'}), 400
        
        agent = BatchProcessorAgent()
        
        # Create input file
        input_file = agent.create_batch_input_file(jobs, task_type, model)
        
        # Upload
        file_id = agent.upload_batch_file(input_file)
        
        # Create batch
        batch_id = agent.create_batch(
            file_id,
            description=f"{task_type} for {len(jobs)} jobs via dashboard"
        )
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'file_id': file_id,
            'job_count': len(jobs),
            'task_type': task_type,
            'model': model,
            'message': 'Batch created. Results available within 24 hours.'
        })
        
    except Exception as e:
        logger.error(f"Batch creation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/status/<batch_id>', methods=['GET'])
def batch_get_status(batch_id):
    """Get status of a batch job."""
    try:
        from agents import BatchProcessorAgent
        
        agent = BatchProcessorAgent()
        status = agent.check_batch_status(batch_id)
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Status check failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/results/<batch_id>', methods=['GET'])
def batch_get_results(batch_id):
    """Download and parse results from a completed batch."""
    try:
        from agents import BatchProcessorAgent
        
        agent = BatchProcessorAgent()
        
        # Check status first
        status = agent.check_batch_status(batch_id)
        
        if status['status'] != 'completed':
            return jsonify({
                'success': False,
                'error': f"Batch not completed yet (status: {status['status']})"
            }), 400
        
        # Download results
        results_file = agent.download_results(batch_id)
        
        # Parse results
        parsed_results = agent.parse_results(results_file)
        
        return jsonify({
            'success': True,
            'batch_id': batch_id,
            'results_file': results_file,
            'total': len(parsed_results),
            'successful': sum(1 for r in parsed_results if r['success']),
            'failed': sum(1 for r in parsed_results if not r['success']),
            'results': parsed_results
        })
        
    except Exception as e:
        logger.error(f"Results retrieval failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/cancel/<batch_id>', methods=['POST'])
def batch_cancel(batch_id):
    """Cancel a running batch job."""
    try:
        from agents import BatchProcessorAgent
        
        agent = BatchProcessorAgent()
        result = agent.cancel_batch(batch_id)
        
        return jsonify({
            'success': True,
            'batch_id': result['id'],
            'status': result['status']
        })
        
    except Exception as e:
        logger.error(f"Batch cancellation failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/list', methods=['GET'])
def batch_list():
    """List recent batch jobs."""
    try:
        from agents import BatchProcessorAgent
        
        limit = request.args.get('limit', 10, type=int)
        
        agent = BatchProcessorAgent()
        batches = agent.list_batches(limit=limit)
        
        return jsonify({
            'success': True,
            'batches': batches,
            'count': len(batches)
        })
        
    except Exception as e:
        logger.error(f"Batch list failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch/process-scraped', methods=['POST'])
def batch_process_scraped_jobs():
    """
    Process all scraped jobs from a scraping session in batch mode.
    
    Expects JSON:
    {
        "scrape_results": [...],  // Results from /api/scrape endpoint
        "task_type": "analyze"  // optional
    }
    """
    try:
        from agents import process_jobs_batch
        
        data = request.json
        scrape_results = data.get('scrape_results', [])
        task_type = data.get('task_type', 'analyze')
        
        if not scrape_results:
            return jsonify({'success': False, 'error': 'scrape_results required'}), 400
        
        # Process in batch mode
        result = process_jobs_batch(
            scrape_results,
            task_type=task_type,
            wait_for_completion=False,
            model='gpt-4o-mini'
        )
        
        return jsonify({
            'success': True,
            'batch_id': result['batch_id'],
            'job_count': result['job_count'],
            'task_type': result['task_type'],
            'message': f"Processing {result['job_count']} jobs in batch mode. Check status with batch_id."
        })
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 80)
    print("FORECASTA LEAD ANALYSIS DASHBOARD")
    print("=" * 80)
    print("\nStarting server...")
    print(f"Leads directory: {LEADS_DIR}")
    print(f"Dashboard URL: http://localhost:3000")
    print("\nAvailable Features:")
    print("  - Lead Analysis & Qualification")
    print("  - Job Scraping (Craigslist)")
    print("  - AI-Powered Parsing")
    print("  - Vector Search")
    print("  - Database Queries")
    if RAG_AVAILABLE:
        print("  - RAG Q&A System")
    print("  - Full Pipeline Automation")
    print("\nPress Ctrl+C to stop\n")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=3000, debug=False)  # Disable debug for clean JSON errors
