import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from temporalio import activity
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


@activity.defn
async def discover_leads_activity(cities: list[str]) -> dict:
    """Activity: Discover new IT businesses"""
    import asyncio
    from discovery.google_places import discover_businesses
    from discovery.storage import save_businesses

    print(f"🔍 Discovering leads in: {cities}")
    businesses = await discover_businesses(cities, max_per_city=5)
    result = save_businesses(businesses)

    return {
        "discovered": len(businesses),
        "saved": result["saved"],
        "failed": result["failed"],
        "timestamp": datetime.utcnow().isoformat()
    }


@activity.defn
async def find_emails_activity() -> dict:
    """Activity: Find emails for businesses without one"""
    from discovery.email_finder import run_email_discovery

    print("📧 Finding emails...")
    await run_email_discovery(limit=20)

    return {
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat()
    }


@activity.defn
async def score_leads_activity() -> dict:
    """Activity: Score all businesses with ML model"""
    from scoring.predict import run_scoring

    print("🎯 Scoring leads...")
    run_scoring()

    # Get counts from DB
    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN tier = 'hot' THEN 1 END) as hot,
                    COUNT(CASE WHEN tier = 'warm' THEN 1 END) as warm,
                    COUNT(CASE WHEN tier = 'cold' THEN 1 END) as cold
                FROM lead_scores
            """)
            stats = dict(cur.fetchone())
    finally:
        conn.close()

    return {
        "total_scored": stats["total"],
        "hot": stats["hot"],
        "warm": stats["warm"],
        "cold": stats["cold"],
        "timestamp": datetime.utcnow().isoformat()
    }


@activity.defn
async def run_agents_activity(limit: int = 3) -> dict:
    """Activity: Run AI agents for hot leads"""
    from agents.crew import run_agent_pipeline

    print(f"🤖 Running agents for top {limit} hot leads...")
    results = run_agent_pipeline(limit=limit)

    return {
        "emails_generated": len(results) if results else 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@activity.defn
async def retrain_model_activity() -> dict:
    """Activity: Retrain model if enough new outcome data"""
    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as count FROM outcomes")
            outcome_count = cur.fetchone()["count"]
    finally:
        conn.close()

    if outcome_count >= 10:
        from scoring.train import run_training
        print(f"🔄 Retraining model with {outcome_count} outcomes...")
        run_training()
        return {
            "retrained": True,
            "outcome_count": outcome_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    else:
        print(f"⏭ Skipping retraining — only {outcome_count} outcomes")
        return {
            "retrained": False,
            "outcome_count": outcome_count,
            "reason": "Not enough outcome data yet",
            "timestamp": datetime.utcnow().isoformat()
        }


@activity.defn
async def log_pipeline_run_activity(run_data: dict) -> str:
    """Activity: Log pipeline run to PostgreSQL"""
    conn = get_postgres_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO pipeline_runs (
                    workflow_id, workflow_type, status,
                    leads_discovered, leads_scored,
                    emails_generated, emails_sent,
                    started_at, completed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id
            """, (
                run_data.get("workflow_id", ""),
                run_data.get("workflow_type", "full_pipeline"),
                run_data.get("status", "completed"),
                run_data.get("leads_discovered", 0),
                run_data.get("leads_scored", 0),
                run_data.get("emails_generated", 0),
                run_data.get("emails_sent", 0),
                run_data.get("started_at", datetime.utcnow()),
                datetime.utcnow()
            ))
            result = cur.fetchone()
            conn.commit()
            return str(result["id"])
    finally:
        conn.close()