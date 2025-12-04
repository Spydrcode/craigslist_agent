# OpenAI Advanced Tools Integration

This document explains the OpenAI advanced capabilities integrated into the Craigslist Agent system.

## 🎨 Available Tools

### 1. **Web Search** (Real-time Company Research)

Uses OpenAI's web search capability to research companies in real-time.

**Methods:**

- `ClientAgent.research_company_web(company_name, focus_areas)` - Research a company via web
- `CompanyResearchAgent.research_company()` - Uses web search by default

**Example:**

```python
from agents import ClientAgent

client = ClientAgent()
research = client.research_company_web(
    company_name="TechCorp Inc",
    focus_areas=["company size", "recent growth", "hiring trends"]
)
```

### 2. **Function Calling** (Structured Data Extraction)

Uses JSON schemas to extract structured data from unstructured text.

**Methods:**

- `ClientAgent.extract_company_info_structured(text)` - Extract company data with schema
- `ParserAgent.parse_job()` - Uses structured extraction by default

**Example:**

```python
from agents import ParserAgent

parser = ParserAgent(use_structured_extraction=True)
parsed_job = parser.parse_job(job_description)
# Returns: ParsedJobPosting with validated fields
```

### 3. **File Search** (Historical Lead Intelligence)

Searches through historical lead data to find patterns and insights.

**Agent:** `FileSearchAgent`

**Methods:**

- `search_similar_companies(company_name, limit)` - Find similar companies
- `search_by_pain_point(pain_point, limit)` - Find companies with specific challenges
- `get_company_history(company_name)` - Retrieve full interaction history

**Example:**

```python
from agents import FileSearchAgent

file_agent = FileSearchAgent()

# Find companies similar to TechCorp
similar = file_agent.search_similar_companies("TechCorp", limit=5)

# Find companies with turnover issues
turnover_companies = file_agent.search_by_pain_point("high employee turnover", limit=10)

# Get full history
history = file_agent.get_company_history("TechCorp")
```

### 4. **Image Generation** (DALL-E 3)

Creates visual assets for sales presentations and reports.

**Methods:**

- `ClientAgent.generate_image(prompt, size, quality)` - Generate custom images
- `ClientAgent.generate_hiring_trend_visualization(company, job_count)` - Hiring charts
- `ClientAgent.generate_company_logo_concept(company, industry)` - Logo concepts

**Sizes:** `1024x1024`, `1792x1024`, `1024x1792`  
**Quality:** `standard`, `hd`

**Example:**

```python
from agents import ClientAgent

client = ClientAgent()

# Generate custom infographic
result = client.generate_image(
    prompt="Create a professional ROI infographic showing 300% ROI",
    size="1792x1024",
    quality="hd"
)
# Returns: {'url': '...', 'revised_prompt': '...'}
```

### 5. **Code Interpreter** (Data Analytics)

Executes Python code for data analysis, calculations, and insights.

**Methods:**

- `ClientAgent.analyze_hiring_data_with_code(job_postings)` - Analyze hiring patterns
- `ClientAgent.calculate_forecasta_roi(company_size, avg_salary, turnover_rate)` - Calculate ROI

**Example:**

```python
from agents import ClientAgent

client = ClientAgent()

# Analyze hiring patterns
job_data = [
    {"title": "Engineer", "location": "SF", "posted_date": "2024-01-01"},
    # ... more jobs
]
analysis = client.analyze_hiring_data_with_code(job_data)

# Calculate ROI
roi = client.calculate_forecasta_roi(
    company_size=250,
    avg_salary=75000,
    turnover_rate=0.18
)
```

## 🎨 Visualization Agent

High-level agent that combines image generation and code interpreter for sales assets.

**Agent:** `VisualizationAgent`

**Methods:**

- `create_prospect_presentation(company, industry, job_count, employee_count)` - Complete package
- `visualize_hiring_patterns(job_postings, company)` - Hiring dashboards
- `create_roi_calculator_visual(company_size, avg_salary, company_name)` - ROI visuals
- `create_comparison_chart(company_a, jobs_a, company_b, jobs_b)` - Comparison charts

**Example:**

```python
from agents import VisualizationAgent

viz = VisualizationAgent()

# Create complete presentation package
package = viz.create_prospect_presentation(
    company_name="TechCorp Solutions",
    industry="Software Development",
    job_count=45,
    employee_count=500
)

# Returns:
# {
#     'company': 'TechCorp Solutions',
#     'assets': {
#         'logo': 'output/visualizations/TechCorp_logo.png',
#         'hiring_trends': 'output/visualizations/TechCorp_hiring_trends.png',
#         'roi_projection': 'output/visualizations/TechCorp_roi.png'
#     },
#     'output_dir': 'output/visualizations'
# }
```

## 📡 Dashboard API Endpoints

The Flask dashboard (`leads_app.py`) provides REST endpoints for all visualization tools.

### Visualization Endpoints

**1. Create Presentation Package**

```bash
POST /api/visualize/presentation
{
    "company_name": "TechCorp",
    "industry": "Software",
    "job_count": 45,
    "employee_count": 500
}
```

**2. Create Hiring Dashboard**

```bash
POST /api/visualize/hiring-dashboard
{
    "company_name": "TechCorp",
    "job_postings": [
        {"title": "...", "location": "...", "posted_date": "..."}
    ]
}
```

**3. Create ROI Visual**

```bash
POST /api/visualize/roi
{
    "company_name": "TechCorp",
    "company_size": 250,
    "avg_salary": 75000
}
```

**4. Compare Companies**

```bash
POST /api/visualize/compare
{
    "company_a": "TechCorp",
    "jobs_a": 45,
    "company_b": "StartupXYZ",
    "jobs_b": 12
}
```

**5. Custom Image Generation**

```bash
POST /api/visualize/custom
{
    "prompt": "Create a professional business infographic...",
    "size": "1024x1024",
    "quality": "hd"
}
```

## 🧪 Testing

### Test Suites

**1. OpenAI Tools Test**

```bash
python test_openai_tools.py
```

Tests:

- Web search for company research
- Function calling for structured extraction
- File search for historical intelligence
- Integrated workflow using all three

**2. Visualization Test**

```bash
python test_visualization.py
```

Tests:

- Prospect presentation packages
- Hiring pattern dashboards
- ROI calculators
- Company comparisons
- Individual image generation
- Code interpreter analytics

## 📊 Integration with Existing Workflow

### CompanyResearchAgent Enhancement

Now uses web search FIRST before manual scraping:

```python
from agents import CompanyResearchAgent

researcher = CompanyResearchAgent(use_web_search=True)
profile = researcher.research_company(company_name="TechCorp")
# Uses OpenAI web search, enriches with manual scraping if needed
```

### ParserAgent Enhancement

Now uses structured extraction with JSON schemas:

```python
from agents import ParserAgent

parser = ParserAgent(use_structured_extraction=True)
parsed = parser.parse_job(job_description)
# Uses function calling for validated structured data
```

## 🔧 Configuration

All tools use the OpenAI API configured in `ClientAgent`:

```python
# In .env file
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-1106-preview  # or gpt-4, gpt-4-turbo, etc.
```

## 📁 Output Directories

- **Visualizations:** `output/visualizations/`
- **Historical Leads:** `output/leads/` (searched by FileSearchAgent)

## 🚀 Usage Patterns

### Pattern 1: Research → Visualize → Present

```python
from agents import CompanyResearchAgent, VisualizationAgent

# 1. Research company using web search
researcher = CompanyResearchAgent(use_web_search=True)
profile = researcher.research_company("TechCorp")

# 2. Create visual presentation
viz = VisualizationAgent()
package = viz.create_prospect_presentation(
    company_name="TechCorp",
    industry=profile.industry,
    job_count=len(profile.job_postings),
    employee_count=profile.company_size
)

# 3. Present to sales team
print(f"Presentation ready at: {package['output_dir']}")
```

### Pattern 2: Analyze → Calculate → Visualize ROI

```python
from agents import ClientAgent, VisualizationAgent

client = ClientAgent()
viz = VisualizationAgent()

# 1. Analyze hiring data
analysis = client.analyze_hiring_data_with_code(job_postings)

# 2. Calculate ROI
roi = client.calculate_forecasta_roi(
    company_size=250,
    avg_salary=75000
)

# 3. Create visual
roi_visual = viz.create_roi_calculator_visual(250, 75000, "TechCorp")
```

### Pattern 3: Historical Intelligence → Similar Companies

```python
from agents import FileSearchAgent

file_agent = FileSearchAgent()

# Find companies similar to known good leads
similar = file_agent.search_similar_companies("KnownGoodClient", limit=10)

# Find companies with specific pain points
turnover = file_agent.search_by_pain_point("employee retention issues", limit=5)
```

## 🎯 Best Practices

1. **Web Search:** Use for real-time company data (size, industry, growth)
2. **Function Calling:** Use for extracting structured data from job postings
3. **File Search:** Use to find patterns in historical successful leads
4. **Image Generation:** Use for sales presentations, not internal analysis
5. **Code Interpreter:** Use for complex calculations and data analytics

## ⚠️ Limitations

- **Web Search:** Results depend on web availability and recency
- **Image Generation:** DALL-E 3 has content policies, avoid sensitive requests
- **Code Interpreter:** Python execution is sandboxed, no external package installs
- **File Search:** Only searches `output/leads/` directory

## 📚 Further Reading

- [OpenAI Web Search Documentation](https://platform.openai.com/docs/guides/web-search)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [DALL-E 3 Documentation](https://platform.openai.com/docs/guides/images)
- [Code Interpreter Documentation](https://platform.openai.com/docs/guides/code-interpreter)
