# Advanced Growth Signal Detection

## Overview

This document explains the sophisticated **multi-signal intelligence system** for identifying companies that are genuinely growing and need your services.

This goes far beyond simple "job count" metrics to detect **real operational signals** that indicate:
- Expansion
- Revenue growth
- Capacity stress
- Operational maturity

---

## New Scoring Model

### Score Weighting (Total 100 points)

| Component | Weight | Max Points | Description |
|-----------|--------|------------|-------------|
| **Growth Signals** | 40% | 100 pts | Cross-functional hiring, revenue roles, capacity stress |
| **Hiring Velocity** | 30% | 100 pts | Number of active job postings |
| **Expansion Indicators** | 20% | 100 pts | Explicit expansion language |
| **Operational Maturity** | 10% | 100 pts | Tech adoption, structured processes |

### Old vs New

**Old System (Simple):**
- 70% = Job count
- 30% = Tech keywords

**New System (Sophisticated):**
- 40% = Multi-signal growth detection
- 30% = Job count
- 20% = Expansion language
- 10% = Operational maturity

---

## The 10 Advanced Growth Indicators

### 1. ⭐ Multiple Roles Across Functions (Cross-Functional Hiring)

**What it means:** Company posting in multiple categories = expanding operations

**Examples:**
- Marketing + Operations + Drivers
- Sales + Customer Service + Technicians
- Admin + Warehouse + Dispatchers

**Detection:**
```python
# Detect if jobs span 2+ categories:
categories = ['sales', 'marketing', 'operations', 'admin', 'drivers',
              'technicians', 'customer_service', 'fulfillment', 'engineering']

if len(detected_categories) >= 2:
    score += 30 points  # Cross-functional hiring bonus
    multiplier *= 1.5x  # 50% bonus multiplier
```

**Why it matters:** Companies expanding ONE function might just be replacing turnover. Companies expanding MULTIPLE functions are scaling the entire business.

**Score Impact:** 30 pts (of 100 in Growth Signals)

---

### 2. 🔥 Expansion Language in Listings

**Gold Standard Signal** - These phrases are the strongest indicators:

#### Direct Expansion
- "We're expanding"
- "Opening a new location"
- "New office"
- "New branch"

#### Demand-Driven
- "Due to increased demand"
- "High demand"
- "Rapidly growing"
- "High-volume"

#### Scaling
- "Scaling operations"
- "We are scaling"

#### Contract/Client Growth
- "New contracts"
- "New clients"
- "Immediate hires"

#### Territory Expansion
- "Expanding service area"
- "New territory"
- "Serving new area"

**Detection:**
```python
expansion_keywords = [
    "we're expanding", "opening a new location",
    "due to increased demand", "scaling operations",
    "new contracts", "expanding route"
]

if any(keyword in job_text):
    score += 50 points
    multiplier *= 2.0x  # DOUBLE the score
```

**Why it matters:** Explicit growth language means the company is TELLING YOU they're growing. This is gold.

**Score Impact:** 50 pts (of 100 in Expansion Indicators) + 2x multiplier

---

### 3. 💰 Revenue-Driving Roles

**What it means:** Jobs that directly generate or fulfill revenue

**Revenue Role Types:**

| Category | Keywords | Why Important |
|----------|----------|---------------|
| **Sales** | Sales rep, account executive, BDR | Direct revenue generation |
| **Customer Success** | Account manager, client success | Revenue retention |
| **Appointment Setters** | Lead gen, appointment coordinator | Pipeline growth |
| **Technicians** | Field tech, service tech, installer | Fulfillment capacity |
| **Drivers** | Delivery driver, route driver | Fulfillment capacity |
| **Dispatchers** | Dispatch coordinator, route planner | Operations scaling |
| **Project Coordinators** | PM, operations coordinator | Contract fulfillment |
| **Fulfillment** | Warehouse, packer, shipping | Order volume |

**Detection:**
```python
revenue_roles_found = 0

if "sales rep" in title:
    revenue_roles_found += 1
if "technician" in title:
    revenue_roles_found += 1
if "driver" in title:
    revenue_roles_found += 1

score += revenue_roles_found * 10  # Up to 30 pts
```

**Why it matters:** These roles directly correlate with revenue. More revenue roles = more customers/contracts = growth.

**Score Impact:** 10 pts per unique role type (max 30 pts)

---

### 4. 📈 High-Volume Hiring

**What it means:** Hiring many people at once = operational scaling

**Patterns to Detect:**

```python
# Look for numbers in job text:
"Hiring 10+ movers"           → 10+
"Need 5 technicians ASAP"     → 5
"Looking for 15 positions"    → 15
"Multiple openings"           → High volume indicator
```

**Detection:**
```python
patterns = [
    r'hiring (\d+)\+',      # "hiring 10+"
    r'need (\d+)',          # "need 5 technicians"
    r'(\d+) positions',     # "15 positions"
]

if number >= 5:
    score += 20 points
```

**Why it matters:** High-volume hiring = operational capacity expansion.

**Score Impact:** 20 pts (of 100 in Growth Signals)

---

### 5. 💵 Wage Premium (Future Enhancement)

**What it means:** Paying above market rate to attract talent fast

**Indicators:**
- Higher wages than similar postings
- Sign-on bonuses
- Overtime guarantees
- Benefits rarely offered in industry

**Future Detection:**
```python
# Compare posted wage to median for category
if posted_wage > median_wage * 1.2:
    score += bonus
```

**Why it matters:** Companies in growth phase pay premiums to hire fast.

**Status:** ⏳ Planned for future implementation

---

### 6. 🗺️ Multi-Location Expansion

**What it means:** Hiring in multiple locations = geographic expansion

**Detection:**
```python
locations = set()
for job in jobs:
    locations.add(job.location)

if len(locations) >= 2:
    score += 30 points
```

**Keywords to Detect:**
- "Now hiring for City B"
- "Serving new area"
- "Expanding route coverage"
- "All counties"
- "Multiple service zones"

**Why it matters:** Geographic expansion = significant growth investment.

**Score Impact:** 30 pts (of 100 in Expansion Indicators)

---

### 7. 🚨 Operational Overload (Capacity Stress)

**CRITICAL SIGNAL** - Shows real revenue pressure

**Stress Indicators:**

| Phrase | What It Means |
|--------|---------------|
| "Need people to start immediately" | Behind on fulfillment |
| "We are behind on work" | Backlog exists |
| "Can't keep up with demand" | Demand > capacity |
| "Tons of work available" | Revenue overflow |
| "Overtime available" | Working beyond capacity |
| "All the work you can handle" | Unlimited demand |

**Detection:**
```python
stress_signals = [
    "start immediately", "behind on work",
    "can't keep up", "tons of work",
    "overtime available"
]

stress_count = sum(1 for signal in stress_signals if signal in text)

score += stress_count * 10  # Up to 20 pts
if stress_count >= 2:
    multiplier *= 1.3x
```

**Why it matters:** Capacity stress = they're DESPERATE for help = high willingness to pay.

**Score Impact:** 10 pts per signal (max 20 pts) + 1.3x multiplier

---

### 8. 🔧 Tech Adoption & Maturity

**What it means:** Upgrading from manual → tech-enabled = scaling with systems

**Maturity Signals:**

| Category | Tools | Growth Indicator |
|----------|-------|------------------|
| **CRM** | Salesforce, HubSpot, Zoho | Systematic sales process |
| **Scheduling** | Dispatch software, route planning | Operations scaling |
| **Accounting** | QuickBooks, Xero, ERP | Financial sophistication |
| **Automation** | AI tools, workflow automation | Efficiency focus |
| **Data** | Excel, reporting, analytics | Data-driven decisions |

**Detection:**
```python
maturity_signals = {
    'crm': ['salesforce', 'hubspot', 'crm'],
    'scheduling': ['dispatch software', 'route planning'],
    'accounting': ['quickbooks', 'xero'],
    'automation': ['ai tools', 'automated'],
}

score += signals_found * 10  # Up to 40 pts
```

**Why it matters:** Companies growing enough to adopt tech are serious about scaling.

**Score Impact:** 10 pts per tool category (max 40 pts)

---

### 9. 📋 Structured Recruiting

**What it means:** Moving from chaotic hiring → systematic process

**Indicators:**
- "Scheduled interview days"
- "Pre-screen questions"
- "Training programs"
- "Onboarding process"
- "Career advancement paths"
- "Performance reviews"

**Detection:**
```python
structured_signals = [
    'scheduled interview', 'training program',
    'onboarding', 'career path'
]

if any(signal in text):
    score += 40 points
```

**Why it matters:** Structure = company maturing and building systems to scale.

**Score Impact:** 40 pts (of 100 in Maturity)

---

### 10. 🔁 Contact Pattern Recognition (Cross-Posting Detection)

**What it means:** Same phone/email across multiple postings = sustained hiring

**Detection:**
```python
# Extract contact info from all jobs
phone_numbers = extract_phones(all_jobs)
emails = extract_emails(all_jobs)

# Future: Track across time to detect repeat hiring
if same_contact_across_30_days:
    score += bonus
```

**Why it matters:** Repeat posting = sustained demand (not one-time hiring).

**Status:** ⏳ Planned for future implementation

---

## Scoring Examples

### Example 1: Hot Lead - Construction Company

**Jobs Posted:**
1. "Project Coordinator - Expanding to 3 new states!"
2. "Technician - We're overwhelmed with work, start immediately"
3. "Dispatcher - High-volume operation, need help ASAP"
4. "Sales Rep - Due to new contracts"
5. "Admin - Onboarding coordinator for new hires"

**Detected Signals:**
- ✅ Cross-functional hiring (5 different roles)
- ✅ Expansion language ("expanding to 3 new states", "due to new contracts")
- ✅ Revenue roles (sales, technician, dispatcher, project coordinator)
- ✅ Capacity stress ("overwhelmed", "start immediately", "need help ASAP")
- ✅ Maturity (structured onboarding)

**Score Calculation:**
```
Hiring Velocity:   5 jobs = 70 pts * 0.30 = 21.0
Growth Signals:
  - Cross-functional: 30 pts
  - Revenue roles: 40 pts (4 types)
  - Stress: 20 pts (3 signals)
  - Total: 90 pts * 0.40 = 36.0
Expansion:
  - Language: 50 pts
  - Total: 50 pts * 0.20 = 10.0
Maturity:
  - Structured recruiting: 40 pts
  - Total: 40 pts * 0.10 = 4.0

Base Score: 21.0 + 36.0 + 10.0 + 4.0 = 71.0

Multipliers:
  - Expansion language: 2.0x
  - Cross-functional: 1.5x
  - Stress signals: 1.3x

Final Score: 71.0 * 2.0 * 1.5 * 1.3 = 276.9 (capped at 100)

TIER: HOT (100/100) 🔥🔥🔥
```

**Why pursue:**
- Explicit expansion language = real growth
- Cross-functional hiring = entire business scaling
- Capacity stress = desperate for help
- Maturity signals = has budget and systems

---

### Example 2: Qualified Lead - Software Company

**Jobs Posted:**
1. "Senior Backend Engineer - Scaling to handle 10x traffic"
2. "DevOps Engineer - Moving to microservices"
3. "Customer Success Manager - New enterprise clients"

**Detected Signals:**
- ✅ Hiring velocity (3 jobs)
- ✅ Expansion language ("scaling", "new enterprise clients")
- ✅ Revenue role (customer success)
- ✅ Tech maturity (microservices, scaling)

**Score Calculation:**
```
Hiring Velocity:   3 jobs = 50 pts * 0.30 = 15.0
Growth Signals:
  - Revenue roles: 10 pts
  - Total: 10 pts * 0.40 = 4.0
Expansion:
  - Language: 50 pts
  - Total: 50 pts * 0.20 = 10.0
Maturity:
  - Tech adoption: 20 pts
  - Total: 20 pts * 0.10 = 2.0

Base Score: 15.0 + 4.0 + 10.0 + 2.0 = 31.0

Multipliers:
  - Expansion language: 2.0x

Final Score: 31.0 * 2.0 = 62.0

TIER: QUALIFIED (62/100) ⭐
```

**Why pursue:**
- Explicit scaling language
- Technical sophistication
- Growing client base

---

### Example 3: Skip - Single Job, No Signals

**Jobs Posted:**
1. "Web Developer - Update our website"

**Detected Signals:**
- ❌ Only 1 job
- ❌ No expansion language
- ❌ No revenue roles
- ❌ No stress signals
- ❌ No maturity signals

**Score:**
```
Hiring Velocity:   1 job = 0 pts * 0.30 = 0.0
Growth Signals:    0 pts * 0.40 = 0.0
Expansion:         0 pts * 0.20 = 0.0
Maturity:          0 pts * 0.10 = 0.0

Final Score: 0.0

TIER: SKIP (0/100) ❌
```

**Why skip:**
- No growth signals
- Single job = likely replacement hiring
- No urgency

---

## Implementation in System

### File: `agents/company_scorer_enhanced.py`

**Key Features:**
1. **Expansion Keywords** - 50+ expansion phrases
2. **Revenue Role Detection** - 8 role categories
3. **Stress Signal Detection** - 15+ capacity indicators
4. **Maturity Detection** - 5 tool categories
5. **Cross-Functional Analysis** - 9 job categories
6. **High-Volume Patterns** - Regex for "hiring X+"
7. **Multi-Location Detection** - Geographic expansion
8. **Contact Extraction** - Phone/email for cross-posting

### Usage:

```python
from agents.company_scorer_enhanced import EnhancedCompanyScoringAgent

scorer = EnhancedCompanyScoringAgent()
scored_companies = scorer.score_companies(company_jobs_dict)

# Results include:
for company in scored_companies:
    print(f"{company.company_name}: {company.total_score}/100")
    print(f"  Tier: {company.tier}")
    print(f"  Growth Signals:")
    print(f"    - Cross-functional: {company.growth_signals.cross_functional_hiring}")
    print(f"    - Expansion language: {company.growth_signals.expansion_language_found}")
    print(f"    - Revenue roles: {company.growth_signals.revenue_roles}")
    print(f"    - Stress signals: {company.growth_signals.capacity_stress_signals}")
```

---

## Validation & Testing

### Test Cases to Run:

1. **Multi-functional company** - Should score HIGH
2. **Expansion language company** - Should get 2x multiplier
3. **Single job company** - Should score LOW
4. **Stress signals** - Should get 1.3x multiplier
5. **Cross-functional + expansion** - Should get 3x multiplier (1.5 * 2.0)

### Expected Outcomes:

| Scenario | Expected Score | Expected Tier |
|----------|----------------|---------------|
| 5+ jobs, expansion language, cross-functional | 80-100 | HOT |
| 3-4 jobs, stress signals | 60-79 | QUALIFIED |
| 2-3 jobs, tech stack | 40-59 | POTENTIAL |
| 1 job, no signals | 0-39 | SKIP |

---

## Future Enhancements

### Phase 2 Additions:
1. **Wage Premium Detection** - Compare to market rates
2. **Cross-Posting Tracking** - Same contact over 30 days
3. **Industry Classification** - Better role categorization
4. **Location Clustering** - Detect regional expansion patterns
5. **Time Series Analysis** - Track hiring velocity changes
6. **Sentiment Analysis** - Detect urgency in language
7. **Image Analysis** - Extract info from job posting images

### Machine Learning Potential:
- Train model on conversion data
- Learn which signals predict best prospects
- Adjust weights dynamically
- Predict deal size based on signals

---

## Summary

The new **Enhanced Growth Signal Detection** system provides:

✅ **40% weight on real growth signals** (vs 30% on simple job count)
✅ **2x-3x multipliers** for strong expansion language
✅ **Cross-functional detection** for scaling businesses
✅ **Capacity stress detection** for desperate companies
✅ **Operational maturity signals** for sophisticated buyers

This results in **higher quality leads** with **better conversion rates** because we're detecting REAL operational growth, not just hiring volume.
