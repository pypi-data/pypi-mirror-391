"""High-level SyncTeams Workflow client."""
from __future__ import annotations

import time
from threading import Event
from typing import Any, Callable, Mapping, MutableMapping, Sequence

from requests import Session

from .errors import WorkflowAPIError
from .http import HttpClient
from .types import (
    ApprovalDecision,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_WAIT_TIME_MS,
    DEFAULT_POLL_INTERVAL_MS,
    ExecuteWorkflowResponse,
    TaskStatusResponse,
    WaitForCompletionCallback,
    WorkflowClientRetryConfig,
    WorkflowStatus,
    RequestDescriptor,
)

TERMINAL_STATUSES: tuple[WorkflowStatus, ...] = (
    WorkflowStatus.COMPLETED,
    WorkflowStatus.FAILED,
    WorkflowStatus.CANCELED,
)


class WorkflowClient:
    """Client for interacting with the SyncTeams Workflow API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str | None = None,
        timeout_ms: int | None = None,
        default_headers: Mapping[str, str] | None = None,
        retry: WorkflowClientRetryConfig | None = None,
        user_agent_suffix: str | None = None,
        session: Session | None = None,
        http_client: HttpClient | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required when constructing WorkflowClient")

        base_url = base_url or DEFAULT_BASE_URL

        self._http = http_client or HttpClient(
            base_url=base_url,
            api_key=api_key,
            timeout_ms=timeout_ms,
            default_headers=default_headers,
            retry=retry,
            user_agent_suffix=user_agent_suffix,
            session=session,
        )

    def execute_workflow(
        self,
        *,
        workflow_id: str,
        input: Mapping[str, Any],
        unique_id: str | None = None,
    ) -> ExecuteWorkflowResponse:
        self._assert_string(workflow_id, "workflow_id")
        self._ensure_serializable(input, "input")
        payload: MutableMapping[str, Any] = {
            "workflowId": workflow_id,
            "input": input,
        }
        if unique_id is not None:
            self._assert_string(unique_id, "unique_id")
            payload["uniqueId"] = unique_id

        return self._http.request(
            "/api/v1",
            method="POST",
            body=payload,
        )

    def get_task_status(self, task_id: str) -> TaskStatusResponse:
        self._assert_string(task_id, "task_id")
        params = {"taskId": task_id}
        return self._http.request(
            "/api/v1/status",
            method="GET",
            params=params,
        )

    def continue_task(
        self,
        *,
        task_id: str,
        decision: ApprovalDecision,
        message: str | None = None,
    ) -> TaskStatusResponse:
        self._assert_string(task_id, "task_id")

        if decision == ApprovalDecision.REJECT and not message:
            raise ValueError("message is required when decision is 'REJECT'")

        if message is not None:
            self._assert_string(message, "message")

        payload: MutableMapping[str, Any] = {
            "taskId": task_id,
            "type": decision,
        }
        if message is not None:
            payload["message"] = message

        return self._http.request(
            "/api/v1/continue",
            method="POST",
            body=payload,
        )

    def wait_for_completion(
        self,
        task_id: str,
        *,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS,
        max_wait_time_ms: int = DEFAULT_MAX_WAIT_TIME_MS,
        terminal_statuses: Sequence[WorkflowStatus] | None = None,
        exit_on_waiting: bool = False,
        stop_event: Event | None = None,
        on_update: WaitForCompletionCallback | None = None,
    ) -> TaskStatusResponse:
        self._assert_string(task_id, "task_id")

        terminal_set = set(terminal_statuses or TERMINAL_STATUSES)
        started_at = time.monotonic()
        last_status: WorkflowStatus | None = None
        poll_seconds = max(poll_interval_ms, 100) / 1000.0

        while True:
            if stop_event and stop_event.is_set():
                raise self._aborted_error(task_id)

            status = self.get_task_status(task_id)
            current_status = status.get("status")

            if current_status != last_status and on_update:
                on_update(status)
            last_status = current_status  # type: ignore[assignment]

            if current_status in terminal_set:
                return status

            if exit_on_waiting and current_status == WorkflowStatus.WAITING:
                return status

            elapsed_ms = (time.monotonic() - started_at) * 1000
            if elapsed_ms >= max_wait_time_ms:
                raise WorkflowAPIError(
                    message=f"Timed out after {max_wait_time_ms}ms waiting for task {task_id}",
                    status=0,
                    status_text="POLL_TIMEOUT",
                    headers={},
                    data={
                        "taskId": task_id,
                        "lastStatus": current_status,
                    },
                    request=RequestDescriptor(
                        method="GET",
                        url=f"/api/v1/status?taskId={task_id}",
                    ),
                )

            if stop_event and stop_event.wait(poll_seconds):
                raise self._aborted_error(task_id)

            if not stop_event:
                time.sleep(poll_seconds)

        # pragma: no cover - loop always returns or raises

    def execute_and_wait(
        self,
        *,
        workflow_id: str,
        input: Mapping[str, Any],
        unique_id: str | None = None,
        poll_interval_ms: int = DEFAULT_POLL_INTERVAL_MS,
        max_wait_time_ms: int = DEFAULT_MAX_WAIT_TIME_MS,
        terminal_statuses: Sequence[WorkflowStatus] | None = None,
        exit_on_waiting: bool = False,
        stop_event: Event | None = None,
        on_update: WaitForCompletionCallback | None = None,
    on_waiting: Callable[[TaskStatusResponse], bool] | None = None,
    ) -> TaskStatusResponse:
        initial = self.execute_workflow(
            workflow_id=workflow_id,
            input=input,
            unique_id=unique_id,
        )

        wait_kwargs = dict(
            poll_interval_ms=poll_interval_ms,
            max_wait_time_ms=max_wait_time_ms,
            terminal_statuses=terminal_statuses,
            stop_event=stop_event,
            on_update=on_update,
        )

        if not on_waiting:
            return self.wait_for_completion(
                initial["taskId"],
                exit_on_waiting=exit_on_waiting,
                **wait_kwargs,
            )

        while True:
            current = self.wait_for_completion(
                initial["taskId"],
                exit_on_waiting=True,
                **wait_kwargs,
            )

            if current.get("status") != WorkflowStatus.WAITING:
                return current

            should_continue = on_waiting(current)
            if not should_continue:
                return current

    @staticmethod
    def _assert_string(value: Any, field: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a non-empty string")

    @staticmethod
    def _ensure_serializable(value: Any, field: str) -> None:
        try:
            import json

            json.dumps(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field} must be JSON serializable") from exc

    @staticmethod
    def _aborted_error(task_id: str) -> WorkflowAPIError:
        return WorkflowAPIError(
            message=f"Polling aborted for task {task_id}",
            status=0,
            status_text="POLL_ABORTED",
            headers={},
            data={"taskId": task_id},
            request=RequestDescriptor(
                method="GET",
                url=f"/api/v1/status?taskId={task_id}",
            ),
        )
