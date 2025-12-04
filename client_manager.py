"""
Client Management System
Tracks prospects, manages outreach, stores all data for analytics.
"""
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from models_enhanced import ProspectLead
from agents.outreach_agent import OutreachAgent
from utils import get_logger

logger = get_logger(__name__)


class ClientManager:
    """
    Manages client lifecycle from prospect to active client.
    Tracks all interactions and stores data for analytics.
    """

    def __init__(self, data_dir: str = "data/clients"):
        """
        Initialize client manager.

        Args:
            data_dir: Directory to store client data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.prospects_file = self.data_dir / "prospects.json"
        self.selected_file = self.data_dir / "selected_clients.json"
        self.interactions_file = self.data_dir / "interactions.json"
        self.outreach_file = self.data_dir / "outreach_content.json"

        self.outreach_agent = OutreachAgent()

        logger.info(f"ClientManager initialized (data_dir: {data_dir})")

    def add_prospect(self, prospect: ProspectLead) -> str:
        """
        Add a new prospect to the system.

        Args:
            prospect: Prospect to add

        Returns:
            Prospect ID
        """
        prospects = self._load_prospects()

        prospect_data = {
            'id': prospect.lead_id,
            'company_name': prospect.company_profile.name,
            'lead_score': prospect.lead_score,
            'priority': prospect.priority_tier,
            'status': 'prospect',  # prospect, selected, contacted, qualified, client, rejected
            'data': self._serialize_prospect(prospect),
            'added_date': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }

        prospects[prospect.lead_id] = prospect_data
        self._save_prospects(prospects)

        logger.info(f"Added prospect: {prospect.company_profile.name}")
        return prospect.lead_id

    def select_client(
        self,
        prospect_id: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Mark a prospect as selected for outreach.

        Args:
            prospect_id: ID of prospect to select
            notes: Optional notes about selection

        Returns:
            Selected client data
        """
        prospects = self._load_prospects()

        if prospect_id not in prospects:
            raise ValueError(f"Prospect {prospect_id} not found")

        prospect_data = prospects[prospect_id]
        prospect_data['status'] = 'selected'
        prospect_data['selected_date'] = datetime.utcnow().isoformat()
        prospect_data['last_updated'] = datetime.utcnow().isoformat()

        if notes:
            prospect_data['selection_notes'] = notes

        # Save to both prospects and selected clients
        self._save_prospects(prospects)

        selected_clients = self._load_selected_clients()
        selected_clients[prospect_id] = prospect_data
        self._save_selected_clients(selected_clients)

        logger.info(f"Selected client: {prospect_data['company_name']}")

        return prospect_data

    def generate_outreach_content(
        self,
        prospect_id: str,
        your_name: str,
        your_company: str,
        your_title: str = "Solutions Consultant",
        include_email: bool = True,
        include_call_script: bool = True,
        include_linkedin: bool = True
    ) -> Dict[str, Any]:
        """
        Generate all outreach content for a prospect.

        Args:
            prospect_id: ID of prospect
            your_name: Your name
            your_company: Your company
            your_title: Your title
            include_email: Generate email
            include_call_script: Generate call script
            include_linkedin: Generate LinkedIn message

        Returns:
            Dictionary with all generated content
        """
        prospects = self._load_prospects()

        if prospect_id not in prospects:
            raise ValueError(f"Prospect {prospect_id} not found")

        prospect_data = prospects[prospect_id]
        prospect = self._deserialize_prospect(prospect_data['data'])

        content = {
            'prospect_id': prospect_id,
            'company_name': prospect.company_profile.name,
            'generated_at': datetime.utcnow().isoformat()
        }

        # Generate email
        if include_email:
            logger.info(f"Generating email for {prospect.company_profile.name}")
            email = self.outreach_agent.generate_email(
                prospect, your_name, your_company, your_title
            )
            content['email'] = email

        # Generate call script
        if include_call_script:
            logger.info(f"Generating call script for {prospect.company_profile.name}")
            call_script = self.outreach_agent.generate_call_script(
                prospect, your_name, your_company
            )
            content['call_script'] = call_script

        # Generate LinkedIn
        if include_linkedin:
            logger.info(f"Generating LinkedIn message for {prospect.company_profile.name}")
            linkedin_msg = self.outreach_agent.generate_linkedin_message(
                prospect, your_name, connection_request=True
            )
            content['linkedin_connection'] = linkedin_msg

            linkedin_dm = self.outreach_agent.generate_linkedin_message(
                prospect, your_name, connection_request=False
            )
            content['linkedin_dm'] = linkedin_dm

        # Save outreach content
        self._save_outreach_content(prospect_id, content)

        logger.info(f"Generated outreach content for {prospect.company_profile.name}")

        return content

    def log_interaction(
        self,
        prospect_id: str,
        interaction_type: str,
        outcome: str,
        notes: Optional[str] = None,
        next_action: Optional[str] = None,
        next_action_date: Optional[str] = None
    ):
        """
        Log an interaction with a prospect.

        Args:
            prospect_id: ID of prospect
            interaction_type: Type (email_sent, call_made, meeting_scheduled, etc.)
            outcome: Outcome (responded, no_response, interested, not_interested, etc.)
            notes: Interaction notes
            next_action: Next action to take
            next_action_date: Date for next action
        """
        interactions = self._load_interactions()

        interaction = {
            'prospect_id': prospect_id,
            'type': interaction_type,
            'outcome': outcome,
            'notes': notes,
            'next_action': next_action,
            'next_action_date': next_action_date,
            'timestamp': datetime.utcnow().isoformat()
        }

        if prospect_id not in interactions:
            interactions[prospect_id] = []

        interactions[prospect_id].append(interaction)
        self._save_interactions(interactions)

        # Update prospect status
        prospects = self._load_prospects()
        if prospect_id in prospects:
            prospects[prospect_id]['last_interaction'] = datetime.utcnow().isoformat()
            prospects[prospect_id]['last_updated'] = datetime.utcnow().isoformat()

            # Update status based on interaction
            if interaction_type == 'email_sent':
                prospects[prospect_id]['status'] = 'contacted'
            elif interaction_type == 'meeting_scheduled':
                prospects[prospect_id]['status'] = 'qualified'
            elif outcome == 'became_client':
                prospects[prospect_id]['status'] = 'client'

            self._save_prospects(prospects)

        logger.info(f"Logged interaction: {interaction_type} for {prospect_id}")

    def get_selected_clients(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all selected clients.

        Args:
            status: Filter by status (selected, contacted, qualified, client)

        Returns:
            List of client data
        """
        selected = self._load_selected_clients()

        clients = list(selected.values())

        if status:
            clients = [c for c in clients if c.get('status') == status]

        return clients

    def get_prospect_history(self, prospect_id: str) -> Dict[str, Any]:
        """
        Get complete history for a prospect.

        Args:
            prospect_id: Prospect ID

        Returns:
            Dictionary with all prospect data and history
        """
        prospects = self._load_prospects()
        interactions = self._load_interactions()
        outreach = self._load_outreach_content()

        if prospect_id not in prospects:
            raise ValueError(f"Prospect {prospect_id} not found")

        history = {
            'prospect': prospects[prospect_id],
            'interactions': interactions.get(prospect_id, []),
            'outreach_content': outreach.get(prospect_id, [])
        }

        return history

    def export_analytics_data(self, output_file: str):
        """
        Export all data for analytics.

        Args:
            output_file: Output CSV file
        """
        prospects = self._load_prospects()
        interactions = self._load_interactions()

        rows = []

        for prospect_id, prospect_data in prospects.items():
            prospect_interactions = interactions.get(prospect_id, [])

            row = {
                'prospect_id': prospect_id,
                'company_name': prospect_data['company_name'],
                'lead_score': prospect_data['lead_score'],
                'priority': prospect_data['priority'],
                'status': prospect_data['status'],
                'added_date': prospect_data['added_date'],
                'selected_date': prospect_data.get('selected_date', ''),
                'total_interactions': len(prospect_interactions),
                'last_interaction': prospect_data.get('last_interaction', ''),
                'outcome': prospect_data.get('final_outcome', ''),
            }

            # Add growth signals
            data = prospect_data.get('data', {})
            if 'company_profile' in data and 'growth_signals' in data['company_profile']:
                gs = data['company_profile']['growth_signals']
                row['growth_score'] = gs.get('growth_score', 0)
                row['growth_stage'] = gs.get('growth_stage', '')

            # Add opportunities
            if 'service_opportunities' in data:
                opps = data['service_opportunities']
                if opps:
                    row['top_opportunity'] = opps[0].get('service_type', '')
                    row['opportunity_confidence'] = opps[0].get('confidence_score', 0)

            rows.append(row)

        # Write CSV
        if rows:
            keys = rows[0].keys()
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"Exported analytics data to {output_file}")

    def _serialize_prospect(self, prospect: ProspectLead) -> Dict[str, Any]:
        """Serialize prospect to dict."""
        return json.loads(json.dumps(prospect.dict(), default=str))

    def _deserialize_prospect(self, data: Dict[str, Any]) -> ProspectLead:
        """Deserialize prospect from dict."""
        return ProspectLead(**data)

    def _load_prospects(self) -> Dict[str, Any]:
        """Load prospects from file."""
        if self.prospects_file.exists():
            with open(self.prospects_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_prospects(self, prospects: Dict[str, Any]):
        """Save prospects to file."""
        with open(self.prospects_file, 'w') as f:
            json.dump(prospects, f, indent=2, default=str)

    def _load_selected_clients(self) -> Dict[str, Any]:
        """Load selected clients from file."""
        if self.selected_file.exists():
            with open(self.selected_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_selected_clients(self, clients: Dict[str, Any]):
        """Save selected clients to file."""
        with open(self.selected_file, 'w') as f:
            json.dump(clients, f, indent=2, default=str)

    def _load_interactions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load interactions from file."""
        if self.interactions_file.exists():
            with open(self.interactions_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_interactions(self, interactions: Dict[str, List[Dict[str, Any]]]):
        """Save interactions to file."""
        with open(self.interactions_file, 'w') as f:
            json.dump(interactions, f, indent=2, default=str)

    def _load_outreach_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load outreach content from file."""
        if self.outreach_file.exists():
            with open(self.outreach_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_outreach_content(self, prospect_id: str, content: Dict[str, Any]):
        """Save outreach content to file."""
        all_content = self._load_outreach_content()

        if prospect_id not in all_content:
            all_content[prospect_id] = []

        all_content[prospect_id].append(content)

        with open(self.outreach_file, 'w') as f:
            json.dump(all_content, f, indent=2, default=str)
