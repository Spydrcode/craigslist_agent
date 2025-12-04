"""
Interactive Client Management Tool
Select prospects, generate outreach content, track interactions.
"""
import sys
import json
from pathlib import Path
from client_manager import ClientManager
from models_enhanced import ProspectLead

# Configuration - UPDATE THESE WITH YOUR DETAILS
YOUR_NAME = "Your Name"
YOUR_COMPANY = "Your Company"
YOUR_TITLE = "Solutions Consultant"


def load_prospects_from_file(filepath: str) -> list:
    """Load prospects from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)

    prospects = []
    for item in data:
        try:
            prospect = ProspectLead(**item)
            prospects.append(prospect)
        except Exception as e:
            print(f"Warning: Could not load prospect: {e}")

    return prospects


def select_prospects_interactive(prospects: list, manager: ClientManager):
    """Interactive prospect selection."""
    print("\n" + "="*60)
    print("PROSPECT SELECTION")
    print("="*60)

    # Show prospects
    print(f"\nFound {len(prospects)} prospects\n")

    for i, prospect in enumerate(prospects, 1):
        print(f"{i}. {prospect.company_profile.name}")
        print(f"   Score: {prospect.lead_score:.1f}/100 | Priority: {prospect.priority_tier}")
        print(f"   Jobs: {len(prospect.job_postings)}")

        if prospect.service_opportunities:
            top_opp = prospect.service_opportunities[0]
            print(f"   Opportunity: {top_opp.service_type} ({top_opp.confidence_score:.0%})")
            print(f"   Value: {top_opp.estimated_value}")

        print()

    # Select prospects
    print("Enter prospect numbers to select (comma-separated, or 'all' for all):")
    print("Example: 1,3,5  or  all")
    selection = input("> ").strip()

    if selection.lower() == 'all':
        selected_prospects = prospects
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_prospects = [prospects[i] for i in indices if 0 <= i < len(prospects)]
        except:
            print("Invalid selection. Using all prospects.")
            selected_prospects = prospects

    # Add to manager and generate content
    print(f"\nProcessing {len(selected_prospects)} prospects...")

    for prospect in selected_prospects:
        # Add prospect
        manager.add_prospect(prospect)

        # Select client
        manager.select_client(prospect.lead_id, notes="Selected from interactive tool")

        # Generate outreach content
        print(f"\nGenerating content for: {prospect.company_profile.name}...")

        try:
            content = manager.generate_outreach_content(
                prospect.lead_id,
                YOUR_NAME,
                YOUR_COMPANY,
                YOUR_TITLE,
                include_email=True,
                include_call_script=True,
                include_linkedin=True
            )

            print(f"  [OK] Email generated")
            print(f"  [OK] Call script generated")
            print(f"  [OK] LinkedIn messages generated")

            # Show email preview
            print(f"\n  EMAIL PREVIEW:")
            print(f"  Subject: {content['email']['subject']}")
            print(f"  Body (first 150 chars): {content['email']['body'][:150]}...")

        except Exception as e:
            print(f"  [ERROR] Failed to generate content: {e}")

    print(f"\n{len(selected_prospects)} prospects processed and saved!")


def view_selected_clients(manager: ClientManager):
    """View all selected clients."""
    clients = manager.get_selected_clients()

    if not clients:
        print("\nNo selected clients yet.")
        return

    print("\n" + "="*60)
    print(f"SELECTED CLIENTS ({len(clients)})")
    print("="*60)

    for client in clients:
        print(f"\nCompany: {client['company_name']}")
        print(f"Status: {client['status']}")
        print(f"Score: {client['lead_score']:.1f}")
        print(f"Priority: {client['priority']}")
        print(f"Selected: {client.get('selected_date', 'Unknown')}")

        if 'last_interaction' in client:
            print(f"Last Interaction: {client['last_interaction']}")


def view_outreach_content(manager: ClientManager):
    """View generated outreach content."""
    clients = manager.get_selected_clients()

    if not clients:
        print("\nNo selected clients yet.")
        return

    print("\n" + "="*60)
    print("OUTREACH CONTENT")
    print("="*60)

    for i, client in enumerate(clients, 1):
        print(f"\n{i}. {client['company_name']}")

    print("\nEnter client number to view outreach content:")
    try:
        idx = int(input("> ").strip()) - 1
        if 0 <= idx < len(clients):
            client = clients[idx]
            prospect_id = client['id']

            history = manager.get_prospect_history(prospect_id)
            outreach = history.get('outreach_content', [])

            if not outreach:
                print(f"\nNo outreach content generated for {client['company_name']} yet.")
                return

            latest = outreach[-1]

            # Show email
            if 'email' in latest:
                print("\n" + "="*60)
                print("EMAIL")
                print("="*60)
                print(f"\nSubject: {latest['email']['subject']}")
                print(f"\n{latest['email']['body']}")

            # Show call script
            if 'call_script' in latest:
                print("\n" + "="*60)
                print("CALL SCRIPT - QUICK REFERENCE")
                print("="*60)
                qr = latest['call_script']['quick_reference']
                print(f"\nOpener:\n  {qr['opener']}")
                print(f"\nHook:\n  {qr['hook']}")
                print(f"\nQuestion:\n  {qr['question']}")
                print(f"\nClose:\n  {qr['close']}")

            # Show LinkedIn
            if 'linkedin_connection' in latest:
                print("\n" + "="*60)
                print("LINKEDIN CONNECTION REQUEST")
                print("="*60)
                print(f"\n{latest['linkedin_connection']}")

            # Save to file
            save_file = Path("output") / "outreach" / f"{client['company_name']}_outreach.txt"
            save_file.parent.mkdir(parents=True, exist_ok=True)

            with open(save_file, 'w', encoding='utf-8') as f:
                f.write(f"OUTREACH CONTENT FOR: {client['company_name']}\n")
                f.write("="*60 + "\n\n")

                if 'email' in latest:
                    f.write(f"EMAIL\n")
                    f.write(f"Subject: {latest['email']['subject']}\n\n")
                    f.write(f"{latest['email']['body']}\n\n")
                    f.write("="*60 + "\n\n")

                if 'call_script' in latest:
                    f.write(f"CALL SCRIPT\n")
                    f.write(f"{latest['call_script']['full_script']}\n\n")
                    f.write("="*60 + "\n\n")

                if 'linkedin_connection' in latest:
                    f.write(f"LINKEDIN CONNECTION\n")
                    f.write(f"{latest['linkedin_connection']}\n\n")

            print(f"\n[Saved to: {save_file}]")

    except (ValueError, IndexError):
        print("Invalid selection.")


def log_interaction_interactive(manager: ClientManager):
    """Log an interaction with a client."""
    clients = manager.get_selected_clients()

    if not clients:
        print("\nNo selected clients yet.")
        return

    print("\n" + "="*60)
    print("LOG INTERACTION")
    print("="*60)

    for i, client in enumerate(clients, 1):
        print(f"{i}. {client['company_name']} ({client['status']})")

    print("\nEnter client number:")
    try:
        idx = int(input("> ").strip()) - 1
        if 0 <= idx < len(clients):
            client = clients[idx]

            print(f"\nLogging interaction for: {client['company_name']}")

            print("\nInteraction type:")
            print("1. Email sent")
            print("2. Call made")
            print("3. Meeting scheduled")
            print("4. Follow-up sent")
            print("5. Other")
            type_choice = input("> ").strip()

            type_map = {
                '1': 'email_sent',
                '2': 'call_made',
                '3': 'meeting_scheduled',
                '4': 'followup_sent',
                '5': 'other'
            }
            interaction_type = type_map.get(type_choice, 'other')

            print("\nOutcome:")
            print("1. Responded/Interested")
            print("2. No response")
            print("3. Not interested")
            print("4. Meeting scheduled")
            print("5. Became client")
            outcome_choice = input("> ").strip()

            outcome_map = {
                '1': 'responded',
                '2': 'no_response',
                '3': 'not_interested',
                '4': 'meeting_scheduled',
                '5': 'became_client'
            }
            outcome = outcome_map.get(outcome_choice, 'unknown')

            print("\nNotes (optional, press Enter to skip):")
            notes = input("> ").strip() or None

            manager.log_interaction(
                client['id'],
                interaction_type,
                outcome,
                notes=notes
            )

            print(f"\n[OK] Interaction logged for {client['company_name']}")

    except (ValueError, IndexError):
        print("Invalid selection.")


def export_analytics(manager: ClientManager):
    """Export analytics data."""
    output_file = "data/clients/analytics_export.csv"
    manager.export_analytics_data(output_file)
    print(f"\n[OK] Analytics data exported to: {output_file}")


def main():
    print("\n" + "="*60)
    print("CLIENT MANAGEMENT SYSTEM")
    print("="*60)

    manager = ClientManager()

    while True:
        print("\nWhat would you like to do?")
        print("1. Load and select prospects from file")
        print("2. View selected clients")
        print("3. View outreach content")
        print("4. Log interaction")
        print("5. Export analytics")
        print("6. Exit")

        choice = input("\n> ").strip()

        if choice == '1':
            # Find latest prospects file
            prospects_dir = Path("output/prospects")
            if prospects_dir.exists():
                json_files = list(prospects_dir.glob("prospects_*.json"))
                if json_files:
                    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
                    print(f"\nUsing: {latest_file.name}")

                    prospects = load_prospects_from_file(str(latest_file))
                    select_prospects_interactive(prospects, manager)
                else:
                    print("\nNo prospect files found. Run prospecting first.")
            else:
                print("\nNo prospects directory found. Run prospecting first.")

        elif choice == '2':
            view_selected_clients(manager)

        elif choice == '3':
            view_outreach_content(manager)

        elif choice == '4':
            log_interaction_interactive(manager)

        elif choice == '5':
            export_analytics(manager)

        elif choice == '6':
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid choice. Try again.")


if __name__ == "__main__":
    # Update your details at the top of this file first!
    if YOUR_NAME == "Your Name":
        print("\n" + "="*60)
        print("SETUP REQUIRED")
        print("="*60)
        print("\nPlease edit manage_clients.py and update:")
        print("  - YOUR_NAME")
        print("  - YOUR_COMPANY")
        print("  - YOUR_TITLE")
        print("\nThen run this script again.")
        sys.exit(1)

    main()
