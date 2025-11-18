# Python Client Guide

This guide covers the Python SDK bundled in `clients/python`. It assumes the Shirly backend is running (`scheduler-api` and at least one `scheduler-worker`) per `../binaries_setup.md`.

## 1. Install Dependencies

The project uses `uv` for dependency management. From `clients/python`:

```bash
cd clients/python
uv sync
```

To install into another project, you can publish the package or use a local path in `pyproject.toml`.

## 2. Configuration

Environment variables:

- `SHIRLY_API_URL` (default `http://localhost:8080/api/v1`)
- `SHIRLY_API_KEY` (optional bearer token)

## 3. Basic Usage

```python
from shirly_client import ShirlyClient, SubmitJobRequest

client = ShirlyClient(
    base_url="http://localhost:8080/api/v1",
    api_key=None,
    timeout=30.0,
)

request = SubmitJobRequest(
    priority="critical",  # optional; defaults to "normal"
    payload={"kind": "email", "to": "ops@example.com"},
    max_retries=3,
)

job = client.submit_job(request)
print("job id", job.job_id)

status = client.get_job_status(job.job_id)
print("job state", status.state)
```

### Priority Options

- `"critical"` — routed through the high-priority stream queue
- `"normal"` (default) — standard list queue

## 4. Scheduling & Workflows

Helpers include:

- `client.create_scheduled_job(CreateScheduledJobRequest(...))`
- `client.create_workflow(CreateWorkflowRequest(...))`
- `client.submit_job_batch(SubmitBatchJobRequest(...))`

Refer to `clients/python/shirly_client/models.py` for request dataclasses.

## 5. Administration APIs

```python
client.list_workers()
client.list_dlq(limit=50)
client.pause_queue("default")
client.get_system_overview()
```

Ensure the API gateway is configured with necessary authentication before exposing admin endpoints.

## 6. Testing

Run the integration suite (requires live API/worker):

```bash
uv run pytest
```

Set the environment variables to point at staging or production when packaging tutorials for end users.

Use this guide to document or onboard teams using the Python client.

