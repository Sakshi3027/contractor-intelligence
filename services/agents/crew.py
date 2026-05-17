import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.research_agent import research_business
from agents.email_agent import generate_email


def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def get_mongo_db():
    client = MongoClient(os.getenv("MONGO_URI"))
    return client[os.getenv("MONGO_DB")]


def get_hot_leads(limit: int = 5) -> list[dict]:
    """Fetch hot leads that haven't been contacted yet"""

    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    b.id,
                    b.name,
                    b.city,
                    b.email,
                    b.website,
                    b.google_rating,
                    b.google_review_count,
                    ls.score,
                    ls.tier
                FROM businesses b
                JOIN lead_scores ls ON b.id = ls.business_id
                LEFT JOIN outreach o ON b.id = o.business_id
                WHERE ls.tier = 'hot'
                AND o.id IS NULL
                AND b.email IS NOT NULL
                AND b.email != ''
                ORDER BY ls.score DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def save_outreach(business_id: str, email_data: dict,
                  research: str) -> str:
    """Save generated outreach to PostgreSQL"""

    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO outreach (
                    business_id, to_email, subject, body,
                    email_version, status, agent_model,
                    generation_prompt, scheduled_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """, (
                business_id,
                email_data.get("to_email", ""),
                email_data.get("subject", ""),
                email_data.get("body", ""),
                "v1",
                "pending",
                "llama3-70b-8192",
                research[:500],
                datetime.utcnow()
            ))
            result = cur.fetchone()
            conn.commit()
            return str(result["id"])
    finally:
        conn.close()


def save_draft_mongodb(business: dict, research: str,
                       email: dict, outreach_id: str):
    """Save full draft with research to MongoDB"""

    db = get_mongo_db()
    db.email_drafts.insert_one({
        "outreach_id": outreach_id,
        "business_id": str(business["id"]),
        "business_name": business["name"],
        "research": research,
        "email_subject": email["subject"],
        "email_body": email["body"],
        "score": float(business.get("score", 0)),
        "tier": business.get("tier", ""),
        "created_at": datetime.utcnow()
    })


def run_agent_pipeline(limit: int = 3):
    """Run full research + email generation pipeline"""

    print("\n🤖 Starting AI Agent Pipeline")
    print("=" * 50)

    # Get hot leads
    leads = get_hot_leads(limit)
    print(f"Found {len(leads)} hot leads to process\n")

    if not leads:
        print("No hot leads available. Run scoring first.")
        return

    results = []

    for i, lead in enumerate(leads, 1):
        print(f"[{i}/{len(leads)}] Processing: {lead['name'][:50]}")
        print(f"   Score: {lead['score']:.3f} | City: {lead['city']}")

        try:
            # Step 1 — Research
            print("   🔍 Researching business...")
            research = research_business(lead)

            # Step 2 — Generate email
            print("   ✍️  Generating email...")
            email = generate_email(lead, research)
            email["to_email"] = lead.get("email", "")

            # Step 3 — Save to PostgreSQL
            outreach_id = save_outreach(
                str(lead["id"]), email, research
            )

            # Step 4 — Save to MongoDB
            save_draft_mongodb(lead, research, email, outreach_id)

            results.append({
                "business": lead["name"],
                "subject": email["subject"],
                "outreach_id": outreach_id
            })

            print(f"   ✅ Email generated and saved")
            print(f"   📧 Subject: {email['subject'][:60]}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    print("=" * 50)
    print(f"✅ Pipeline complete: {len(results)}/{len(leads)} processed")
    print("\n📋 Generated Emails:")
    for r in results:
        print(f"   • {r['business'][:40]}")
        print(f"     Subject: {r['subject'][:55]}")

    return results