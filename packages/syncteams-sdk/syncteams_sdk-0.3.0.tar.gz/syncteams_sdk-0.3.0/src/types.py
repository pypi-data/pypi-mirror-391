"""Shared type definitions and constants for the SyncTeams Python SDK."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import Event
from typing import Any, Callable, List, Mapping, MutableMapping, Optional, Sequence, TypedDict

from typing_extensions import NotRequired

from .event_types import ExecutionEvent


class WorkflowStatus(str, Enum):
    """Enum representing the possible workflow execution statuses."""
    QUEUED = "QUEUED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class ApprovalDecision(str, Enum):
    """Enum representing approval decisions for waiting workflows."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class WorkflowEventType(str, Enum):
    """Enum representing the types of events emitted during workflow execution."""
    UserInputEvent = "UserInputEvent"
    ConnectorInputEvent = "ConnectorInputEvent"
    TaskApprovalRequestEvent = "TaskApprovalRequestEvent"
    TaskApprovalResponseEvent = "TaskApprovalResponseEvent"
    CrewKickoffStartedEvent = "CrewKickoffStartedEvent"
    CrewKickoffCompletedEvent = "CrewKickoffCompletedEvent"
    CrewKickoffFailedEvent = "CrewKickoffFailedEvent"
    CrewTestStartedEvent = "CrewTestStartedEvent"
    CrewTestCompletedEvent = "CrewTestCompletedEvent"
    CrewTestFailedEvent = "CrewTestFailedEvent"
    CrewTrainStartedEvent = "CrewTrainStartedEvent"
    CrewTrainCompletedEvent = "CrewTrainCompletedEvent"
    CrewTestResultEvent = "CrewTestResultEvent"
    CrewTrainFailedEvent = "CrewTrainFailedEvent"
    AgentExecutionStartedEvent = "AgentExecutionStartedEvent"
    AgentExecutionCompletedEvent = "AgentExecutionCompletedEvent"
    AgentExecutionErrorEvent = "AgentExecutionErrorEvent"
    AgentReasoningStartedEvent = "AgentReasoningStartedEvent"
    AgentReasoningCompletedEvent = "AgentReasoningCompletedEvent"
    AgentReasoningFailedEvent = "AgentReasoningFailedEvent"
    TaskStartedEvent = "TaskStartedEvent"
    TaskCompletedEvent = "TaskCompletedEvent"
    TaskFailedEvent = "TaskFailedEvent"
    TaskEvaluationEvent = "TaskEvaluationEvent"
    TaskOutput = "TaskOutput"
    ToolUsageStartedEvent = "ToolUsageStartedEvent"
    ToolUsageFinishedEvent = "ToolUsageFinishedEvent"
    ToolUsageErrorEvent = "ToolUsageErrorEvent"
    ToolValidateInputErrorEvent = "ToolValidateInputErrorEvent"
    ToolExecutionErrorEvent = "ToolExecutionErrorEvent"
    ToolSelectionErrorEvent = "ToolSelectionErrorEvent"
    KnowledgeRetrievalStartedEvent = "KnowledgeRetrievalStartedEvent"
    KnowledgeRetrievalCompletedEvent = "KnowledgeRetrievalCompletedEvent"
    KnowledgeQueryStartedEvent = "KnowledgeQueryStartedEvent"
    KnowledgeQueryCompletedEvent = "KnowledgeQueryCompletedEvent"
    KnowledgeQueryFailedEvent = "KnowledgeQueryFailedEvent"
    KnowledgeSearchQueryFailedEvent = "KnowledgeSearchQueryFailedEvent"
    FlowCreatedEvent = "FlowCreatedEvent"
    FlowStartedEvent = "FlowStartedEvent"
    FlowFinishedEvent = "FlowFinishedEvent"
    FlowPlotEvent = "FlowPlotEvent"
    MethodExecutionStartedEvent = "MethodExecutionStartedEvent"
    MethodExecutionFinishedEvent = "MethodExecutionFinishedEvent"
    MethodExecutionFailedEvent = "MethodExecutionFailedEvent"
    LLMCallStartedEvent = "LLMCallStartedEvent"
    LLMCallCompletedEvent = "LLMCallCompletedEvent"
    LLMCallFailedEvent = "LLMCallFailedEvent"
    LLMStreamChunkEvent = "LLMStreamChunkEvent"


class TaskEventLog(TypedDict, total=False):
    eventType: str  # WorkflowEventType enum or custom string
    eventData: ExecutionEvent
    createdAt: str
    updatedAt: str


class ExecuteWorkflowInput(TypedDict):
    workflowId: str
    input: Mapping[str, Any]
    uniqueId: NotRequired[str]


class ExecuteWorkflowResponse(TypedDict):
    taskId: str
    status: WorkflowStatus


class TaskStatusResponse(ExecuteWorkflowResponse, total=False):
    eventLogs: List[TaskEventLog]


class WebhookEventPayload(TypedDict, total=False):
    taskId: str
    uniqueId: str
    status: WorkflowStatus
    eventLogs: List[TaskEventLog]


class WorkflowClientRetryConfig(TypedDict, total=False):
    max_attempts: int
    initial_delay_ms: int
    backoff_factor: float
    max_delay_ms: int
    retry_on_statuses: Sequence[int]


class WorkflowClientOptions(TypedDict, total=False):
    base_url: str
    api_key: str
    timeout_ms: int
    default_headers: Mapping[str, str]
    retry: WorkflowClientRetryConfig
    user_agent_suffix: str


WaitForCompletionCallback = Callable[[TaskStatusResponse], None]


class WaitForCompletionOptions(TypedDict, total=False):
    poll_interval_ms: int
    max_wait_time_ms: int
    terminal_statuses: Sequence[WorkflowStatus]
    exit_on_waiting: bool
    stop_event: Event
    on_update: WaitForCompletionCallback


class ExecuteAndWaitOptions(WaitForCompletionOptions, total=False):
    on_waiting: Callable[[TaskStatusResponse], bool]


DEFAULT_REQUEST_TIMEOUT_MS = 30_000
DEFAULT_POLL_INTERVAL_MS = 2_000
DEFAULT_MAX_WAIT_TIME_MS = 10 * 60 * 1000  # 10 minutes
DEFAULT_BASE_URL = "https://develop.api.syncteams.studio"


@dataclass
class RequestDescriptor:
    """Minimal request metadata used when raising :class:`WorkflowAPIError`."""

    method: str
    url: str
    body: Optional[Any] = None


Headers = MutableMapping[str, str]
