import httpx
import asyncio
import os
from dotenv import load_dotenv
from typing import Optional
import json

from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
NEW_PLACES_URL = "https://places.googleapis.com/v1/places"

IT_SERVICE_TYPES = [
    "IT services company",
    "managed service provider",
    "cybersecurity company",
    "cloud computing services",
    "software development company",
    "IT consulting firm",
    "network solutions company",
    "tech support company"
]


async def search_businesses(
    query: str,
    city: str,
    max_results: int = 20
) -> list[dict]:
    """Search using Places API (New)"""

    results = []

    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": ",".join([
                "places.id",
                "places.displayName",
                "places.formattedAddress",
                "places.nationalPhoneNumber",
                "places.websiteUri",
                "places.rating",
                "places.userRatingCount",
                "places.priceLevel",
                "places.location",
                "places.businessStatus",
                "places.types",
                "places.regularOpeningHours"
            ])
        }

        payload = {
            "textQuery": f"{query} in {city}",
            "maxResultCount": min(max_results, 20),
            "languageCode": "en"
        }

        response = await client.post(
            f"{NEW_PLACES_URL}:searchText",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            return []

        data = response.json()
        results = data.get("places", [])

    return results


def parse_business(place: dict, city: str) -> dict:
    """Parse new Places API response into our schema"""

    location = place.get("location", {})
    address = place.get("formattedAddress", "")
    address_parts = address.split(",")
    display_name = place.get("displayName", {})

    return {
        "google_place_id": place.get("id", ""),
        "name": display_name.get("text", "") if isinstance(display_name, dict) else str(display_name),
        "address": address,
        "city": city,
        "state": address_parts[-2].strip().split(" ")[0] if len(address_parts) >= 2 else "",
        "country": "US",
        "phone": place.get("nationalPhoneNumber", ""),
        "website": place.get("websiteUri", ""),
        "email": "",
        "business_type": "IT Services",
        "google_rating": float(place.get("rating", 0.0)),
        "google_review_count": int(place.get("userRatingCount", 0)),
        "price_level": 0,
        "latitude": float(location.get("latitude", 0.0)),
        "longitude": float(location.get("longitude", 0.0)),
        "is_verified": place.get("businessStatus") == "OPERATIONAL",
        "raw_google_data": {
            "types": place.get("types", []),
            "opening_hours": place.get("regularOpeningHours", {}),
            "business_status": place.get("businessStatus", ""),
            "price_level": place.get("priceLevel", ""),
        }
    }


async def discover_businesses(
    cities: list[str],
    max_per_city: int = 10
) -> list[dict]:
    """Main discovery function"""

    all_businesses = []
    seen_place_ids = set()

    for city in cities:
        print(f"\n🔍 Searching in {city}...")
        city_count = 0

        for query in IT_SERVICE_TYPES[:3]:
            if city_count >= max_per_city:
                break

            print(f"  Query: {query}")
            places = await search_businesses(query, city, max_results=5)

            for place in places:
                if city_count >= max_per_city:
                    break

                place_id = place.get("id")
                if place_id in seen_place_ids:
                    continue

                seen_place_ids.add(place_id)
                business = parse_business(place, city)
                all_businesses.append(business)
                city_count += 1
                print(f"  ✅ Found: {business['name']}")

                await asyncio.sleep(0.3)

    print(f"\n📊 Total businesses discovered: {len(all_businesses)}")
    return all_businesses


if __name__ == "__main__":
    cities = ["Boston", "New York", "Chicago"]
    businesses = asyncio.run(discover_businesses(cities, max_per_city=5))
    if businesses:
        print(json.dumps(businesses[0], indent=2))