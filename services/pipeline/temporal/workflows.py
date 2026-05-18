from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from pipeline.temporal.activities import (
        discover_leads_activity,
        find_emails_activity,
        score_leads_activity,
        run_agents_activity,
        retrain_model_activity,
        log_pipeline_run_activity
    )


@workflow.defn
class FullPipelineWorkflow:
    """
    Full pipeline: Discover → Email → Score → Agents → Retrain
    Runs on schedule via Temporal
    """

    @workflow.run
    async def run(self, cities: list[str] = None) -> dict:
        cities = cities or ["Boston", "New York", "Chicago",
                           "San Francisco", "Austin"]

        started_at = workflow.now()
        run_id = workflow.info().workflow_id

        print(f"\n🚀 Pipeline started: {run_id}")
        print(f"   Cities: {cities}")

        retry_policy = RetryPolicy(
            maximum_attempts=3,
            initial_interval=timedelta(seconds=5)
        )

        results = {}

        # Step 1 — Discover
        print("\n📍 Step 1: Discovery")
        discovery = await workflow.execute_activity(
            discover_leads_activity,
            cities,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry_policy
        )
        results["discovery"] = discovery
        print(f"   ✅ Found {discovery['discovered']} businesses")

        # Step 2 — Emails
        print("\n📧 Step 2: Email Discovery")
        emails = await workflow.execute_activity(
            find_emails_activity,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry_policy
        )
        results["emails"] = emails
        print(f"   ✅ Email discovery complete")

        # Step 3 — Score
        print("\n🎯 Step 3: Lead Scoring")
        scoring = await workflow.execute_activity(
            score_leads_activity,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy
        )
        results["scoring"] = scoring
        print(f"   ✅ Scored — Hot: {scoring['hot']} Warm: {scoring['warm']}")

        # Step 4 — Agents
        print("\n🤖 Step 4: AI Agents")
        agents = await workflow.execute_activity(
            run_agents_activity,
            3,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=2)
        )
        results["agents"] = agents
        print(f"   ✅ Generated {agents['emails_generated']} emails")

        # Step 5 — Retrain
        print("\n🔄 Step 5: Model Retraining Check")
        retrain = await workflow.execute_activity(
            retrain_model_activity,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry_policy
        )
        results["retrain"] = retrain

        # Step 6 — Log
        await workflow.execute_activity(
            log_pipeline_run_activity,
            {
                "workflow_id": run_id,
                "workflow_type": "full_pipeline",
                "status": "completed",
                "leads_discovered": discovery["discovered"],
                "leads_scored": scoring["total_scored"],
                "emails_generated": agents["emails_generated"],
                "emails_sent": 0,
                "started_at": started_at.isoformat()
            },
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy
        )

        print(f"\n✅ Pipeline complete!")
        return results


@workflow.defn
class ScoringOnlyWorkflow:
    """Lightweight workflow — just score existing leads"""

    @workflow.run
    async def run(self) -> dict:
        print("\n🎯 Running scoring-only pipeline...")

        scoring = await workflow.execute_activity(
            score_leads_activity,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )

        return scoring