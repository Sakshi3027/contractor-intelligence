import httpx
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from discovery.storage import (
    get_postgres_conn,
    get_mongo_client,
    get_businesses_without_email,
    update_business_email
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_BASE_URL = "https://api.hunter.io/v2"


async def find_email_by_domain(domain: str) -> Optional[dict]:
    """Find emails for a domain using Hunter.io"""

    # Clean domain — remove http/https/www
    domain = domain.replace("https://", "").replace("http://", "")
    domain = domain.replace("www.", "").split("/")[0]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{HUNTER_BASE_URL}/domain-search",
            params={
                "domain": domain,
                "api_key": HUNTER_API_KEY,
                "limit": 5,
                "type": "generic"
            }
        )

        if response.status_code != 200:
            print(f"  Hunter error {response.status_code}: {domain}")
            return None

        data = response.json()
        emails = data.get("data", {}).get("emails", [])

        if not emails:
            # Try email finder with common patterns
            return await guess_email(domain)

        # Return highest confidence email
        best = max(emails, key=lambda x: x.get("confidence", 0))
        return {
            "email": best.get("value"),
            "confidence": best.get("confidence"),
            "type": best.get("type"),
            "source": "hunter_domain_search"
        }


async def guess_email(domain: str) -> Optional[dict]:
    """Try common email patterns when Hunter finds nothing"""

    async with httpx.AsyncClient() as client:
        # Try info@domain first
        for prefix in ["info", "contact", "hello", "sales"]:
            response = await client.get(
                f"{HUNTER_BASE_URL}/email-verifier",
                params={
                    "email": f"{prefix}@{domain}",
                    "api_key": HUNTER_API_KEY
                }
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get("data", {}).get("status")

                if status in ["valid", "accept_all"]:
                    return {
                        "email": f"{prefix}@{domain}",
                        "confidence": 70,
                        "type": "guessed",
                        "source": "pattern_guess"
                    }

    return None


def update_mongodb_email(google_place_id: str, email_data: dict):
    """Store email discovery results in MongoDB"""

    db = get_mongo_client()
    db.raw_businesses.update_one(
        {"google_place_id": google_place_id},
        {"$set": {
            "email_discovery": email_data
        }}
    )


async def run_email_discovery(limit: int = 50):
    """Find emails for all businesses without one"""

    print("\n📧 Starting Email Discovery")
    print("=" * 40)

    businesses = get_businesses_without_email(limit)
    print(f"Found {len(businesses)} businesses needing emails\n")

    found = 0
    not_found = 0

    for biz in businesses:
        website = biz.get("website", "")
        name = biz.get("name", "")
        biz_id = str(biz.get("id"))
        place_id = biz.get("google_place_id", "")

        if not website:
            not_found += 1
            continue

        print(f"🔍 {name[:50]}")
        print(f"   Domain: {website}")

        result = await find_email_by_domain(website)

        if result and result.get("email"):
            email = result["email"]
            confidence = result.get("confidence", 0)

            # Save to PostgreSQL
            update_business_email(biz_id, email)

            # Save full result to MongoDB
            update_mongodb_email(place_id, result)

            print(f"   ✅ {email} (confidence: {confidence}%)")
            found += 1
        else:
            print(f"   ❌ No email found")
            not_found += 1

        # Rate limit — Hunter free tier
        import asyncio
        await asyncio.sleep(1)

    print(f"\n{'=' * 40}")
    print(f"✅ Emails found:     {found}")
    print(f"❌ Not found:        {not_found}")
    print(f"📊 Success rate:     {round(found/(found+not_found)*100)}%")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_email_discovery())