from __future__ import annotations

import os
import time
from typing import Iterable

import pytest

from shirly_client import (
    CreateScheduledJobRequest,
    CreateWorkflowRequest,
    JobDependency,
    JobHistoryQuery,
    QueueStatus,
    SchedulerStatus,
    ShirlyApiError,
    ShirlyClient,
    SubmitBatchJobRequest,
    SubmitJobRequest,
    WorkflowJob,
    WorkflowJobRequest,
    WorkflowResponse,
)

E2E_ENABLED = os.getenv("SHIRLY_E2E") == "1"


@pytest.fixture
def client() -> Iterable[ShirlyClient]:
    base_url = os.getenv("SHIRLY_BASE_URL", "http://localhost:8080/api/v1")
    api_key = os.getenv("SHIRLY_API_KEY")

    with ShirlyClient(
        base_url=base_url,
        api_key=api_key,
    ) as client:
        yield client


@pytest.mark.skipif(not E2E_ENABLED, reason="SHIRLY_E2E not enabled")
def test_comprehensive_api_coverage(client: ShirlyClient) -> None:
    immediate = client.submit_job(
        SubmitJobRequest(payload={"scenario": "py_e2e", "case": "immediate"})
    )
    critical = client.submit_job(
        SubmitJobRequest(
            payload={"scenario": "py_e2e", "case": "critical"}, priority="critical"
        )
    )
    schedule_in = client.submit_job(
        SubmitJobRequest(
            payload={"scenario": "py_e2e", "case": "schedule_in"}, schedule_in="5s"
        )
    )
    schedule_at = client.submit_job(
        SubmitJobRequest(
            payload={"scenario": "py_e2e", "case": "schedule_at"},
            schedule_at=int(time.time() * 1000) + 10_000,
        )
    )
    recurring = client.submit_job(
        SubmitJobRequest(
            payload={"scenario": "py_e2e", "case": "recurring"},
            schedule_in="5s",
            recurrence="FREQ=MINUTELY;COUNT=2",
        )
    )

    batch = client.submit_job_batch(
        SubmitBatchJobRequest(
            jobs=[
                SubmitJobRequest(
                    payload={"scenario": "py_e2e", "case": "batch_normal"}
                ),
                SubmitJobRequest(
                    payload={"scenario": "py_e2e", "case": "batch_critical"},
                    priority="critical",
                ),
            ]
        )
    )
    assert batch.succeeded == len(batch.results)

    for job in [
        immediate,
        critical,
        schedule_in,
        schedule_at,
        recurring,
        *batch.results,
    ]:
        _wait_for_job(client, job.job_id)

    history = list(
        client.get_job_history(JobHistoryQuery(job_id=immediate.job_id, limit=50))
    )
    assert history is not None

    dlq = client.list_dlq()
    if dlq.entries:
        client.replay_dlq(dlq.entries[0].job_id)

    workers = list(client.list_workers())
    assert workers, "expected at least one worker"

    overview = client.get_system_overview()
    assert overview.total_segments >= 0

    list(client.list_audit_logs(limit=5))

    try:
        client.pause_scheduler()
    except ShirlyApiError as exc:
        assert exc.status_code in (400, 404)
    client.resume_scheduler()
    scheduler_status = client.get_scheduler_status()
    assert isinstance(scheduler_status, SchedulerStatus)

    queues = list(client.list_queues())
    if queues:
        queue_name = queues[0].queue
        _toggle_queue(client, queue_name)

    scheduled_id = f"py-e2e-{int(time.time())}"
    client.create_scheduled_job(
        CreateScheduledJobRequest(
            id=scheduled_id,
            schedule="0/30 * * * * * *",
            payload={"scenario": "py_e2e", "case": "scheduled"},
            priority="normal",
            max_retries=1,
            timeout_ms=60_000,
        )
    )
    client.get_scheduled_job(scheduled_id)
    list(client.list_scheduled_jobs(limit=50))
    client.delete_scheduled_job(scheduled_id)

    workflow = client.create_workflow(
        CreateWorkflowRequest(
            name=f"py-e2e-workflow-{int(time.time())}",
            jobs=[
                WorkflowJobRequest(
                    id="step_a",
                    name="Step A",
                    payload={"scenario": "py_e2e", "case": "workflow_a"},
                    state="Waiting",
                ),
                WorkflowJobRequest(
                    id="step_b",
                    name="Step B",
                    payload={"scenario": "py_e2e", "case": "workflow_b"},
                    state="Waiting",
                ),
            ],
            dependencies=[
                JobDependency(
                    from_job_id="step_a", to_job_id="step_b", dependency_type="Success"
                )
            ],
        )
    )
    assert isinstance(workflow, WorkflowResponse)
    _wait_for_workflow(client, workflow.id)

    cancel_workflow = client.create_workflow(
        CreateWorkflowRequest(
            name=f"py-e2e-cancel-{int(time.time())}",
            jobs=[
                WorkflowJobRequest(
                    id="cancel_step",
                    name="Cancel Step",
                    payload={"scenario": "py_e2e", "case": "workflow_cancel"},
                    state="Waiting",
                ),
            ],
            dependencies=[],
        )
    )
    try:
        client.cancel_workflow(cancel_workflow.id)
    except ShirlyApiError as exc:
        assert exc.status_code in (400, 404)
    _wait_for_workflow(
        client, cancel_workflow.id, allow_states=("Cancelled", "Completed", "Failed")
    )

    metrics = client.get_metrics()
    assert metrics

    openapi = client.get_openapi_spec()
    assert "openapi" in openapi

    health = client.health()
    assert health.status.lower() == "healthy"


@pytest.mark.skipif(E2E_ENABLED, reason="Runs only when SHIRLY_E2E is not set")
def test_skip_when_disabled() -> None:
    pytest.skip("Integration suite requires SHIRLY_E2E=1")


def _wait_for_job(client: ShirlyClient, job_id: str, *, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            status = client.get_job_status(job_id)
        except ShirlyApiError as exc:
            if exc.status_code == 404:
                time.sleep(0.5)
                continue
            raise
        if status.state in {"completed", "failed", "pending", "scheduled"}:
            return
        time.sleep(0.5)
    raise AssertionError(f"Job {job_id} did not reach a terminal state")


def _wait_for_workflow(
    client: ShirlyClient,
    workflow_id: str,
    *,
    timeout: float = 120.0,
    allow_states: Iterable[str] = ("Completed", "Failed", "Running"),
) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        workflow = client.get_workflow(workflow_id)
        if workflow.state in allow_states:
            return
        time.sleep(1.0)
    raise AssertionError(f"Workflow {workflow_id} did not reach expected state")


def _toggle_queue(client: ShirlyClient, queue: str) -> None:
    try:
        paused = client.pause_queue(queue)
        assert isinstance(paused, QueueStatus)
    except ShirlyApiError as exc:
        if exc.status_code not in (400, 404):
            raise
    try:
        resumed = client.resume_queue(queue)
        assert isinstance(resumed, QueueStatus)
    except ShirlyApiError as exc:
        if exc.status_code not in (400, 404):
            raise
