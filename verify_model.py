"""Verify which OpenAI model is configured"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from config import Config

print("\n" + "="*60)
print("MODEL CONFIGURATION VERIFICATION")
print("="*60)

print(f"\nLoaded model: {Config.OPENAI_MODEL}")

if Config.OPENAI_MODEL == "gpt-4o-mini":
    print("\nCORRECT! Using gpt-4o-mini (cheapest option)")
    print("\nCost per 400 jobs:")
    print("  Real-time: $0.10")
    print("  Batch API: $0.05 (50% discount)")
elif Config.OPENAI_MODEL == "gpt-3.5-turbo":
    print("\nWARNING: Using gpt-3.5-turbo (3x more expensive than gpt-4o-mini)")
    print("\nCost per 400 jobs: $0.28")
    print("\nRecommendation: Switch to gpt-4o-mini to save 70%")
elif "gpt-4" in Config.OPENAI_MODEL:
    print("\nWARNING! Using expensive GPT-4 model!")
    print(f"\nModel: {Config.OPENAI_MODEL}")
    print("Cost per 400 jobs: $1.60 - $5.60 (16-56x more expensive!)")
    print("\nCHANGE .env file to: OPENAI_MODEL=gpt-4o-mini")
    print("   This will save you 90%+ on API costs!")
    sys.exit(1)
else:
    print(f"\nWARNING: Unknown model: {Config.OPENAI_MODEL}")

# Check API key
if Config.OPENAI_API_KEY:
    print(f"\nAPI Key loaded: {Config.OPENAI_API_KEY[:20]}...")
else:
    print("\nERROR: No API key found!")
    sys.exit(1)

print("\n" + "="*60)
print("READY TO RUN!")
print("="*60)
print("\nYou can now safely run searches without burning credits.")
print("\nNext steps:")
print("  1. Restart dashboard: python dashboard/leads_app.py")
print("  2. Open http://localhost:3000")
print("  3. Search Phoenix → $0.10 for 400 jobs")
