"""Calculate actual API costs for processing jobs"""

# Example: Processing 400 jobs scraped from 2 pages
jobs_scraped = 400
companies_found = 50  # After grouping by company
qualified_companies = 20  # After filtering by growth score

print("\n" + "="*60)
print("COST BREAKDOWN FOR 400 JOBS (GPT-3.5 Turbo)")
print("="*60)

# Actual AI usage and costs
stages = [
    ("Stage 1: Scraping 400 jobs", 0, "No AI - just HTTP requests"),
    ("Stage 2: Parsing 400 jobs", jobs_scraped * 0.008, "Extract company, skills, pain points"),
    ("Stage 3: Growth analysis", 0, "Rule-based (no AI)"),
    ("Stage 4: Research 50 companies", companies_found * 0.04, "Web search + website analysis"),
    ("Stage 5: Pain point matching 20 companies", qualified_companies * 0.03, "Match to 2nmynd services"),
    ("Stage 6: ML Scoring", 0, "Local ML model (no API)"),
    ("Stage 7: Outreach generation 20 companies", qualified_companies * 0.02, "Email + scripts"),
]

total = 0
for stage, cost, description in stages:
    print(f"\n{stage}")
    print(f"  Cost: ${cost:.2f}")
    print(f"  What: {description}")
    total += cost

print("\n" + "="*60)
print(f"TOTAL COST PER RUN: ${total:.2f}")
print("="*60)

# Show what you get for that cost
print("\n📊 What you get:")
print(f"  ✓ {jobs_scraped} jobs scraped")
print(f"  ✓ {companies_found} companies identified")
print(f"  ✓ {qualified_companies} qualified leads")
print(f"  ✓ Full pain point analysis for each")
print(f"  ✓ Custom email + phone scripts for each")
print(f"\n💰 Cost per qualified lead: ${total/qualified_companies:.2f}")

# Compare to GPT-4
print("\n" + "="*60)
print("COST WITH GPT-4 (Better quality, slower)")
print("="*60)
gpt4_total = jobs_scraped * 0.025 + companies_found * 0.15 + qualified_companies * 0.08
print(f"Total: ${gpt4_total:.2f} (about {gpt4_total/total:.1f}x more expensive)")
print(f"Cost per qualified lead: ${gpt4_total/qualified_companies:.2f}")
