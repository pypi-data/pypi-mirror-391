from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Literal, Optional


def _drop_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}


# Jobs ------------------------------------------------------------------------


@dataclass(slots=True)
class SubmitJobRequest:
    payload: Dict[str, Any]
    priority: Optional[str] = None
    max_retries: Optional[int] = None
    timeout_ms: Optional[int] = None
    schedule_at: Optional[int] = None
    schedule_in: Optional[str] = None
    recurrence: Optional[str] = None
    job_type: Optional[str] = None
    encrypt: Optional[bool] = None
    payload_encrypted: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return _drop_none(
            {
                "payload": self.payload,
                "priority": self.priority,
                "max_retries": self.max_retries,
                "timeout_ms": self.timeout_ms,
                "schedule_at": self.schedule_at,
                "schedule_in": self.schedule_in,
                "recurrence": self.recurrence,
                "job_type": self.job_type,
                "encrypt": self.encrypt,
                "payload_encrypted": self.payload_encrypted,
            }
        )


@dataclass(slots=True)
class SubmitBatchJobRequest:
    jobs: Iterable[SubmitJobRequest]

    def to_dict(self) -> Dict[str, Any]:
        return {"jobs": [job.to_dict() for job in self.jobs]}


@dataclass(slots=True)
class SubmitJobResponse:
    job_id: str
    segment: int
    stream_id: str
    status: str


@dataclass(slots=True)
class SubmitBatchJobResponse:
    results: List[SubmitJobResponse]
    total: int
    succeeded: int
    failed: int


@dataclass(slots=True)
class CancelJobResponse:
    job_id: str
    status: str


@dataclass(slots=True)
class JobStatus:
    job_id: str
    state: str
    attempt: int
    created_at: int
    owner: Optional[str] = None
    queue: Optional[str] = None
    priority: Optional[str] = None
    payload_digest: Optional[str] = None


@dataclass(slots=True)
class JobHistoryQuery:
    job_id: Optional[str] = None
    from_ts: Optional[int] = None
    to_ts: Optional[int] = None
    event_type: Optional[str] = None
    priority: Optional[str] = None
    state: Optional[str] = None
    limit: Optional[int] = None

    def to_params(self) -> Dict[str, Any]:
        return _drop_none(
            {
                "job_id": self.job_id,
                "from": self.from_ts,
                "to": self.to_ts,
                "event_type": self.event_type,
                "priority": self.priority,
                "state": self.state,
                "limit": self.limit,
            }
        )


@dataclass(slots=True)
class JobHistoryEvent:
    job_id: str
    timestamp: int
    event_type: str
    state: str
    attempt: int
    worker_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


# DLQ -------------------------------------------------------------------------


@dataclass(slots=True)
class DlqEntry:
    job_id: str
    error: str
    failed_at: int
    segment: int


@dataclass(slots=True)
class ListDlqResponse:
    entries: List[DlqEntry] = field(default_factory=list)
    total: int = 0


@dataclass(slots=True)
class ReplayResponse:
    status: str


# Workers & Admin -------------------------------------------------------------


@dataclass(slots=True)
class WorkerMetrics:
    cpu_usage_percent: float
    memory_used_bytes: int
    memory_total_bytes: int
    jobs_in_flight: int


@dataclass(slots=True)
class WorkerStatus:
    worker_id: str
    alive: bool
    segments: List[int]
    metrics: WorkerMetrics
    last_heartbeat: Optional[int] = None


@dataclass(slots=True)
class SystemOverview:
    workers: List[WorkerStatus]
    assignments: Dict[str, List[int]]
    total_segments: int


@dataclass(slots=True)
class AuditLogEntry:
    timestamp: int
    operation: str
    component: str
    result: str
    details: Dict[str, Any] = field(default_factory=dict)
    job_id: Optional[str] = None
    worker_id: Optional[str] = None


@dataclass(slots=True)
class SchedulerControlResponse:
    status: str
    message: str
    paused: bool


@dataclass(slots=True)
class SchedulerStatus:
    status: str
    paused: bool


@dataclass(slots=True)
class QueueStatus:
    queue: str
    paused: bool
    depth: int


# Scheduled Jobs --------------------------------------------------------------


@dataclass(slots=True)
class CreateScheduledJobRequest:
    schedule: str
    payload: Dict[str, Any]
    id: Optional[str] = None
    priority: Optional[str] = None
    max_retries: Optional[int] = None
    timeout_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "schedule": self.schedule,
                "payload": self.payload,
                "priority": self.priority,
                "max_retries": self.max_retries,
                "timeout_ms": self.timeout_ms,
            }
        )


@dataclass(slots=True)
class ScheduledJobResponse:
    id: str
    schedule: str
    enabled: bool
    next_run: int
    created_at: int
    last_run: Optional[int] = None


@dataclass(slots=True)
class ScheduledJob:
    id: str
    schedule: str
    schedule_type: str
    payload: Dict[str, Any]
    priority: str
    max_retries: int
    timeout_ms: int
    enabled: bool
    next_run: int
    created_at: int
    updated_at: int
    last_run: Optional[int] = None


# Workflows -------------------------------------------------------------------

WorkflowState = Literal[
    "Pending", "Running", "Completed", "Failed", "Cancelled", "Paused"
]
DependencyType = Literal["Success", "Completion", "Failure"]


@dataclass(slots=True)
class JobDependency:
    from_job_id: str
    to_job_id: str
    dependency_type: DependencyType


@dataclass(slots=True)
class WorkflowConfig:
    max_concurrent_jobs: int
    timeout_ms: int
    continue_on_failure: bool
    retry_workflow: bool
    max_workflow_retries: int


@dataclass(slots=True)
class WorkflowJob:
    id: str
    name: str
    payload: Dict[str, Any]
    priority: str
    max_retries: int
    timeout_ms: int
    state: WorkflowState
    scheduler_job_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None


@dataclass(slots=True)
class WorkflowJobRequest:
    id: str
    name: str
    payload: Dict[str, Any]
    priority: Optional[str] = None
    max_retries: Optional[int] = None
    timeout_ms: Optional[int] = None
    state: Optional[str] = None
    scheduler_job_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _drop_none(
            {
                "id": self.id,
                "name": self.name,
                "payload": self.payload,
                "priority": self.priority,
                "max_retries": self.max_retries,
                "timeout_ms": self.timeout_ms,
                "state": self.state,
                "scheduler_job_id": self.scheduler_job_id,
                "result": self.result,
                "error": self.error,
                "started_at": self.started_at,
                "completed_at": self.completed_at,
            }
        )


@dataclass(slots=True)
class WorkflowConfigRequest:
    max_concurrent_jobs: Optional[int] = None
    timeout_ms: Optional[int] = None
    continue_on_failure: Optional[bool] = None
    retry_workflow: Optional[bool] = None
    max_workflow_retries: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return _drop_none(
            {
                "max_concurrent_jobs": self.max_concurrent_jobs,
                "timeout_ms": self.timeout_ms,
                "continue_on_failure": self.continue_on_failure,
                "retry_workflow": self.retry_workflow,
                "max_workflow_retries": self.max_workflow_retries,
            }
        )


@dataclass(slots=True)
class CreateWorkflowRequest:
    name: str
    jobs: Iterable[WorkflowJobRequest]
    id: Optional[str] = None
    description: Optional[str] = None
    dependencies: Optional[Iterable[JobDependency]] = None
    config: Optional[WorkflowConfigRequest] = None

    def to_dict(self) -> Dict[str, Any]:
        dependencies = None
        if self.dependencies is not None:
            dependencies = [
                {
                    "from_job_id": dep.from_job_id,
                    "to_job_id": dep.to_job_id,
                    "dependency_type": dep.dependency_type,
                }
                for dep in self.dependencies
            ]

        return _drop_none(
            {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "jobs": [job.to_dict() for job in self.jobs],
                "dependencies": dependencies,
                "config": self.config.to_dict() if self.config else None,
            }
        )


@dataclass(slots=True)
class WorkflowResponse:
    id: str
    name: str
    state: WorkflowState
    progress: float
    created_at: int
    started_at: Optional[int] = None
    completed_at: Optional[int] = None


@dataclass(slots=True)
class Workflow:
    id: str
    name: str
    state: WorkflowState
    jobs: List[WorkflowJob]
    dependencies: List[JobDependency]
    config: WorkflowConfig
    created_at: int
    updated_at: int
    description: Optional[str] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None


# Misc ------------------------------------------------------------------------


@dataclass(slots=True)
class HealthResponse:
    status: str
    version: str
