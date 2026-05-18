import asyncio
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from temporalio.client import Client
from temporalio.common import WorkflowIDReusePolicy
from dotenv import load_dotenv
import uuid

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from pipeline.temporal.workflows import (
    FullPipelineWorkflow,
    ScoringOnlyWorkflow
)


async def run_full_pipeline(cities: list[str] = None):
    """Trigger a full pipeline run"""
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233")
    )

    workflow_id = f"full-pipeline-{uuid.uuid4().hex[:8]}"

    print(f"🚀 Starting FullPipelineWorkflow: {workflow_id}")

    handle = await client.start_workflow(
        FullPipelineWorkflow.run,
        cities or ["Boston", "New York", "Chicago"],
        id=workflow_id,
        task_queue="contractor-pipeline",
    )

    print(f"✅ Workflow started: {handle.id}")
    print(f"🔗 View at: http://localhost:8888/namespaces/default/workflows")
    print("\n⏳ Waiting for completion...")

    result = await handle.result()
    print("\n📊 Pipeline Results:")
    import json
    print(json.dumps(result, indent=2, default=str))
    return result


async def run_scoring_only():
    """Trigger scoring-only pipeline"""
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233")
    )

    workflow_id = f"scoring-{uuid.uuid4().hex[:8]}"

    handle = await client.start_workflow(
        ScoringOnlyWorkflow.run,
        id=workflow_id,
        task_queue="contractor-pipeline",
    )

    result = await handle.result()
    print(f"✅ Scoring complete: {result}")
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "scoring":
        asyncio.run(run_scoring_only())
    else:
        asyncio.run(run_full_pipeline())