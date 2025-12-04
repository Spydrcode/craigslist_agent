"""Storer Agent - Save processed data for ML and retrieval."""

import json
import csv
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


class StorerAgent:
    """Handles data persistence for leads and analytics."""

    def __init__(self, data_dir: str = "data/leads"):
        self.name = "StorerAgent"
        self.data_dir = Path(data_dir)
        self.leads_dir = self.data_dir
        self.master_csv = self.data_dir / "leads_master.csv"

        # Ensure directories exist
        self.leads_dir.mkdir(parents=True, exist_ok=True)

    def store(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store processed lead data.

        Args:
            processed_data: Fully processed lead from Writer agent

        Returns:
            Data with storage metadata added
        """
        try:
            # Generate unique ID
            lead_id = self._generate_lead_id(processed_data)

            # Save individual lead file
            lead_file = self.leads_dir / f"lead_{lead_id}.json"
            with open(lead_file, 'w') as f:
                json.dump(processed_data, f, indent=2)

            # Update master CSV
            self._update_master_csv(processed_data, lead_id)

            result = {
                **processed_data,
                "lead_id": lead_id,
                "storage_path": str(lead_file),
                "storage_status": "success",
                "stored_at": datetime.utcnow().isoformat()
            }

            return result

        except Exception as e:
            return {
                **processed_data,
                "storage_status": "error",
                "storage_error": str(e)
            }

    def _generate_lead_id(self, data: Dict[str, Any]) -> str:
        """Generate unique lead ID."""
        company = data.get('company_name', 'unknown').replace(' ', '_').lower()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{company}_{timestamp}"

    def _update_master_csv(self, data: Dict[str, Any], lead_id: str) -> None:
        """Update master CSV with lead summary."""
        # Check if file exists
        file_exists = self.master_csv.exists()

        # Prepare row data
        row = {
            'lead_id': lead_id,
            'company_name': data.get('company_name'),
            'job_title': data.get('job_title'),
            'location': data.get('location'),
            'industry': data.get('company_industry'),
            'score': data.get('score'),
            'tier': data.get('tier'),
            'employee_count': data.get('company_size'),
            'is_local': data.get('is_local'),
            'disqualified': data.get('disqualified', False),
            'disqualification_reason': data.get('disqualification_reason'),
            'posting_url': data.get('posting_url'),
            'posting_date': data.get('posting_date'),
            'processed_at': datetime.utcnow().isoformat(),
            'status': 'new'
        }

        # Write to CSV
        with open(self.master_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)

    def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """Retrieve a lead by ID."""
        lead_file = self.leads_dir / f"lead_{lead_id}.json"
        if lead_file.exists():
            with open(lead_file, 'r') as f:
                return json.load(f)
        return None

    def get_all_leads(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve all leads with optional filtering."""
        leads = []

        for lead_file in self.leads_dir.glob("lead_*.json"):
            with open(lead_file, 'r') as f:
                lead = json.load(f)

                # Apply filters if provided
                if filters:
                    if not self._matches_filters(lead, filters):
                        continue

                leads.append(lead)

        return leads

    def _matches_filters(self, lead: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if lead matches filter criteria."""
        for key, value in filters.items():
            if key not in lead:
                return False
            if lead[key] != value:
                return False
        return True

    def update_lead_status(self, lead_id: str, status: str, notes: str = None) -> bool:
        """Update lead status and add notes."""
        lead = self.get_lead(lead_id)
        if not lead:
            return False

        lead['status'] = status
        if notes:
            if 'notes' not in lead:
                lead['notes'] = []
            lead['notes'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'note': notes
            })

        # Save updated lead
        lead_file = self.leads_dir / f"lead_{lead_id}.json"
        with open(lead_file, 'w') as f:
            json.dump(lead, f, indent=2)

        return True

    def get_analytics(self) -> Dict[str, Any]:
        """Generate analytics from stored leads."""
        all_leads = self.get_all_leads()

        analytics = {
            'total_leads': len(all_leads),
            'by_tier': {},
            'by_status': {},
            'by_industry': {},
            'avg_score': 0,
            'disqualified_count': 0
        }

        total_score = 0

        for lead in all_leads:
            # Count by tier
            tier = lead.get('tier')
            if tier:
                analytics['by_tier'][tier] = analytics['by_tier'].get(tier, 0) + 1

            # Count by status
            status = lead.get('status', 'new')
            analytics['by_status'][status] = analytics['by_status'].get(status, 0) + 1

            # Count by industry
            industry = lead.get('company_industry', 'unknown')
            analytics['by_industry'][industry] = analytics['by_industry'].get(industry, 0) + 1

            # Sum scores
            score = lead.get('score', 0)
            total_score += score

            # Count disqualified
            if lead.get('disqualified'):
                analytics['disqualified_count'] += 1

        # Calculate average score
        if len(all_leads) > 0:
            analytics['avg_score'] = round(total_score / len(all_leads), 2)

        return analytics
