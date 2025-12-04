"""
Test script for OpenAI Conversation State APIs.
Demonstrates multi-turn conversations with persistent context.
"""
from agents import ConversationalLeadAgent, analyze_lead_conversationally
from utils import get_logger

logger = get_logger(__name__)


def test_basic_conversation_state():
    """Test basic conversation state management."""
    print("\n" + "="*80)
    print("TEST 1: Basic Conversation State Management")
    print("="*80)
    
    agent = ConversationalLeadAgent(create_conversation=True)
    
    print(f"\n📝 Created conversation: {agent.conversation_id}")
    
    # Initial analysis
    initial_data = {
        'job_count': 45,
        'industry': 'Software Development',
        'company_size': 500,
        'avg_salary': 85000
    }
    
    print("\n🔍 Step 1: Initial company analysis...")
    initial = agent.start_company_analysis("TechCorp Solutions", initial_data)
    print(f"   ✅ Analysis complete")
    print(f"   Response ID: {initial['response_id']}")
    print(f"   Tier: {initial['analysis'].get('tier', 'N/A')}")
    
    # Follow-up question using context
    print("\n💬 Step 2: Follow-up question with context...")
    answer = agent.ask_followup_question("What are the top 3 reasons this company is a good fit?")
    print(f"   ✅ Answer: {answer[:150]}...")
    
    # Check context usage
    print("\n📊 Step 3: Check context window usage...")
    usage = agent.check_context_usage()
    print(f"   Tokens used: {usage['total_tokens']}/{usage['max_context']}")
    print(f"   Usage: {usage['usage_percent']}%")
    print(f"   Status: {usage['recommendation']}")
    
    # Get summary
    print("\n📋 Step 4: Get conversation summary...")
    summary = agent.get_conversation_summary()
    print(f"   ✅ Summary generated")
    print(f"   Total tokens used: {summary['total_tokens_used']}")
    print(f"   Messages: {summary['messages_in_history']}")
    
    return agent


def test_multi_turn_analysis_workflow():
    """Test complete multi-turn analysis workflow."""
    print("\n" + "="*80)
    print("TEST 2: Multi-Turn Analysis Workflow")
    print("="*80)
    
    agent = ConversationalLeadAgent(create_conversation=True)
    
    initial_data = {
        'job_count': 78,
        'industry': 'Healthcare Technology',
        'company_size': 300,
        'avg_salary': 72000,
        'location': 'Boston, MA'
    }
    
    # Step 1: Initial analysis
    print("\n🔍 Step 1: Initial analysis...")
    initial = agent.start_company_analysis("MedTech Innovations", initial_data)
    print(f"   ✅ Tier: {initial['analysis'].get('tier', 'N/A')}")
    print(f"   Pain points identified: {len(initial['analysis'].get('pain_points', []))}")
    
    # Step 2: Research pain point
    pain_points = initial['analysis'].get('pain_points', [])
    if pain_points:
        top_pain_point = pain_points[0] if isinstance(pain_points, list) else pain_points
        print(f"\n🔬 Step 2: Researching pain point: '{top_pain_point}'...")
        pain_analysis = agent.research_pain_point(top_pain_point)
        print(f"   ✅ Severity: {pain_analysis.get('severity', 'N/A')}/10")
        print(f"   Forecasta fit: {pain_analysis.get('forecasta_fit', 'N/A')}")
    
    # Step 3: Calculate ROI with context
    print(f"\n💰 Step 3: Calculating ROI with full context...")
    roi = agent.calculate_roi_in_context(
        company_size=initial_data['company_size'],
        avg_salary=initial_data['avg_salary']
    )
    print(f"   ✅ Annual savings: ${roi.get('annual_savings', 0):,.0f}")
    print(f"   ROI: {roi.get('roi_percentage', 0):.1f}%")
    print(f"   Confidence: {roi.get('confidence_level', 'N/A')}")
    
    # Step 4: Generate personalized email
    print(f"\n📧 Step 4: Generating personalized outreach...")
    email = agent.generate_outreach_email(contact_name="Dr. Sarah Johnson")
    print(f"   ✅ Email generated ({len(email)} chars)")
    print(f"\n   Preview:\n   {email[:200]}...")
    
    # Final summary
    print(f"\n📊 Final Summary:")
    summary = agent.get_conversation_summary()
    print(f"   Total turns: {summary['messages_in_history']}")
    print(f"   Total tokens: {summary['total_tokens_used']}")
    print(f"   Recommendation: {summary.get('recommended_next_steps', 'N/A')}")
    
    return agent


def test_response_chaining():
    """Test response chaining with previous_response_id."""
    print("\n" + "="*80)
    print("TEST 3: Response Chaining (previous_response_id)")
    print("="*80)
    
    from agents import ClientAgent
    
    client = ClientAgent()
    
    print("\n💬 Turn 1: Ask about company...")
    messages1 = [
        {"role": "system", "content": "You are a sales analyst."},
        {"role": "user", "content": "Tell me what makes a company a good fit for workforce analytics software."}
    ]
    
    response1 = client._call_api(messages1, store=True)
    print(f"   ✅ Response 1 ID: {client.previous_response_id}")
    print(f"   Preview: {response1[:100]}...")
    
    print("\n💬 Turn 2: Follow-up using context (chained)...")
    messages2 = [
        {"role": "user", "content": "Now apply those criteria to a healthcare company with 500 employees posting 40 jobs."}
    ]
    
    # This automatically uses previous_response_id for context
    response2 = client._call_api(messages2, store=True)
    print(f"   ✅ Response 2 ID: {client.previous_response_id}")
    print(f"   Preview: {response2[:100]}...")
    
    print("\n💬 Turn 3: Another follow-up (still chained)...")
    messages3 = [
        {"role": "user", "content": "What's the estimated ROI for that company?"}
    ]
    
    response3 = client._call_api(messages3, store=True)
    print(f"   ✅ Response 3 ID: {client.previous_response_id}")
    print(f"   Preview: {response3[:100]}...")
    
    print(f"\n📊 Chain Summary:")
    print(f"   Total tokens: {client.total_tokens_used}")
    print(f"   History length: {len(client.conversation_history)} messages")
    
    return client


def test_context_window_management():
    """Test context window overflow prevention."""
    print("\n" + "="*80)
    print("TEST 4: Context Window Management")
    print("="*80)
    
    from agents import ClientAgent
    
    client = ClientAgent()
    
    # Simulate a long conversation
    print("\n📝 Simulating long conversation...")
    for i in range(20):
        client.conversation_history.append({
            "role": "user",
            "content": f"Message {i}: " + ("x" * 500)  # 500 char messages
        })
        client.conversation_history.append({
            "role": "assistant",
            "content": f"Response {i}: " + ("y" * 500)
        })
    
    print(f"   Created {len(client.conversation_history)} messages")
    
    # Check context usage
    print("\n📊 Checking context usage...")
    usage = client.estimate_context_usage(client.conversation_history)
    print(f"   Total tokens: {usage['total_tokens']:,}")
    print(f"   Usage: {usage['usage_percent']}%")
    print(f"   At risk: {usage['at_risk']}")
    print(f"   Recommendation: {usage['recommendation']}")
    
    # Truncate if needed
    if usage['at_risk']:
        print("\n✂️ Truncating conversation history...")
        truncated = client.truncate_conversation_history(keep_recent=10)
        print(f"   Before: {len(client.conversation_history)} messages")
        print(f"   After: {len(truncated)} messages")
        
        new_usage = client.estimate_context_usage(truncated)
        print(f"   New usage: {new_usage['usage_percent']}%")


def test_convenience_function():
    """Test the convenience function for complete analysis."""
    print("\n" + "="*80)
    print("TEST 5: Convenience Function (analyze_lead_conversationally)")
    print("="*80)
    
    initial_data = {
        'job_count': 32,
        'industry': 'Financial Services',
        'company_size': 450,
        'avg_salary': 95000,
        'location': 'New York, NY'
    }
    
    print("\n🚀 Running complete conversational analysis...")
    results = analyze_lead_conversationally(
        company_name="FinanceFlow Corp",
        initial_data=initial_data,
        research_pain_points=True,
        calculate_roi=True,
        generate_email=True
    )
    
    print("\n✅ Analysis Complete!")
    print(f"   Initial tier: {results['initial_analysis']['analysis'].get('tier', 'N/A')}")
    
    if 'pain_point_analysis' in results:
        print(f"   Pain point severity: {results['pain_point_analysis'].get('severity', 'N/A')}/10")
    
    if 'roi_calculation' in results:
        print(f"   ROI: {results['roi_calculation'].get('roi_percentage', 0):.1f}%")
    
    if 'outreach_email' in results:
        print(f"   Email generated: {len(results['outreach_email'])} chars")
    
    print(f"\n📊 Summary:")
    print(f"   Total tokens: {results['summary']['total_tokens_used']}")
    print(f"   Context usage: {results['summary'].get('context_usage', {}).get('usage_percent', 0):.1f}%")


def run_all_tests():
    """Run all conversation state tests."""
    print("\n" + "🎯"*40)
    print("OPENAI CONVERSATION STATE API TESTS")
    print("🎯"*40)
    
    try:
        # Test 1: Basic conversation
        test_basic_conversation_state()
        
        # Test 2: Multi-turn workflow
        test_multi_turn_analysis_workflow()
        
        # Test 3: Response chaining
        test_response_chaining()
        
        # Test 4: Context management
        test_context_window_management()
        
        # Test 5: Convenience function
        test_convenience_function()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        
        print("\n🎉 Conversation State APIs are fully integrated!")
        print("\nNew Capabilities:")
        print("  ✅ Multi-turn conversations with persistent context")
        print("  ✅ Response chaining (previous_response_id)")
        print("  ✅ Conversation objects for long-running analysis")
        print("  ✅ Context window monitoring and management")
        print("  ✅ Automatic conversation history tracking")
        print("  ✅ Token usage monitoring")
        
    except Exception as e:
        logger.error(f"Test suite error: {e}", exc_info=True)
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    run_all_tests()
