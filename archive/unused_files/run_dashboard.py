"""
Enhanced Prospecting Dashboard
Combines prospecting, client management, and analytics in one interface.

Run: python run_dashboard.py
Access: http://localhost:5000
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from models_enhanced import ProspectLead
from client_manager import ClientManager
from orchestrator_simple import SimpleProspectingOrchestrator
from utils import get_logger

logger = get_logger(__name__)

app = Flask(__name__,
            template_folder='dashboard/templates',
            static_folder='dashboard/static')
app.config['SECRET_KEY'] = 'enhanced-prospecting-2025'

# Initialize
client_manager = ClientManager()
orchestrator = None  # Lazy init

# Directories
PROSPECTS_DIR = Path("output/prospects")
BATCH_RESULTS_DIR = Path("output/batch_results")


def get_orchestrator():
    """Lazy initialization of orchestrator."""
    global orchestrator
    if orchestrator is None:
        orchestrator = SimpleProspectingOrchestrator()
    return orchestrator


def load_all_prospects() -> List[Dict]:
    """Load all prospects from all sources."""
    prospects = []

    # Load from regular prospecting runs
    if PROSPECTS_DIR.exists():
        for file in sorted(PROSPECTS_DIR.glob("prospects_*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            item['_source'] = 'single'
                            item['_file'] = file.name
                            item['_timestamp'] = file.stat().st_mtime
                            prospects.append(item)
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

    # Load from batch results
    if BATCH_RESULTS_DIR.exists():
        for file in sorted(BATCH_RESULTS_DIR.glob("batch_prospects_*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            item['_source'] = 'batch'
                            item['_file'] = file.name
                            item['_timestamp'] = file.stat().st_mtime
                            prospects.append(item)
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

    # Remove duplicates (by lead_id)
    seen = set()
    unique_prospects = []
    for p in prospects:
        lead_id = p.get('lead_id')
        if lead_id and lead_id not in seen:
            seen.add(lead_id)
            unique_prospects.append(p)

    return unique_prospects


@app.route('/')
def index():
    """Main dashboard."""
    return render_template('index.html')


@app.route('/api/prospects')
def api_prospects():
    """Get all prospects with filters."""
    city = request.args.get('city')
    category = request.args.get('category')
    priority = request.args.get('priority')
    min_score = request.args.get('min_score', type=float)
    selected_only = request.args.get('selected') == 'true'

    prospects = load_all_prospects()

    # Apply filters
    if city:
        prospects = [p for p in prospects if p.get('source_city') == city]
    if category:
        prospects = [p for p in prospects if p.get('source_category') == category]
    if priority:
        prospects = [p for p in prospects if p.get('priority_tier') == priority]
    if min_score:
        prospects = [p for p in prospects if p.get('lead_score', 0) >= min_score]

    # Check if selected
    selected_clients = client_manager.get_selected_clients()
    selected_ids = {c['id'] for c in selected_clients}

    for p in prospects:
        p['is_selected'] = p.get('lead_id') in selected_ids

    if selected_only:
        prospects = [p for p in prospects if p['is_selected']]

    # Sort by score
    prospects.sort(key=lambda x: x.get('lead_score', 0), reverse=True)

    return jsonify({
        'success': True,
        'count': len(prospects),
        'prospects': prospects
    })


@app.route('/api/stats')
def api_stats():
    """Get dashboard statistics."""
    prospects = load_all_prospects()

    stats = {
        'total_prospects': len(prospects),
        'urgent': sum(1 for p in prospects if p.get('priority_tier') == 'URGENT'),
        'high': sum(1 for p in prospects if p.get('priority_tier') == 'HIGH'),
        'medium': sum(1 for p in prospects if p.get('priority_tier') == 'MEDIUM'),
        'low': sum(1 for p in prospects if p.get('priority_tier') == 'LOW'),
        'by_city': {},
        'by_category': {},
        'by_growth_stage': {},
        'avg_score': 0
    }

    # Averages
    scores = [p.get('lead_score', 0) for p in prospects]
    stats['avg_score'] = round(sum(scores) / len(scores), 1) if scores else 0

    # Group by city
    for p in prospects:
        city = p.get('source_city', 'Unknown')
        stats['by_city'][city] = stats['by_city'].get(city, 0) + 1

    # Group by category
    for p in prospects:
        cat = p.get('source_category', 'Unknown')
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1

    # Group by growth stage
    for p in prospects:
        stage = p.get('company_profile', {}).get('growth_signals', {}).get('growth_stage', 'UNKNOWN')
        stats['by_growth_stage'][stage] = stats['by_growth_stage'].get(stage, 0) + 1

    # Selected clients stats
    selected = client_manager.get_selected_clients()
    stats['selected_total'] = len(selected)
    stats['selected_by_status'] = {}
    for c in selected:
        status = c.get('status', 'unknown')
        stats['selected_by_status'][status] = stats['selected_by_status'].get(status, 0) + 1

    return jsonify(stats)


@app.route('/api/prospect/<prospect_id>')
def api_prospect_detail(prospect_id):
    """Get single prospect details."""
    prospects = load_all_prospects()
    prospect = next((p for p in prospects if p.get('lead_id') == prospect_id), None)

    if not prospect:
        return jsonify({'error': 'Prospect not found'}), 404

    # Check if selected
    selected_clients = client_manager.get_selected_clients()
    prospect['is_selected'] = prospect_id in {c['id'] for c in selected_clients}

    # Get history if selected
    if prospect['is_selected']:
        try:
            history = client_manager.get_prospect_history(prospect_id)
            prospect['interactions'] = history.get('interactions', [])
            prospect['outreach_content'] = history.get('outreach_content', [])
        except:
            prospect['interactions'] = []
            prospect['outreach_content'] = []

    return jsonify(prospect)


@app.route('/api/prospect/<prospect_id>/select', methods=['POST'])
def api_select_prospect(prospect_id):
    """Select prospect and generate outreach."""
    try:
        data = request.get_json() or {}

        # Load prospect
        prospects = load_all_prospects()
        prospect_data = next((p for p in prospects if p.get('lead_id') == prospect_id), None)

        if not prospect_data:
            return jsonify({'error': 'Prospect not found'}), 404

        # Convert to model
        prospect = ProspectLead(**prospect_data)

        # Add to manager
        client_manager.add_prospect(prospect)
        client_manager.select_client(prospect_id, notes=data.get('notes', 'Selected from dashboard'))

        # Generate outreach
        content = client_manager.generate_outreach_content(
            prospect_id,
            data.get('your_name', 'Your Name'),
            data.get('your_company', 'Your Company'),
            data.get('your_title', 'Solutions Consultant'),
            include_email=True,
            include_call_script=True,
            include_linkedin=True
        )

        return jsonify({
            'success': True,
            'message': 'Prospect selected and outreach generated',
            'content': content
        })

    except Exception as e:
        logger.error(f"Error selecting prospect: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/prospect/<prospect_id>/interaction', methods=['POST'])
def api_log_interaction(prospect_id):
    """Log interaction."""
    try:
        data = request.get_json()
        client_manager.log_interaction(
            prospect_id,
            data.get('type', 'other'),
            data.get('outcome', 'unknown'),
            notes=data.get('notes'),
            next_action=data.get('next_action'),
            next_action_date=data.get('next_action_date')
        )
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging interaction: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """Run prospecting for a single city/category."""
    try:
        data = request.get_json()

        orch = get_orchestrator()
        result = orch.find_prospects(
            city=data.get('city', 'sfbay'),
            category=data.get('category', 'sof'),
            keywords=data.get('keywords'),
            max_pages=data.get('max_pages', 2),
            min_growth_score=data.get('min_growth_score', 0.3),
            min_lead_score=data.get('min_lead_score', 50.0)
        )

        if result['success']:
            return jsonify({
                'success': True,
                'jobs': result['stats']['jobs_scraped'],
                'prospects': len(result['prospects']),
                'message': f"Found {len(result['prospects'])} prospects from {result['stats']['jobs_scraped']} jobs"
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error')
            })

    except Exception as e:
        logger.error(f"Scrape error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/batch-scrape', methods=['POST'])
def api_batch_scrape():
    """Run batch prospecting across multiple cities/categories."""
    try:
        data = request.get_json()
        cities = data.get('cities', [])
        categories = data.get('categories', [])

        if not cities or not categories:
            return jsonify({'error': 'Cities and categories required'}), 400

        # Import batch prospector
        from batch_prospecting import BatchProspector

        prospector = BatchProspector()
        result = prospector.run_batch(
            cities=cities,
            categories=categories,
            keywords=data.get('keywords'),
            max_pages=data.get('max_pages', 2),
            min_growth_score=data.get('min_growth_score', 0.3),
            min_lead_score=data.get('min_lead_score', 50.0)
        )

        return jsonify({
            'success': True,
            'total_searches': result['stats']['total_searches'],
            'completed': result['stats']['completed_searches'],
            'prospects': len(result['prospects']),
            'files': result['files']
        })

    except Exception as e:
        logger.error(f"Batch scrape error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/filters')
def api_filters():
    """Get available filter options."""
    prospects = load_all_prospects()

    cities = sorted(set(p.get('source_city', 'Unknown') for p in prospects if p.get('source_city')))
    categories = sorted(set(p.get('source_category', 'Unknown') for p in prospects if p.get('source_category')))
    priorities = ['URGENT', 'HIGH', 'MEDIUM', 'LOW']

    return jsonify({
        'cities': cities,
        'categories': categories,
        'priorities': priorities
    })


@app.route('/api/export/csv')
def api_export_csv():
    """Export prospects to CSV."""
    import csv
    import io

    prospects = load_all_prospects()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Lead ID', 'Company', 'Score', 'Priority', 'Growth Stage', 'Growth Score',
        'Jobs', 'City', 'Category', 'Selected', 'Source'
    ])

    selected_ids = {c['id'] for c in client_manager.get_selected_clients()}

    for p in prospects:
        company = p.get('company_profile', {})
        growth = company.get('growth_signals', {})

        writer.writerow([
            p.get('lead_id', ''),
            company.get('name', ''),
            p.get('lead_score', 0),
            p.get('priority_tier', ''),
            growth.get('growth_stage', ''),
            growth.get('growth_score', 0),
            len(p.get('job_postings', [])),
            p.get('source_city', ''),
            p.get('source_category', ''),
            'Yes' if p.get('lead_id') in selected_ids else 'No',
            p.get('_source', '')
        ])

    output.seek(0)

    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=prospects_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    }


if __name__ == '__main__':
    print("\n" + "="*80)
    print("ENHANCED PROSPECTING DASHBOARD")
    print("="*80)
    print("\nStarting server...")
    print(f"Dashboard URL: http://localhost:5000")
    print("\nFeatures:")
    print("  - View all prospects from batch and single runs")
    print("  - Filter by city, category, priority, score")
    print("  - Run new prospecting searches from dashboard")
    print("  - Run batch prospecting across multiple cities")
    print("  - Select prospects and generate outreach")
    print("  - Track interactions and status")
    print("  - Export to CSV")
    print("\nPress Ctrl+C to stop\n")
    print("="*80)

    app.run(host='0.0.0.0', port=5000, debug=True)
