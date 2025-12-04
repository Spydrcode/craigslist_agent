# OpenAI Conversation State APIs - Implementation Guide

## 🎯 Overview

Your project now includes **OpenAI's Conversation State APIs**, enabling multi-turn conversations with persistent context. This is a significant enhancement over manual history management.

## ✅ What's Been Implemented

### 1. **Enhanced ClientAgent** with Conversation State

- Automatic conversation history tracking
- Response ID chaining (`previous_response_id`)
- Conversation objects for persistent state
- Context window monitoring
- Token usage tracking

### 2. **ConversationalLeadAgent** - New High-Level Agent

Multi-turn lead analysis with contextual understanding across:

- Initial company qualification
- Deep-dive pain point research
- Contextual ROI calculations
- Personalized outreach email generation
- Conversation summaries

### 3. **Dashboard API Endpoints**

6 new REST endpoints for conversational workflows:

- `POST /api/conversation/start` - Start conversation
- `POST /api/conversation/ask` - Follow-up questions
- `POST /api/conversation/roi` - ROI with context
- `POST /api/conversation/email` - Generate email
- `POST /api/conversation/summary` - Get summary
- `POST /api/conversation/complete` - Complete workflow

---

## 🚀 Key Benefits

### Before (Manual History Management)

```python
# Had to manually chain messages
history = []
history.append({"role": "user", "content": "analyze company"})
response1 = call_api(history)
history.append({"role": "assistant", "content": response1})
history.append({"role": "user", "content": "tell me more"})
response2 = call_api(history)  # Pass entire history again
```

### After (Conversation State APIs)

```python
# Automatic context management
agent = ConversationalLeadAgent(create_conversation=True)
agent.start_company_analysis("TechCorp", data)
agent.ask_followup_question("tell me more")  # Context preserved!
```

---

## 📚 Usage Examples

### Example 1: Basic Multi-Turn Analysis

```python
from agents import ConversationalLeadAgent

# Create conversation
agent = ConversationalLeadAgent(create_conversation=True)

# Step 1: Initial analysis
initial = agent.start_company_analysis(
    company_name="TechCorp Solutions",
    initial_data={
        'job_count': 45,
        'industry': 'Software',
        'company_size': 500
    }
)

# Step 2: Follow-up question (context preserved)
answer = agent.ask_followup_question(
    "What are the top 3 reasons this is a good fit?"
)

# Step 3: Calculate ROI (knows company from context)
roi = agent.calculate_roi_in_context(
    company_size=500,
    avg_salary=85000
)

# Step 4: Generate email (personalizes based on full context)
email = agent.generate_outreach_email("Sarah Johnson")
```

### Example 2: Complete Workflow (One Function)

```python
from agents import analyze_lead_conversationally

results = analyze_lead_conversationally(
    company_name="TechCorp",
    initial_data={'job_count': 45, 'company_size': 500},
    research_pain_points=True,
    calculate_roi=True,
    generate_email=True
)

# Results include:
# - initial_analysis
# - pain_point_analysis
# - roi_calculation
# - outreach_email
# - summary (with token usage)
```

### Example 3: Response Chaining

```python
from agents import ClientAgent

client = ClientAgent()

# Turn 1
messages1 = [{"role": "user", "content": "What makes a good lead?"}]
response1 = client._call_api(messages1, store=True)
# Response ID saved automatically

# Turn 2 (automatically chained via previous_response_id)
messages2 = [{"role": "user", "content": "Apply that to TechCorp with 500 employees"}]
response2 = client._call_api(messages2, store=True)

# Turn 3 (still chained)
messages3 = [{"role": "user", "content": "What's the ROI?"}]
response3 = client._call_api(messages3, store=True)
```

### Example 4: Context Window Management

```python
from agents import ClientAgent

client = ClientAgent()

# Check context usage
usage = client.estimate_context_usage(client.conversation_history)
print(f"Usage: {usage['usage_percent']}%")
print(f"At risk: {usage['at_risk']}")
print(f"Recommendation: {usage['recommendation']}")

# Truncate if needed
if usage['at_risk']:
    truncated = client.truncate_conversation_history(keep_recent=10)
```

---

## 🌐 Dashboard API Examples

### Start Conversational Analysis

```bash
curl -X POST http://localhost:3000/api/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp",
    "job_count": 45,
    "industry": "Software",
    "company_size": 500,
    "avg_salary": 85000
  }'

# Response:
{
  "success": true,
  "conversation_id": "conv_abc123",
  "response_id": "resp_xyz789",
  "analysis": {
    "tier": "TIER 2",
    "pain_points": ["High turnover", "Scaling challenges"],
    ...
  }
}
```

### Ask Follow-Up Question

```bash
curl -X POST http://localhost:3000/api/conversation/ask \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "question": "What are their biggest pain points?"
  }'

# Response includes full context from previous turns
```

### Calculate ROI with Context

```bash
curl -X POST http://localhost:3000/api/conversation/roi \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "company_size": 500,
    "avg_salary": 85000
  }'

# ROI calculation uses full conversation context
```

### Generate Personalized Email

```bash
curl -X POST http://localhost:3000/api/conversation/email \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123",
    "contact_name": "Sarah Johnson"
  }'

# Email references specific pain points and ROI from conversation
```

### Get Conversation Summary

```bash
curl -X POST http://localhost:3000/api/conversation/summary \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_abc123"
  }'
```

### Complete Analysis (One API Call)

```bash
curl -X POST http://localhost:3000/api/conversation/complete \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "TechCorp",
    "job_count": 45,
    "company_size": 500,
    "generate_email": true
  }'

# Runs full workflow: analyze → research → ROI → email → summary
```

---

## 🔧 ClientAgent Enhancements

### New Attributes

```python
self.conversation_id: Optional[str]  # Persistent conversation
self.previous_response_id: Optional[str]  # For chaining
self.conversation_history: List[Dict]  # Auto-tracked
self.total_tokens_used: int  # Running total
```

### New Methods

**`create_conversation()`** - Create persistent conversation

```python
conversation_id = client.create_conversation()
```

**`get_conversation_history()`** - Get message history

```python
history = client.get_conversation_history()
```

**`clear_conversation_history()`** - Reset state

```python
client.clear_conversation_history()
```

**`estimate_context_usage()`** - Check context window

```python
usage = client.estimate_context_usage(messages)
# Returns: total_tokens, usage_percent, at_risk, recommendation
```

**`truncate_conversation_history()`** - Prevent overflow

```python
truncated = client.truncate_conversation_history(keep_recent=10)
```

### Enhanced `_call_api()`

```python
response = client._call_api(
    messages,
    store=True,  # Store for 30 days
    use_conversation=True,  # Use conversation_id
    previous_response_id="resp_xyz"  # Chain responses
)
```

---

## 📊 ConversationalLeadAgent Methods

| Method                       | Purpose                       | Returns                            |
| ---------------------------- | ----------------------------- | ---------------------------------- |
| `start_company_analysis()`   | Begin multi-turn analysis     | Initial analysis + conversation_id |
| `research_pain_point()`      | Deep dive specific pain point | Detailed pain point analysis       |
| `calculate_roi_in_context()` | ROI with full context         | Contextualized ROI projection      |
| `generate_outreach_email()`  | Personalized email            | Email text using full context      |
| `ask_followup_question()`    | Ad-hoc questions              | Answer based on conversation       |
| `get_conversation_summary()` | Full summary                  | Complete analysis summary          |
| `check_context_usage()`      | Monitor context window        | Usage statistics                   |
| `export_conversation()`      | Export for review             | Complete conversation data         |

---

## 💡 Use Cases

### 1. **Deep Lead Analysis**

Multi-turn investigation of complex leads:

- Initial qualification
- Research specific pain points
- Calculate multiple ROI scenarios
- Generate personalized outreach

### 2. **Interactive Sales Calls**

Use during live sales calls:

- Start conversation with company data
- Ask follow-up questions in real-time
- Calculate ROI based on discussion
- Generate instant follow-up email

### 3. **Batch Processing with Context**

Analyze multiple companies with persistent learning:

- Create conversation per company
- Each analysis builds on previous context
- Compare companies within conversation
- Generate comparative reports

### 4. **Long-Running Research**

Multi-day research projects:

- Conversation persists across sessions
- Resume analysis days later
- Add new findings incrementally
- Final summary includes all context

---

## ⚙️ Configuration

### Context Window Limits (by Model)

| Model       | Context Window | Recommended Max |
| ----------- | -------------- | --------------- |
| GPT-4       | 8,192 tokens   | ~6,500 tokens   |
| GPT-4-32k   | 32,768 tokens  | ~26,000 tokens  |
| GPT-4-Turbo | 128,000 tokens | ~102,000 tokens |
| GPT-4o      | 128,000 tokens | ~102,000 tokens |

### Response Storage

- `store=True`: Responses stored 30 days (viewable in dashboard)
- `store=False`: Not stored (default for privacy)
- Conversation items: No 30-day limit (persistent)

---

## 🧪 Testing

**Run Test Suite:**

```bash
python test_conversation_state.py
```

**Tests:**

1. Basic conversation state management
2. Multi-turn analysis workflow
3. Response chaining with `previous_response_id`
4. Context window management
5. Convenience function

---

## 📈 Performance Tips

### 1. Use Conversations for Long-Running Analysis

```python
# Good: Single conversation for entire lead lifecycle
agent = ConversationalLeadAgent(create_conversation=True)
# All analysis in one conversation

# Avoid: Creating new conversation per step
```

### 2. Monitor Context Usage

```python
usage = agent.check_context_usage()
if usage['at_risk']:
    # Summarize or truncate history
    agent.client.truncate_conversation_history(keep_recent=10)
```

### 3. Use Response Chaining for Sequential Tasks

```python
# Automatically chains via previous_response_id
response1 = client._call_api(messages1, store=True)
response2 = client._call_api(messages2, store=True)  # Has context from response1
```

### 4. Disable Storage for Sensitive Data

```python
# Don't store sensitive conversations
response = client._call_api(messages, store=False)
```

---

## 🔒 Privacy & Security

- **Default:** `store=False` (not saved)
- **Stored responses:** 30-day retention
- **Conversations:** No automatic deletion
- **Data usage:** OpenAI doesn't train on API data
- **Best practice:** Use `store=False` for sensitive leads

---

## 🎯 Key Takeaways

✅ **Automatic Context Management** - No manual history tracking  
✅ **Persistent Conversations** - Resume across sessions  
✅ **Response Chaining** - Seamless multi-turn workflows  
✅ **Context Monitoring** - Prevent overflow  
✅ **Token Tracking** - Monitor costs  
✅ **Dashboard Integration** - 6 new API endpoints

---

## 📚 Further Reading

- [OpenAI Conversation State Guide](https://platform.openai.com/docs/guides/conversation-state)
- [Responses API Documentation](https://platform.openai.com/docs/api-reference/responses)
- [Conversations API Documentation](https://platform.openai.com/docs/api-reference/conversations)
- [Context Window Management](https://platform.openai.com/docs/guides/context-window)

---

**Implementation Date:** December 2025  
**Status:** Production Ready ✅  
**Integration:** Complete with existing agents
