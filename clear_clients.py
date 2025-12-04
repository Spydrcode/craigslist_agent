"""
Simple script to clear all test clients from the database.
Run this to start fresh with proper company names.
"""

import json
import shutil
from pathlib import Path

# Paths
clients_dir = Path('data/clients')
backup_dir = Path('data/clients_backup')

def clear_clients():
    """Clear all client files and create backup."""

    # Create backup directory
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup all client files
    client_files = list(clients_dir.glob('client_*.json'))
    all_clients_file = clients_dir / 'all_clients.json'

    if client_files:
        print(f"📦 Backing up {len(client_files)} client files to {backup_dir}")
        for client_file in client_files:
            shutil.copy2(client_file, backup_dir / client_file.name)

        if all_clients_file.exists():
            shutil.copy2(all_clients_file, backup_dir / 'all_clients.json')

    # Delete all client files
    for client_file in client_files:
        client_file.unlink()
        print(f"  ✓ Deleted {client_file.name}")

    # Reset all_clients.json
    with open(all_clients_file, 'w') as f:
        json.dump([], f, indent=2)

    print(f"\n✅ Cleared {len(client_files)} clients")
    print(f"📁 Backup saved to: {backup_dir}")
    print("\nYou can now add clients with proper company names!")

if __name__ == '__main__':
    print("🗑️  Clearing all test clients...\n")
    clear_clients()
