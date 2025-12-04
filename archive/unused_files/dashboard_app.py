"""
Professional Web Dashboard for Prospecting System
Flask-based dashboard for managing hundreds of companies.

Run: python dashboard_app.py
Access: http://localhost:5000
"""
import sys
import os
import json
import glob
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from typing import List, Dict, Any

from models_enhanced import ProspectLead
from client_manager import ClientManager
from agents.outreach_agent import OutreachAgent
from utils import get_logger

logger = get_logger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'prospecting-dashboard-2025'

# Initialize managers
client_manager = ClientManager()
outreach_agent = OutreachAgent()

# Directories
PROSPECTS_DIR = Path("output/prospects")
BATCH_RESULTS_DIR = Path("output/batch_results")
CLIENTS_DIR = Path("data/clients")


def load_all_prospects() -> List[Dict[str, Any]]:
    """Load all prospects from all sources."""
    prospects = []

    # Load from regular prospecting
    if PROSPECTS_DIR.exists():
        for file in PROSPECTS_DIR.glob("prospects_*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            item['_source'] = 'regular'
                            item['_file'] = file.name
                            prospects.append(item)
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

    # Load from batch results
    if BATCH_RESULTS_DIR.exists():
        for file in BATCH_RESULTS_DIR.glob("batch_prospects_*.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            item['_source'] = 'batch'
                            item['_file'] = file.name
                            prospects.append(item)
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

    return prospects


def get_prospect_stats(prospects: List[Dict]) -> Dict:
    """Calculate statistics from prospects."""
    if not prospects:
        return {
            'total': 0,
            'urgent': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'by_city': {},
            'by_category': {},
            'by_growth_stage': {},
            'avg_score': 0
        }

    stats = {
        'total': len(prospects),
        'urgent': sum(1 for p in prospects if p.get('priority_tier') == 'URGENT'),
        'high': sum(1 for p in prospects if p.get('priority_tier') == 'HIGH'),
        'medium': sum(1 for p in prospects if p.get('priority_tier') == 'MEDIUM'),
        'low': sum(1 for p in prospects if p.get('priority_tier') == 'LOW'),
        'by_city': {},
        'by_category': {},
        'by_growth_stage': {},
        'avg_score': 0
    }

    # Calculate averages
    scores = [p.get('lead_score', 0) for p in prospects]
    stats['avg_score'] = round(sum(scores) / len(scores), 1) if scores else 0

    # By city
    for p in prospects:
        city = p.get('source_city', 'Unknown')
        stats['by_city'][city] = stats['by_city'].get(city, 0) + 1

    # By category
    for p in prospects:
        cat = p.get('source_category', 'Unknown')
        stats['by_category'][cat] = stats['by_category'].get(cat, 0) + 1

    # By growth stage
    for p in prospects:
        stage = p.get('company_profile', {}).get('growth_signals', {}).get('growth_stage', 'UNKNOWN')
        stats['by_growth_stage'][stage] = stats['by_growth_stage'].get(stage, 0) + 1

    return stats


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/prospects')
def api_prospects():
    """Get all prospects with optional filters."""
    # Get filters from query params
    city_filter = request.args.get('city', None)
    category_filter = request.args.get('category', None)
    priority_filter = request.args.get('priority', None)
    min_score = request.args.get('min_score', None)
    selected_only = request.args.get('selected', None)

    # Load all prospects
    prospects = load_all_prospects()

    # Apply filters
    if city_filter:
        prospects = [p for p in prospects if p.get('source_city') == city_filter]

    if category_filter:
        prospects = [p for p in prospects if p.get('source_category') == category_filter]

    if priority_filter:
        prospects = [p for p in prospects if p.get('priority_tier') == priority_filter]

    if min_score:
        try:
            min_val = float(min_score)
            prospects = [p for p in prospects if p.get('lead_score', 0) >= min_val]
        except:
            pass

    # Check if prospect is selected
    selected_clients = client_manager.get_selected_clients()
    selected_ids = {c['id'] for c in selected_clients}

    for p in prospects:
        p['is_selected'] = p.get('lead_id') in selected_ids

    if selected_only == 'true':
        prospects = [p for p in prospects if p['is_selected']]

    # Sort by score (descending)
    prospects.sort(key=lambda x: x.get('lead_score', 0), reverse=True)

    return jsonify({
        'success': True,
        'count': len(prospects),
        'prospects': prospects
    })


@app.route('/api/stats')
def api_stats():
    """Get prospect statistics."""
    prospects = load_all_prospects()
    stats = get_prospect_stats(prospects)

    # Add selected client stats
    selected_clients = client_manager.get_selected_clients()
    stats['selected_total'] = len(selected_clients)
    stats['selected_by_status'] = {}

    for client in selected_clients:
        status = client.get('status', 'unknown')
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
    """Select a prospect for outreach."""
    try:
        data = request.get_json() or {}
        notes = data.get('notes', 'Selected from dashboard')
        your_name = data.get('your_name', 'Your Name')
        your_company = data.get('your_company', 'Your Company')
        your_title = data.get('your_title', 'Solutions Consultant')

        # Load prospect
        prospects = load_all_prospects()
        prospect_data = next((p for p in prospects if p.get('lead_id') == prospect_id), None)

        if not prospect_data:
            return jsonify({'error': 'Prospect not found'}), 404

        # Convert to ProspectLead model
        prospect = ProspectLead(**prospect_data)

        # Add to manager
        client_manager.add_prospect(prospect)
        client_manager.select_client(prospect_id, notes=notes)

        # Generate outreach content
        content = client_manager.generate_outreach_content(
            prospect_id,
            your_name,
            your_company,
            your_title,
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
    """Log an interaction with a prospect."""
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


@app.route('/api/filters')
def api_filters():
    """Get available filter options."""
    prospects = load_all_prospects()

    cities = sorted(set(p.get('source_city', 'Unknown') for p in prospects))
    categories = sorted(set(p.get('source_category', 'Unknown') for p in prospects))
    priorities = sorted(set(p.get('priority_tier', 'UNKNOWN') for p in prospects))

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

    # Header
    writer.writerow([
        'Lead ID', 'Company', 'Score', 'Priority', 'Growth Stage', 'Growth Score',
        'Jobs', 'City', 'Category', 'Source File'
    ])

    # Rows
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
            p.get('_file', '')
        ])

    output.seek(0)

    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename=prospects_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    }


@app.route('/api/analytics')
def api_analytics():
    """Export analytics data."""
    output_file = "data/clients/analytics_export.csv"
    client_manager.export_analytics_data(output_file)

    return jsonify({
        'success': True,
        'file': output_file
    })


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PROSPECTING DASHBOARD")
    print("="*80)
    print("\nStarting server...")
    print(f"Dashboard URL: http://localhost:5000")
    print("\nFeatures:")
    print("  - View all prospects from all searches")
    print("  - Filter by city, category, priority, score")
    print("  - Select prospects for outreach")
    print("  - Generate emails, call scripts, LinkedIn messages")
    print("  - Track all interactions")
    print("  - Export to CSV")
    print("  - Analytics dashboard")
    print("\nPress Ctrl+C to stop\n")
    print("="*80)

    app.run(host='0.0.0.0', port=5000, debug=True)
