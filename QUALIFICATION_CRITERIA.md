# Company Qualification Criteria

## What Makes a Company a Good Prospect?

### **Tier 1: Strong Buy Signals (Most Valuable)**

#### 1. **Multiple Active Job Postings** (Weight: 30%)
- **3-5 jobs**: Steady growth
- **6-10 jobs**: Rapid expansion
- **10+ jobs**: Aggressive scaling

**Why it matters**: Companies hiring multiple people simultaneously have urgent needs and budget approved.

#### 2. **Technical Debt Indicators** (Weight: 25%)
Job descriptions mention:
- "Legacy system" / "outdated tech stack"
- "Modernize" / "migrate" / "refactor"
- "Technical debt"
- "Scaling issues" / "performance problems"
- "Rewrite" / "rebuild"

**Why it matters**: These are pain points YOU can solve with software services.

#### 3. **Growth Stage Keywords** (Weight: 20%)
- "Startup" / "early stage"
- "Series A/B/C funded"
- "Scaling rapidly"
- "Expanding team"
- "New market"
- "Recent funding"

**Why it matters**: Growing companies have budget and urgency.

#### 4. **Tech Stack Signals** (Weight: 15%)
Modern tech = budget + sophistication:
- Cloud (AWS, GCP, Azure)
- Modern frameworks (React, Vue, Next.js)
- Microservices
- Kubernetes, Docker
- CI/CD pipelines

**Why it matters**: Companies using modern tech understand value of external expertise.

#### 5. **Seniority Mix** (Weight: 10%)
Hiring both:
- Senior roles (architects, staff engineers, tech leads)
- Junior roles (engineers, developers)

**Why it matters**: Building a complete team = serious investment in growth.

---

### **Tier 2: Moderate Signals**

#### 6. **Remote/Distributed Team**
- Remote-first positions
- "Distributed team"
- Multiple locations

**Why it matters**: Remote companies often need external help with infrastructure, processes, tooling.

#### 7. **Product Keywords**
- "SaaS" / "platform"
- "B2B" / "enterprise"
- "Product-led growth"

**Why it matters**: Product companies have recurring revenue and long-term budget.

#### 8. **Specific Pain Points in Job Descriptions**
- "Overwhelmed with requests"
- "Backlog"
- "Need to move faster"
- "Quality issues"
- "Slow deployment"

**Why it matters**: These are EXPLICIT problems you can solve.

---

### **Tier 3: Red Flags (Disqualify)**

#### ❌ **Avoid These Companies:**

1. **Agencies/Consulting Firms**
   - They're your competitors
   - "Agency" / "consulting" in name

2. **Staffing/Recruiting Companies**
   - Not end clients
   - Just middlemen

3. **Non-Tech Companies with 1-2 Tech Jobs**
   - Retail, restaurants, real estate with "website developer"
   - Low tech sophistication
   - Small budgets

4. **Spam Indicators**
   - "Make $X/week"
   - "Work from home - no experience"
   - MLM keywords

5. **Government/Non-Profit (unless specifically targeting)**
   - Long sales cycles
   - Low budgets
   - Procurement complexity

---

## **Scoring Formula**

### Base Score (0-100):

```
Score =
  (job_count * 5) +                    // Max 50 points (10+ jobs)
  (technical_debt_score * 25) +        // Max 25 points
  (growth_signals * 20) +              // Max 20 points
  (tech_stack_modernity * 15) +        // Max 15 points
  (seniority_mix_bonus * 10)           // Max 10 points
```

### Multipliers:

- **2x** if "funded" or "series A/B/C" mentioned
- **1.5x** if specific pain points identified
- **0.5x** if agency/consulting
- **0x** if spam detected

---

## **Qualification Tiers**

| Score | Tier | Action |
|-------|------|--------|
| 80-100 | 🔥 **HOT LEAD** | Priority analysis, immediate outreach |
| 60-79 | ⭐ **QUALIFIED** | Full analysis, personalized outreach |
| 40-59 | ✅ **POTENTIAL** | Basic analysis, template outreach |
| 0-39 | ❌ **SKIP** | Don't waste time |

---

## **Service Matching Logic**

Based on job descriptions, offer these services:

### If they mention "legacy" or "technical debt":
- **Code modernization**
- **Architecture review**
- **Tech stack migration**

### If they mention "scaling" or "performance":
- **Performance optimization**
- **Cloud architecture**
- **Database optimization**

### If they mention "slow deployment" or "manual process":
- **CI/CD setup**
- **DevOps automation**
- **Infrastructure as code**

### If hiring multiple frontend devs:
- **UI/UX optimization**
- **Component library**
- **Design system**

### If hiring multiple backend devs:
- **API development**
- **Microservices architecture**
- **Backend scalability**

---

## **Data Points to Extract**

For each qualified company, we need:

1. **Company name** (extracted from jobs)
2. **Total job count**
3. **Job titles** (shows what they're building)
4. **Tech stack** (from job requirements)
5. **Pain points** (from job descriptions)
6. **Growth stage** (startup vs established)
7. **Location** (remote vs specific city)
8. **Industry** (if identifiable)

---

## **Example: High-Quality Lead**

**Company**: TechStartup Inc.

**Signals**:
- ✅ 7 active job postings
- ✅ Job titles: "Senior Backend Engineer", "DevOps Engineer", "Engineering Manager", "Junior Frontend Developer"
- ✅ Keywords found: "scaling rapidly", "legacy monolith", "migrate to microservices"
- ✅ Tech stack: React, Node.js, PostgreSQL, AWS
- ✅ Mentioned: "Series A funded"

**Score**: 85/100 (🔥 HOT LEAD)

**Recommended Services**:
- Microservices migration
- DevOps/CI/CD setup
- Cloud architecture consulting

**Why pursue**: Clear pain point (legacy system), budget (funded), urgency (7 jobs = rapid growth)

---

## **Example: Low-Quality Lead**

**Company**: Bob's Pizza Shop

**Signals**:
- ❌ 1 job posting
- ❌ Job title: "Website developer needed part-time"
- ❌ Description: "Update our Wix site, $15/hr"
- ❌ No tech stack mentioned
- ❌ No growth indicators

**Score**: 10/100 (❌ SKIP)

**Why avoid**: Low budget, low sophistication, not a tech company

