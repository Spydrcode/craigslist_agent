# OpenAI Tools - Quick Reference Card

## 🎯 When to Use Each Tool

| Tool                 | Use Case                       | Example                                  |
| -------------------- | ------------------------------ | ---------------------------------------- |
| **Web Search**       | Real-time company intelligence | Company size, industry, recent news      |
| **Function Calling** | Extract structured data        | Parse job postings into validated fields |
| **File Search**      | Find historical patterns       | Similar companies, common pain points    |
| **Image Generation** | Sales presentations            | Logos, charts, infographics              |
| **Code Interpreter** | Data analysis                  | ROI calculations, hiring trends          |

---

## 📚 Quick Code Snippets

### Web Search - Research Company

```python
from agents import CompanyResearchAgent

researcher = CompanyResearchAgent(use_web_search=True)
profile = researcher.research_company("TechCorp")
```

### Function Calling - Structured Extraction

```python
from agents import ParserAgent

parser = ParserAgent(use_structured_extraction=True)
parsed = parser.parse_job(job_description)
```

### File Search - Find Similar Companies

```python
from agents import FileSearchAgent

file_agent = FileSearchAgent()
similar = file_agent.search_similar_companies("GoodClient", limit=5)
```

### Image Generation - Create Presentation

```python
from agents import VisualizationAgent

viz = VisualizationAgent()
package = viz.create_prospect_presentation(
    company_name="TechCorp",
    industry="Software",
    job_count=45,
    employee_count=500
)
```

### Code Interpreter - Calculate ROI

```python
from agents import ClientAgent

client = ClientAgent()
roi = client.calculate_forecasta_roi(
    company_size=250,
    avg_salary=75000,
    turnover_rate=0.18
)
```

---

## 🌐 Dashboard API Quick Reference

### Create Presentation Package

```bash
curl -X POST http://localhost:3000/api/visualize/presentation \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp",
    "industry": "Software",
    "job_count": 45,
    "employee_count": 500
  }'
```

### Generate Custom Image

```bash
curl -X POST http://localhost:3000/api/visualize/custom \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Professional business infographic showing 300% ROI",
    "size": "1792x1024",
    "quality": "hd"
  }'
```

### Create ROI Visual

```bash
curl -X POST http://localhost:3000/api/visualize/roi \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp",
    "company_size": 250,
    "avg_salary": 75000
  }'
```

---

## 🔑 Key Classes & Methods

### ClientAgent (Core AI Wrapper)

- `research_company_web(company_name, focus_areas)` - Web search
- `extract_company_info_structured(text)` - Function calling
- `generate_image(prompt, size, quality)` - DALL-E 3
- `analyze_hiring_data_with_code(job_postings)` - Code interpreter
- `calculate_forecasta_roi(company_size, avg_salary, turnover_rate)` - ROI

### VisualizationAgent (High-Level Visual Creation)

- `create_prospect_presentation(...)` - Complete package
- `visualize_hiring_patterns(job_postings, company)` - Dashboard
- `create_roi_calculator_visual(...)` - ROI visual
- `create_comparison_chart(...)` - Compare companies

### FileSearchAgent (Historical Intelligence)

- `search_similar_companies(company_name, limit)` - Similar companies
- `search_by_pain_point(pain_point, limit)` - Pain point search
- `get_company_history(company_name)` - Full history

### CompanyResearchAgent (Enhanced with Web Search)

- `research_company(company_name)` - Uses web search first

### ParserAgent (Enhanced with Structured Extraction)

- `parse_job(job_description)` - Uses function calling

---

## 📊 Image Generation Sizes

| Size        | Dimensions | Use Case                          |
| ----------- | ---------- | --------------------------------- |
| `1024x1024` | Square     | Social media, icons, logos        |
| `1792x1024` | Landscape  | Presentations, dashboards, slides |
| `1024x1792` | Portrait   | Mobile, infographics, posters     |

**Quality:** `standard` (default, fast) or `hd` (higher quality, slower)

---

## 💰 Cost Estimates

| Tool             | Cost         | Notes                     |
| ---------------- | ------------ | ------------------------- |
| Web Search       | Included     | Part of GPT-4 API pricing |
| Function Calling | Included     | No additional cost        |
| File Search      | Free         | Local file system         |
| Image Generation | ~$0.04-$0.08 | Per image (size/quality)  |
| Code Interpreter | Included     | Part of API pricing       |

**Typical Complete Workflow:** ~$0.20-$0.40 per lead (with visuals)

---

## 🧪 Testing

**Test OpenAI Tools:**

```bash
python test_openai_tools.py
```

**Test Visualizations:**

```bash
python test_visualization.py
```

**End-to-End Example:**

```bash
python example_end_to_end.py
```

---

## 📁 Output Directories

- **Visualizations:** `output/visualizations/`
- **Historical Leads:** `output/leads/` (searched by FileSearchAgent)
- **Logs:** `logs/`

---

## ⚡ Performance Tips

1. **Web Search:** Results are cached - reuse when possible
2. **Image Generation:** Use `standard` quality for drafts, `hd` for finals
3. **Code Interpreter:** Batch job data for better analysis
4. **File Search:** Keep leads directory organized for faster search

---

## 🔧 Configuration

**Required Environment Variables:**

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-1106-preview  # or gpt-4, gpt-4-turbo
```

**Optional Parameters:**

- `use_web_search=True` - Enable web search (CompanyResearchAgent)
- `use_structured_extraction=True` - Enable function calling (ParserAgent)
- `quality="hd"` - High quality images (slower, more expensive)

---

## 🚨 Common Issues

**Issue:** Web search returns no results  
**Fix:** Check company name spelling, try adding location

**Issue:** Image generation fails  
**Fix:** Check prompt length (<1000 chars), avoid prohibited content

**Issue:** File search returns nothing  
**Fix:** Ensure leads exist in `output/leads/`, check JSON format

**Issue:** Code interpreter timeout  
**Fix:** Reduce dataset size, simplify calculations

---

## 📖 Full Documentation

- **User Guide:** `OPENAI_TOOLS_GUIDE.md`
- **Implementation Summary:** `OPENAI_TOOLS_SUMMARY.md`
- **Main README:** `README.md`

---

## 🎯 Common Workflows

### 1. New Lead Discovery

```
Scrape → Research (Web Search) → Parse (Function Calling) → Analyze → Visualize
```

### 2. Sales Presentation

```
Research → Calculate ROI (Code Interpreter) → Create Visuals (Image Gen) → Present
```

### 3. Pattern Discovery

```
File Search → Find Similar Companies → Research Each → Visualize Comparison
```

### 4. Quick ROI Pitch

```
Get Company Size → Calculate ROI → Create Visual → Email to Prospect
```

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Status:** Production Ready ✅
