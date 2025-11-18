from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, cast

import httpx

from .models import (
    AuditLogEntry,
    CancelJobResponse,
    CreateScheduledJobRequest,
    CreateWorkflowRequest,
    DlqEntry,
    HealthResponse,
    JobDependency,
    JobHistoryEvent,
    JobHistoryQuery,
    JobStatus,
    ListDlqResponse,
    QueueStatus,
    ReplayResponse,
    SchedulerControlResponse,
    SchedulerStatus,
    ScheduledJob,
    ScheduledJobResponse,
    SubmitBatchJobRequest,
    SubmitBatchJobResponse,
    SubmitJobRequest,
    SubmitJobResponse,
    SystemOverview,
    Workflow,
    WorkflowConfig,
    WorkflowJob,
    WorkflowState,
    WorkflowResponse,
    WorkerMetrics,
    WorkerStatus,
)


DEFAULT_TIMEOUT = 30.0


class ShirlyApiError(RuntimeError):
    def __init__(self, status_code: int, body: Any) -> None:
        super().__init__(f"Shirly API error {status_code}: {body!r}")
        self.status_code = status_code
        self.body = body


@dataclass(slots=True)
class ShirlyClientConfig:
    base_url: str = "http://localhost:8080/api/v1"
    api_key: Optional[str] = None
    timeout: float = DEFAULT_TIMEOUT
    headers: Optional[Dict[str, str]] = None


class ShirlyClient:
    def __init__(
        self,
        base_url: str = "http://localhost:8080/api/v1",
        api_key: Optional[str] = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        headers: Optional[Dict[str, str]] = None,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._base_headers = dict(headers or {})
        if api_key:
            self._base_headers["Authorization"] = f"Bearer {api_key}"

        self._client = client or httpx.Client(base_url=self._base_url, timeout=timeout)
        self._owns_client = client is None
        self._timeout = timeout

    def __enter__(self) -> "ShirlyClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    # Jobs ------------------------------------------------------------------

    def submit_job(self, request: SubmitJobRequest) -> SubmitJobResponse:
        data = self._request("POST", "/jobs", json=request.to_dict())
        return SubmitJobResponse(**data)

    def submit_job_batch(
        self, request: SubmitBatchJobRequest
    ) -> SubmitBatchJobResponse:
        data = self._request("POST", "/jobs/batch", json=request.to_dict())
        results = [SubmitJobResponse(**item) for item in data.get("results", [])]
        return SubmitBatchJobResponse(
            results=results,
            total=data.get("total", 0),
            succeeded=data.get("succeeded", 0),
            failed=data.get("failed", 0),
        )

    def cancel_job(self, job_id: str) -> CancelJobResponse:
        data = self._request("POST", f"/jobs/{job_id}/cancel")
        return CancelJobResponse(**data)

    def get_job_status(self, job_id: str) -> JobStatus:
        data = self._request("GET", f"/jobs/{job_id}")
        return JobStatus(**data)

    def get_job_history(
        self, query: Optional[JobHistoryQuery] = None
    ) -> Iterable[JobHistoryEvent]:
        params = query.to_params() if query else None
        data = self._request("GET", "/jobs/history", params=params)
        return [JobHistoryEvent(**item) for item in data or []]

    # DLQ -------------------------------------------------------------------

    def list_dlq(self, **params: Any) -> ListDlqResponse:
        data = self._request("GET", "/admin/dlq", params=params)
        entries = [DlqEntry(**entry) for entry in data.get("entries", [])]
        return ListDlqResponse(entries=entries, total=data.get("total", 0))

    def replay_dlq(self, job_id: str) -> ReplayResponse:
        data = self._request("POST", "/admin/dlq/replay", json={"job_id": job_id})
        return ReplayResponse(**data)

    # Admin / workers -------------------------------------------------------

    def list_workers(self) -> Iterable[WorkerStatus]:
        data = self._request("GET", "/admin/workers")
        workers = []
        for entry in data or []:
            metrics = WorkerMetrics(**entry.get("metrics", {}))
            workers.append(
                WorkerStatus(
                    worker_id=entry["worker_id"],
                    alive=entry["alive"],
                    segments=entry.get("segments", []),
                    metrics=metrics,
                    last_heartbeat=entry.get("last_heartbeat"),
                )
            )
        return workers

    def get_system_overview(self) -> SystemOverview:
        data = self._request("GET", "/admin/overview")
        workers = []
        for entry in data.get("workers", []):
            metrics = WorkerMetrics(**entry.get("metrics", {}))
            workers.append(
                WorkerStatus(
                    worker_id=entry["worker_id"],
                    alive=entry["alive"],
                    segments=entry.get("segments", []),
                    metrics=metrics,
                    last_heartbeat=entry.get("last_heartbeat"),
                )
            )
        return SystemOverview(
            workers=workers,
            assignments=data.get("assignments", {}),
            total_segments=data.get("total_segments", 0),
        )

    def list_audit_logs(
        self, *, limit: Optional[int] = None
    ) -> Iterable[AuditLogEntry]:
        params = {"limit": limit} if limit is not None else None
        data = self._request("GET", "/admin/audit-logs", params=params)
        return [AuditLogEntry(**entry) for entry in data or []]

    def pause_scheduler(self) -> SchedulerControlResponse:
        data = self._request("POST", "/admin/control/pause")
        return SchedulerControlResponse(**data)

    def resume_scheduler(self) -> SchedulerControlResponse:
        data = self._request("POST", "/admin/control/resume")
        return SchedulerControlResponse(**data)

    def get_scheduler_status(self) -> SchedulerStatus:
        data = self._request("GET", "/admin/control/status")
        return SchedulerStatus(**data)

    def list_queues(self) -> Iterable[QueueStatus]:
        data = self._request("GET", "/admin/queues")
        return [QueueStatus(**entry) for entry in data or []]

    def pause_queue(self, queue: str) -> QueueStatus:
        data = self._request("POST", f"/admin/queues/{queue}/pause")
        return QueueStatus(**data)

    def resume_queue(self, queue: str) -> QueueStatus:
        data = self._request("POST", f"/admin/queues/{queue}/resume")
        return QueueStatus(**data)

    # Scheduled jobs --------------------------------------------------------

    def create_scheduled_job(
        self, request: CreateScheduledJobRequest
    ) -> ScheduledJobResponse:
        data = self._request("POST", "/scheduled-jobs", json=request.to_dict())
        return ScheduledJobResponse(**data)

    def get_scheduled_job(self, job_id: str) -> ScheduledJob:
        data = self._request("GET", f"/scheduled-jobs/{job_id}")
        return ScheduledJob(**data)

    def list_scheduled_jobs(
        self, limit: Optional[int] = None
    ) -> Iterable[ScheduledJob]:
        params = {"limit": limit} if limit is not None else None
        data = self._request("GET", "/scheduled-jobs", params=params)
        return [ScheduledJob(**entry) for entry in data or []]

    def delete_scheduled_job(self, job_id: str) -> None:
        self._request("DELETE", f"/scheduled-jobs/{job_id}")

    # Workflows -------------------------------------------------------------

    def create_workflow(self, request: CreateWorkflowRequest) -> WorkflowResponse:
        data = self._request("POST", "/workflows", json=request.to_dict())
        return WorkflowResponse(**data)

    def get_workflow(self, workflow_id: str) -> Workflow:
        data = self._request("GET", f"/workflows/{workflow_id}")
        workflow_jobs = [
            WorkflowJob(
                id=job["id"],
                name=job["name"],
                payload=job.get("payload", {}),
                priority=job.get("priority", "normal"),
                max_retries=job.get("max_retries", 0),
                timeout_ms=job.get("timeout_ms", 0),
                state=cast(WorkflowState, job.get("state", "Pending")),
                scheduler_job_id=job.get("scheduler_job_id"),
                result=job.get("result"),
                error=job.get("error"),
                started_at=job.get("started_at"),
                completed_at=job.get("completed_at"),
            )
            for job in data.get("jobs", [])
        ]
        dependencies = [JobDependency(**dep) for dep in data.get("dependencies", [])]
        config_data = data.get("config", {})
        config = WorkflowConfig(
            max_concurrent_jobs=config_data.get("max_concurrent_jobs", 0),
            timeout_ms=config_data.get("timeout_ms", 0),
            continue_on_failure=config_data.get("continue_on_failure", False),
            retry_workflow=config_data.get("retry_workflow", False),
            max_workflow_retries=config_data.get("max_workflow_retries", 0),
        )
        return Workflow(
            id=data["id"],
            name=data["name"],
            state=data["state"],
            jobs=workflow_jobs,
            dependencies=dependencies,
            config=config,
            description=data.get("description"),
            created_at=data.get("created_at", 0),
            updated_at=data.get("updated_at", 0),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
        )

    def list_workflows(self) -> Iterable[WorkflowResponse]:
        data = self._request("GET", "/workflows")
        return [WorkflowResponse(**entry) for entry in data or []]

    def cancel_workflow(self, workflow_id: str) -> None:
        self._request("POST", f"/workflows/{workflow_id}/cancel")

    # System ----------------------------------------------------------------

    def get_metrics(self) -> str:
        return self._request("GET", "/metrics", accept="text/plain") or ""

    def get_openapi_spec(self) -> Dict[str, Any]:
        return self._request("GET", "/openapi.json") or {}

    def health(self) -> HealthResponse:
        data = self._request("GET", "/health")
        return HealthResponse(**data)

    # Internal --------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        accept: str = "application/json",
    ) -> Any:
        headers = dict(self._base_headers)
        headers["accept"] = accept

        if json is not None:
            headers.setdefault("content-type", "application/json")

        try:
            response = self._client.request(
                method,
                path,
                params=params,
                json=json,
                headers=headers,
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise RuntimeError(f"HTTP request to {path} failed: {exc}") from exc

        if response.status_code < 200 or response.status_code >= 300:
            body: Any
            if "application/json" in response.headers.get("content-type", ""):
                body = response.json()
            else:
                body = response.text
            raise ShirlyApiError(response.status_code, body)

        if accept == "text/plain":
            return response.text

        if not response.content:
            return None

        if "application/json" in response.headers.get("content-type", ""):
            return response.json()

        return response.text
