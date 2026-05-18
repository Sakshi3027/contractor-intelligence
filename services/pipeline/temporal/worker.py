import asyncio
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from temporalio.client import Client
from temporalio.worker import Worker
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from pipeline.temporal.workflows import (
    FullPipelineWorkflow,
    ScoringOnlyWorkflow
)
from pipeline.temporal.activities import (
    discover_leads_activity,
    find_emails_activity,
    score_leads_activity,
    run_agents_activity,
    retrain_model_activity,
    log_pipeline_run_activity
)


async def main():
    print("🔧 Connecting to Temporal...")
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233")
    )
    print("✅ Connected to Temporal")

    worker = Worker(
        client,
        task_queue="contractor-pipeline",
        workflows=[FullPipelineWorkflow, ScoringOnlyWorkflow],
        activities=[
            discover_leads_activity,
            find_emails_activity,
            score_leads_activity,
            run_agents_activity,
            retrain_model_activity,
            log_pipeline_run_activity
        ]
    )

    print("🚀 Worker started — listening on 'contractor-pipeline' queue")
    print("   Workflows: FullPipelineWorkflow, ScoringOnlyWorkflow")
    print("   Press Ctrl+C to stop\n")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())