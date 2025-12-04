"""
Setup script for Craigslist Job Scraper.
Helps users quickly configure and test the system.
"""
import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_path = Path('.env')
    env_example_path = Path('.env.example')

    if env_path.exists():
        print("✓ .env file already exists")
        return

    if not env_example_path.exists():
        print("✗ .env.example not found")
        return

    # Copy template
    with open(env_example_path, 'r') as f:
        content = f.read()

    with open(env_path, 'w') as f:
        f.write(content)

    print("✓ Created .env file from template")
    print("  → Please edit .env and add your API keys")


def create_directories():
    """Create necessary directories."""
    directories = [
        'logs',
        'data',
        'exports',
    ]

    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory exists: {directory}")


def check_dependencies():
    """Check if all dependencies are installed."""
    print("\nChecking dependencies...")

    required_packages = [
        'requests',
        'beautifulsoup4',
        'openai',
        'pinecone',
        'supabase',
        'pandas',
        'pydantic',
        'tenacity',
        'apscheduler',
        'streamlit',
        'plotly',
        'python-dotenv',
    ]

    missing = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)

    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        return False

    print("\n✓ All dependencies installed")
    return True


def verify_env_config():
    """Verify that .env has required configuration."""
    from dotenv import load_dotenv

    load_dotenv()

    print("\nVerifying environment configuration...")

    required_vars = [
        'OPENAI_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT',
        'SUPABASE_URL',
        'SUPABASE_KEY',
    ]

    missing = []

    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"  ✗ {var} not configured")
            missing.append(var)
        else:
            # Show partial key for verification
            masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
            print(f"  ✓ {var}: {masked}")

    if missing:
        print(f"\n⚠ Missing configuration: {', '.join(missing)}")
        print("  Please edit .env and add your API keys")
        return False

    print("\n✓ Environment configuration complete")
    return True


def test_connections():
    """Test connections to external services."""
    print("\nTesting connections...")

    # Test OpenAI
    try:
        from openai import OpenAI
        from config import Config

        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        # Simple test - list models
        models = client.models.list()
        print("  ✓ OpenAI connection successful")
    except Exception as e:
        print(f"  ✗ OpenAI connection failed: {e}")

    # Test Pinecone
    try:
        from pinecone import Pinecone
        from config import Config

        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        indexes = pc.list_indexes()
        print("  ✓ Pinecone connection successful")
    except Exception as e:
        print(f"  ✗ Pinecone connection failed: {e}")

    # Test Supabase
    try:
        from supabase import create_client
        from config import Config

        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        # Test query
        result = supabase.table('jobs').select('id').limit(1).execute()
        print("  ✓ Supabase connection successful")
    except Exception as e:
        print(f"  ✗ Supabase connection failed: {e}")


def main():
    """Main setup process."""
    print("=" * 60)
    print("Craigslist Job Scraper - Setup Wizard")
    print("=" * 60)

    # Step 1: Create .env
    print("\nStep 1: Environment Configuration")
    create_env_file()

    # Step 2: Create directories
    print("\nStep 2: Creating Directories")
    create_directories()

    # Step 3: Check dependencies
    print("\nStep 3: Checking Dependencies")
    deps_ok = check_dependencies()

    if not deps_ok:
        print("\n⚠ Please install dependencies before continuing")
        sys.exit(1)

    # Step 4: Verify configuration
    print("\nStep 4: Verifying Configuration")
    config_ok = verify_env_config()

    if not config_ok:
        print("\n⚠ Please configure .env before continuing")
        sys.exit(1)

    # Step 5: Test connections
    print("\nStep 5: Testing Connections")
    test_connections()

    # Done
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)

    print("\nNext steps:")
    print("  1. Review database_schema.sql and run it in Supabase SQL Editor")
    print("  2. Try a basic scrape: python main.py scrape --city sfbay --category sof --pages 1")
    print("  3. Launch dashboard: streamlit run dashboard/app.py")
    print("  4. Check examples/: python examples/basic_scrape.py")

    print("\nFor help: python main.py --help")
    print("Documentation: README.md")


if __name__ == "__main__":
    main()
