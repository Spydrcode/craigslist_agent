"""
Test script to verify all API connections are working.
Run this before using the prospecting system.
"""
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI API connection."""
    print("\n1. Testing OpenAI API...")
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   ❌ OPENAI_API_KEY not found in .env")
            return False

        client = OpenAI(api_key=api_key)

        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )

        print(f"   [OK] OpenAI API connected successfully")
        print(f"   Model: {response.model}")
        return True

    except Exception as e:
        print(f"   [FAIL] OpenAI API failed: {e}")
        return False


def test_pinecone():
    """Test Pinecone connection (optional)."""
    print("\n2. Testing Pinecone (optional)...")
    try:
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            print("   ⚠️  PINECONE_API_KEY not found - vector search will be disabled")
            return None

        from pinecone import Pinecone

        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()

        print(f"   ✅ Pinecone connected successfully")
        print(f"   Available indexes: {[idx.name for idx in indexes]}")
        return True

    except Exception as e:
        print(f"   ⚠️  Pinecone connection failed: {e}")
        print("   Vector search will be disabled")
        return None


def test_supabase():
    """Test Supabase connection (optional)."""
    print("\n3. Testing Supabase (optional)...")
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            print("   ⚠️  Supabase credentials not found - database storage will be disabled")
            return None

        from supabase import create_client

        supabase = create_client(url, key)

        # Test connection by listing tables
        result = supabase.table('jobs').select("*").limit(1).execute()

        print(f"   ✅ Supabase connected successfully")
        print(f"   Database accessible")
        return True

    except Exception as e:
        print(f"   ⚠️  Supabase connection failed: {e}")
        print("   Database storage will be disabled")
        return None


def test_internet_connection():
    """Test internet connection for scraping."""
    print("\n4. Testing internet connection...")
    try:
        import requests

        response = requests.get("https://sfbay.craigslist.org", timeout=5)

        if response.status_code == 200:
            print(f"   ✅ Internet connection OK")
            print(f"   Craigslist accessible")
            return True
        else:
            print(f"   ⚠️  Craigslist returned status {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Internet connection failed: {e}")
        return False


def main():
    print("="*60)
    print("TESTING API CONNECTIONS")
    print("="*60)

    results = {
        'openai': test_openai(),
        'internet': test_internet_connection(),
        'pinecone': test_pinecone(),
        'supabase': test_supabase()
    }

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    # Required services
    print("\nRequired Services:")
    print(f"  OpenAI API: {'✅ Working' if results['openai'] else '❌ FAILED'}")
    print(f"  Internet: {'✅ Working' if results['internet'] else '❌ FAILED'}")

    # Optional services
    print("\nOptional Services:")
    print(f"  Pinecone: {'✅ Working' if results['pinecone'] else '⚠️  Disabled'}")
    print(f"  Supabase: {'✅ Working' if results['supabase'] else '⚠️  Disabled'}")

    # Overall status
    print("\n" + "="*60)

    if results['openai'] and results['internet']:
        print("✅ READY TO USE")
        print("\nYou can now run:")
        print("  python main_prospecting.py prospect --city sfbay --category sof --pages 2")

        if not results['pinecone']:
            print("\nNote: Vector search disabled (Pinecone not available)")
        if not results['supabase']:
            print("Note: Database storage disabled (Supabase not available)")
            print("      Results will be saved to files only")

        return 0
    else:
        print("❌ SETUP INCOMPLETE")
        print("\nMissing required services:")
        if not results['openai']:
            print("  - OpenAI API (check OPENAI_API_KEY in .env)")
        if not results['internet']:
            print("  - Internet connection (check network)")

        return 1


if __name__ == "__main__":
    sys.exit(main())
