# Client Management & Outreach System

Complete guide for managing prospects, generating outreach content, and tracking all interactions for analytics.

## Overview

After finding prospects with the prospecting system, you can now:

1. **Select prospects** to pursue
2. **Generate personalized outreach** (emails, call scripts, LinkedIn messages)
3. **Track all interactions** (emails sent, calls made, responses)
4. **Store everything** for future analytics

## Quick Start

### Step 1: Run Prospecting

```bash
python run_prospecting_simple.py
```

This creates a file like `output/prospects/prospects_20241202_114500.json`

### Step 2: Configure Your Details

Edit `manage_clients.py` lines 10-12:

```python
YOUR_NAME = "John Smith"
YOUR_COMPANY = "TechSolutions Inc"
YOUR_TITLE = "Solutions Consultant"
```

### Step 3: Manage Clients

```bash
python manage_clients.py
```

This opens an interactive menu to:
- Select prospects from your search
- Generate personalized outreach
- Track interactions
- Export analytics

## Features

### 1. Automated Email Generation

For each selected prospect, generates:

**Subject Line**: Attention-grabbing but professional
```
Subject: Quick question about TechCorp's growth
```

**Email Body**: Personalized based on:
- Their specific hiring activity
- Detected pain points
- Your service offerings
- Growth signals found

**Example**:
```
Hi [Name],

I noticed TechCorp is hiring 5 positions including Senior Software Engineer
and Engineering Manager. Companies scaling that quickly often struggle with
[specific pain point we detected].

We specialize in [relevant service] and have helped similar companies in
[their industry] solve this exact challenge.

Would you be open to a brief 15-minute call to explore if there's a fit?

Best regards,
John Smith
Solutions Consultant
TechSolutions Inc
```

### 2. Call Script Generation

Generates structured call scripts with:

**Opening**: Permission-based, not pushy
```
"Hi, this is John with TechSolutions. Is this [Decision Maker]?
Do you have 60 seconds? I promise this isn't a typical sales call."
```

**Pattern Interrupt**: References their specific situation
```
"I noticed you're hiring 5 positions, which usually means you're either
growing fast or having trouble keeping up with demand."
```

**Discovery Question**: Gets them talking
```
"How are you currently handling your data infrastructure as you scale?"
```

**Meeting Request**: Specific time options
```
"How does your calendar look for a quick 15-minute call this Thursday
at 10am, or would Friday afternoon work better?"
```

**Objection Handling**: Pre-written responses to common objections

### 3. LinkedIn Messages

Generates two types:

**Connection Request** (300 char max):
```
"Hi [Name], noticed TechCorp is expanding rapidly. We help companies in
[industry] optimize their [service area]. Would love to connect and
share some insights. Best, John"
```

**Direct Message** (if already connected):
Longer, more detailed message with specific value proposition.

### 4. Interaction Tracking

Log every interaction:

- **Email sent** → Automatically marks as "contacted"
- **Call made** → Records outcome (answered, voicemail, etc.)
- **Meeting scheduled** → Marks as "qualified"
- **Follow-ups** → Tracks all touchpoints
- **Became client** → Marks as "client" status

All data stored with timestamps for analytics.

### 5. Analytics Export

Export everything to CSV:

```csv
prospect_id, company_name, lead_score, status, total_interactions, outcome, growth_score, opportunity, ...
abc-123, TechCorp, 87.3, client, 5, became_client, 0.89, AI/ML Consulting, ...
```

Perfect for:
- Analyzing which signals predict success
- Tracking conversion rates
- Optimizing outreach strategies
- Reporting to stakeholders

## File Structure

All data automatically saved to:

```
data/clients/
├── prospects.json              ← All prospects from searches
├── selected_clients.json       ← Clients you chose to pursue
├── interactions.json           ← All logged interactions
└── outreach_content.json       ← Generated emails/scripts

output/outreach/
└── [CompanyName]_outreach.txt  ← Formatted outreach content
```

## Complete Workflow

### Week 1: Prospecting

**Monday Morning**:
```bash
python run_prospecting_simple.py
```
- Finds 10-20 qualified prospects
- Saves to `output/prospects/`

### Week 1: Selection & Generation

**Monday Afternoon**:
```bash
python manage_clients.py
```

1. Choose option 1: "Load and select prospects"
2. Select your top 5 prospects (e.g., enter: 1,2,3,4,5)
3. System generates:
   - Personalized email for each
   - Custom call script for each
   - LinkedIn messages for each
4. All saved automatically

### Week 1: Outreach

**Tuesday-Thursday**:

For each prospect:

1. Choose option 3: "View outreach content"
2. Copy email → Send via your email client
3. If no response in 48 hours, make call using script
4. After each action, choose option 4: "Log interaction"

### Week 2: Follow-up

For prospects who responded:

1. Schedule meetings
2. Log as "meeting_scheduled"
3. After meeting, log outcome
4. If they become clients, log as "became_client"

### End of Month: Analytics

```bash
python manage_clients.py
```
Choose option 5: "Export analytics"

Review:
- Conversion rates
- Which signals predicted success
- Which services were most interesting
- Response times

## Interaction Types

When logging interactions, use these types:

- **email_sent**: Initial or follow-up email sent
- **call_made**: Phone call attempted or completed
- **meeting_scheduled**: Demo or discovery call scheduled
- **followup_sent**: Follow-up communication sent
- **other**: Any other interaction

## Outcomes

When logging, record these outcomes:

- **responded**: They replied (email or called back)
- **no_response**: No reply yet
- **not_interested**: Explicitly said no
- **meeting_scheduled**: They agreed to meet
- **became_client**: They signed on as a client

## Customization

### Change Email Tone

Edit `manage_clients.py` line where email is generated:

```python
content = manager.generate_outreach_content(
    prospect.lead_id,
    YOUR_NAME,
    YOUR_COMPANY,
    YOUR_TITLE,
    include_email=True,
    include_call_script=True,
    include_linkedin=True
)
```

Available tones (in `OutreachAgent`):
- `professional` (default)
- `casual`
- `direct`

### Add Custom Fields

Edit `client_manager.py` to track additional data:

```python
prospect_data['custom_field'] = value
```

### Change Storage Location

Edit `manage_clients.py` line 18:

```python
manager = ClientManager(data_dir="your/custom/path")
```

## Analytics Insights

After collecting data, you can analyze:

### Conversion by Growth Score

```python
import pandas as pd

df = pd.read_csv('data/clients/analytics_export.csv')

# Group by growth score ranges
df['growth_bucket'] = pd.cut(df['growth_score'], bins=[0, 0.3, 0.5, 0.7, 1.0])
conversion_by_growth = df.groupby('growth_bucket')['status'].apply(
    lambda x: (x == 'client').sum() / len(x)
)
```

### Best Opportunities

```python
# Which service opportunities convert best?
df.groupby('top_opportunity')['status'].apply(
    lambda x: (x == 'client').sum() / len(x)
).sort_values(ascending=False)
```

### Response Rates

```python
# Email response rates
df['responded'] = df['total_interactions'] > 0
response_rate = df['responded'].mean()
```

## Best Practices

### 1. Daily Routine

- **Morning**: Check responses, log interactions
- **Afternoon**: Reach out to 3-5 new prospects
- **Evening**: Follow up with active conversations

### 2. Prioritization

Focus on:
1. URGENT tier prospects first
2. Prospects with multiple service opportunities
3. Companies with high growth scores (0.7+)

### 3. Personalization

Always:
- Reference specific job postings
- Mention their growth stage
- Use evidence from their listings
- Keep it about them, not you

### 4. Persistence

Average B2B sale requires 5-7 touchpoints:
1. Email
2. Follow-up email (48 hours)
3. Call attempt
4. LinkedIn connection
5. Value-add content share
6. Final email
7. Call attempt #2

### 5. Data Hygiene

- Log every interaction immediately
- Be consistent with outcome codes
- Add notes with key details
- Export analytics monthly

## Troubleshooting

### "No prospects found"

Run prospecting first:
```bash
python run_prospecting_simple.py
```

### "Failed to generate content"

Check:
- OpenAI API key in `.env`
- Internet connection
- API credits available

### "Cannot load prospect"

The JSON file may be corrupted. Check:
```bash
python -m json.tool output/prospects/prospects_XXX.json
```

### Slow content generation

Normal! AI generation takes 3-5 seconds per prospect.

## Advanced Features

### Batch Processing

Process multiple prospects at once (already implemented in interactive tool).

### Template Customization

Edit `agents/outreach_agent.py` to modify email/script templates.

### CRM Integration

Export `selected_clients.json` and import to your CRM:
- HubSpot: Use their API
- Salesforce: Use their API
- Pipedrive: Use CSV import

### Automated Follow-ups

Coming soon: Scheduled email follow-ups based on interaction history.

## Security Notes

- All data stored locally (no external database required)
- Sensitive client data in `data/clients/` - don't commit to git
- API keys in `.env` - never share or commit

## Summary

Your complete client workflow:

1. ✅ **Find** prospects with `run_prospecting_simple.py`
2. ✅ **Select** best prospects with `manage_clients.py`
3. ✅ **Generate** personalized outreach automatically
4. ✅ **Track** every interaction with timestamps
5. ✅ **Analyze** what works with analytics export

**Everything saved for future analysis!**

---

Questions? Check the generated outreach content in `output/outreach/` for examples.
