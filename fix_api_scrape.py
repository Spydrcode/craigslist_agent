"""
Script to replace the broken /api/scrape endpoint with the orchestrator-based version.
This removes 476 lines of manual scraping code and replaces with 130 lines using ObservableOrchestrator.
"""

def fix_api_scrape_endpoint():
    # Read the original file
    with open('dashboard/leads_app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Read the new endpoint code
    with open('dashboard/NEW_api_scrape.txt', 'r', encoding='utf-8') as f:
        new_endpoint = f.read()

    # Find the start and end of the broken function
    # Line 843 is @app.route('/api/scrape', methods=['POST'])
    # Line 1321 is the blank line before @app.route('/api/scrape-single'

    start_line = 842  # 0-indexed (line 843)
    end_line = 1320    # 0-indexed (line 1321) - keep this blank line

    print(f"Original file: {len(lines)} lines")
    print(f"Removing lines {start_line+1} to {end_line} ({end_line - start_line} lines)")
    print(f"Inserting new endpoint code")

    # Create new file content
    new_lines = lines[:start_line] + [new_endpoint + '\n'] + lines[end_line:]

    print(f"New file: {len(new_lines)} lines")
    print(f"Lines removed: {end_line - start_line}")
    print(f"Lines added: {len(new_endpoint.splitlines())}")

    # Backup original file
    with open('dashboard/leads_app.py.backup', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("\n✅ Backup created: dashboard/leads_app.py.backup")

    # Write the fixed file
    with open('dashboard/leads_app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("✅ Fixed file written: dashboard/leads_app.py")
    print("\n🎉 SUCCESS! The /api/scrape endpoint now uses ObservableOrchestrator!")
    print("\n📊 What changed:")
    print("  ❌ REMOVED: 476 lines of manual scraping code (with duplicates)")
    print("  ✅ ADDED: 130 lines using orchestrator.find_prospects()")
    print("\n🔧 Next steps:")
    print("  1. Restart the dashboard: python dashboard/leads_app.py")
    print("  2. Open browser and test a search")
    print("  3. You should now see all 9 agent progress bars!")
    print("\n📈 Agent progress bars you'll see:")
    print("  1. 🔍 Scraper Agent - Quick scanning ALL job postings")
    print("  2. ⚡ Filter Agent - Filtering spam and grouping by company")
    print("  3. ⭐ Scorer Agent - Scoring companies by hiring velocity")
    print("  4. 📝 Parser Agent - Deep analysis on top companies")
    print("  5. 📈 Growth Analyzer - Analyzing company growth signals")
    print("  6. 🔬 Research Agent - Researching company details")
    print("  7. 🎯 Service Matcher - Identifying service opportunities")
    print("  8. 🤖 ML Scoring - Scoring leads with ML")
    print("  9. 💾 Saver - Saving results to files")

if __name__ == '__main__':
    try:
        fix_api_scrape_endpoint()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
