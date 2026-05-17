import os
import uuid
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from pymongo import MongoClient

from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def get_mongo_client():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client[os.getenv("MONGO_DB")]


def save_business_postgres(business: dict) -> Optional[str]:
    """Save structured business data to PostgreSQL"""

    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO businesses (
                    google_place_id, name, address, city, state,
                    country, phone, website, email, business_type,
                    google_rating, google_review_count, price_level,
                    latitude, longitude, is_verified
                ) VALUES (
                    %(google_place_id)s, %(name)s, %(address)s,
                    %(city)s, %(state)s, %(country)s, %(phone)s,
                    %(website)s, %(email)s, %(business_type)s,
                    %(google_rating)s, %(google_review_count)s,
                    %(price_level)s, %(latitude)s, %(longitude)s,
                    %(is_verified)s
                )
                ON CONFLICT (google_place_id)
                DO UPDATE SET
                    google_rating = EXCLUDED.google_rating,
                    google_review_count = EXCLUDED.google_review_count,
                    updated_at = NOW()
                RETURNING id
            """, business)

            result = cur.fetchone()
            conn.commit()
            return str(result["id"]) if result else None

    except Exception as e:
        conn.rollback()
        print(f"PostgreSQL error: {e}")
        return None
    finally:
        conn.close()


def save_business_mongodb(business: dict, postgres_id: str):
    """Save raw unstructured data to MongoDB"""

    db = get_mongo_client()

    doc = {
        "postgres_id": postgres_id,
        "google_place_id": business["google_place_id"],
        "name": business["name"],
        "google_data": business.get("raw_google_data", {}),
        "scraped_website": {},
        "email_discovery": {},
        "agent_research": {},
        "scraped_at": datetime.utcnow()
    }

    db.raw_businesses.update_one(
        {"google_place_id": business["google_place_id"]},
        {"$set": doc},
        upsert=True
    )


def save_businesses(businesses: list[dict]) -> dict:
    """Save list of businesses to both databases"""

    saved = 0
    failed = 0

    for business in businesses:
        postgres_id = save_business_postgres(business)

        if postgres_id:
            save_business_mongodb(business, postgres_id)
            saved += 1
            print(f"  💾 Saved: {business['name']}")
        else:
            failed += 1
            print(f"  ❌ Failed: {business['name']}")

    return {"saved": saved, "failed": failed}


def get_businesses_without_email(limit: int = 50) -> list[dict]:
    """Get businesses that need email discovery"""

    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, website, google_place_id
                FROM businesses
                WHERE (email IS NULL OR email = '')
                AND website IS NOT NULL
                AND website != ''
                LIMIT %s
            """, (limit,))
            return cur.fetchall()
    finally:
        conn.close()


def update_business_email(business_id: str, email: str):
    """Update email for a business"""

    conn = get_postgres_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE businesses
                SET email = %s, updated_at = NOW()
                WHERE id = %s
            """, (email, business_id))
            conn.commit()
    finally:
        conn.close()