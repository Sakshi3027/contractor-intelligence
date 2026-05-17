import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery.google_places import discover_businesses
from discovery.storage import save_businesses, get_businesses_without_email

# Target cities for IT service discovery
TARGET_CITIES = [
    "Boston",
    "New York",
    "Chicago",
    "San Francisco",
    "Austin",
    "Seattle",
    "Atlanta",
    "Denver"
]

async def run_discovery(cities: list[str] = None, max_per_city: int = 10):
    """Run full discovery pipeline"""

    cities = cities or TARGET_CITIES

    print("=" * 50)
    print("🚀 Starting Contractor Intelligence Discovery")
    print("=" * 50)

    # Step 1 — Discover businesses
    print("\n📍 Phase 1: Business Discovery")
    businesses = await discover_businesses(cities, max_per_city)

    if not businesses:
        print("❌ No businesses discovered")
        return

    # Step 2 — Save to databases
    print("\n💾 Phase 2: Saving to Databases")
    result = save_businesses(businesses)
    print(f"\n✅ Saved: {result['saved']} | ❌ Failed: {result['failed']}")

    # Step 3 — Summary
    print("\n" + "=" * 50)
    print("📊 Discovery Complete")
    print(f"   Cities searched: {len(cities)}")
    print(f"   Businesses found: {len(businesses)}")
    print(f"   Successfully saved: {result['saved']}")
    print("=" * 50)


if __name__ == "__main__":
    # Run with just 3 cities for testing
    asyncio.run(run_discovery(
        cities=["Boston", "New York", "Chicago"],
        max_per_city=5
    ))