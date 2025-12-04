"""
Test script to verify API connections.
Simple version without Unicode characters for Windows compatibility.
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("TESTING API CONNECTIONS")
print("="*60)

# Test 1: OpenAI
print("\n1. Testing OpenAI API...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'test'"}],
        max_tokens=5
    )
    print("   [OK] OpenAI connected")
    openai_ok = True
except Exception as e:
    print(f"   [FAIL] {e}")
    openai_ok = False

# Test 2: Internet
print("\n2. Testing internet...")
try:
    import requests
    r = requests.get("https://sfbay.craigslist.org", timeout=5)
    print("   [OK] Craigslist accessible")
    internet_ok = True
except Exception as e:
    print(f"   [FAIL] {e}")
    internet_ok = False

# Test 3: Pinecone (optional)
print("\n3. Testing Pinecone (optional)...")
try:
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    indexes = pc.list_indexes()
    print(f"   [OK] Connected - indexes: {[idx.name for idx in indexes]}")
    pinecone_ok = True
except Exception as e:
    print(f"   [SKIP] Not configured or failed: {e}")
    pinecone_ok = False

# Test 4: Supabase (optional)
print("\n4. Testing Supabase (optional)...")
try:
    from supabase import create_client
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    result = supabase.table('jobs').select("*").limit(1).execute()
    print("   [OK] Database accessible")
    supabase_ok = True
except Exception as e:
    print(f"   [SKIP] Not configured or failed: {e}")
    supabase_ok = False

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"\nRequired:")
print(f"  OpenAI:  {'OK' if openai_ok else 'FAIL - CHECK API KEY'}")
print(f"  Internet: {'OK' if internet_ok else 'FAIL - CHECK NETWORK'}")

print(f"\nOptional:")
print(f"  Pinecone:  {'OK' if pinecone_ok else 'DISABLED'}")
print(f"  Supabase:  {'OK' if supabase_ok else 'DISABLED'}")

print("\n" + "="*60)

if openai_ok and internet_ok:
    print("\n[READY] System is ready to use!")
    print("\nYou can now run:")
    print("  python run_prospecting_simple.py")
    if not supabase_ok:
        print("\nNote: Results will be saved to files only (no database)")
else:
    print("\n[NOT READY] Fix the failed items above")
    if not openai_ok:
        print("  - Add OPENAI_API_KEY to .env file")
    if not internet_ok:
        print("  - Check your internet connection")
