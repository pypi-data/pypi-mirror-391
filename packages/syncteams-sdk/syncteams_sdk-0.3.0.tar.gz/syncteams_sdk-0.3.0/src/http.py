"""Low-level HTTP helper with retry/backoff logic for the SyncTeams SDK."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional, Sequence

import requests
from requests import Response, Session
from requests.exceptions import RequestException

from .errors import WorkflowAPIError
from .types import (
    DEFAULT_REQUEST_TIMEOUT_MS,
    Headers,
    RequestDescriptor,
    WorkflowClientRetryConfig,
)
from ._version import __version__

DEFAULT_RETRYABLE_STATUSES = [408, 425, 429]


@dataclass(frozen=True)
class ResolvedRetryConfig:
    max_attempts: int
    initial_delay_ms: int
    backoff_factor: float
    max_delay_ms: int
    retry_on_statuses: tuple[int, ...]


class HttpClient:
    """Small wrapper around :mod:`requests` with SyncTeams-friendly defaults."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_ms: int | None = None,
        default_headers: Mapping[str, str] | None = None,
        retry: WorkflowClientRetryConfig | None = None,
        user_agent_suffix: str | None = None,
        session: Session | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must be provided")
        if not base_url:
            raise ValueError("base_url must be provided")

        self._base_url = base_url.rstrip("/")
        self._timeout_ms = timeout_ms or DEFAULT_REQUEST_TIMEOUT_MS
        self._retry = self._normalize_retry_config(retry)
        self._session = session or requests.Session()
        self._default_headers = self._build_default_headers(
            api_key, default_headers, user_agent_suffix
        )

    def request(
        self,
        path: str,
        *,
        method: str = "GET",
        headers: Mapping[str, str] | Headers | None = None,
        params: Mapping[str, Any] | None = None,
        body: Any | None = None,
        timeout_ms: int | None = None,
        retry: WorkflowClientRetryConfig | None = None,
    ) -> Any:
        method = method.upper()
        url = self._resolve_url(path)
        merged_headers = self._merge_headers(headers, body)
        timeout = (timeout_ms or self._timeout_ms) / 1000.0
        retry_config = self._normalize_retry_config(retry, self._retry)
        descriptor = RequestDescriptor(method=method, url=url, body=self._prepare_debug_body(body))

        for attempt in range(1, retry_config.max_attempts + 1):
            try:
                response = self._perform_request(
                    url,
                    method=method,
                    headers=merged_headers,
                    params=params,
                    body=body,
                    timeout=timeout,
                )
            except RequestException as exc:
                if attempt < retry_config.max_attempts and self._is_retryable_network_error(exc):
                    self._delay_with_backoff(attempt, retry_config)
                    continue

                raise WorkflowAPIError(
                    message=str(exc) or "Request failed without a message",
                    status=0,
                    status_text="NETWORK_ERROR",
                    headers={},
                    data=None,
                    request=descriptor,
                    cause=exc,
                ) from exc

            if 200 <= response.status_code < 300:
                return self._parse_success_response(response, descriptor)

            error = self._to_workflow_error(response, descriptor)
            if (
                attempt < retry_config.max_attempts
                and response.status_code in retry_config.retry_on_statuses
            ):
                self._delay_with_backoff(attempt, retry_config)
                continue

            raise error

        # Should not be reachable because the loop either returned or raised
        raise WorkflowAPIError(
            message="Exceeded maximum retry attempts",
            status=0,
            status_text="RETRY_EXHAUSTED",
            headers={},
            data=None,
            request=descriptor,
        )

    def _perform_request(
        self,
        url: str,
        *,
        method: str,
        headers: Mapping[str, str],
        params: Mapping[str, Any] | None,
        body: Any | None,
        timeout: float,
    ) -> Response:
        request_kwargs: dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers,
            "params": params,
            "timeout": timeout,
        }

        if body is not None:
            if isinstance(body, (bytes, bytearray)):
                request_kwargs["data"] = body
            elif isinstance(body, str):
                request_kwargs["data"] = body
            else:
                request_kwargs["json"] = body

        return self._session.request(**request_kwargs)

    def _merge_headers(
        self, headers: Mapping[str, str] | Headers | None, body: Any | None
    ) -> dict[str, str]:
        merged: dict[str, str] = dict(self._default_headers)

        if headers:
            for key, value in headers.items():
                merged[key] = value

        if body is not None:
            has_content_type = any(key.lower() == "content-type" for key in merged)
            if not has_content_type and not isinstance(body, (bytes, bytearray, str)):
                merged.setdefault("Content-Type", "application/json")

        return merged

    def _resolve_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"{self._base_url}{path}"

    def _normalize_retry_config(
        self,
        retry: WorkflowClientRetryConfig | None,
        fallback: ResolvedRetryConfig | None = None,
    ) -> ResolvedRetryConfig:
        base = fallback or ResolvedRetryConfig(
            max_attempts=3,
            initial_delay_ms=1_000,
            backoff_factor=2.0,
            max_delay_ms=30_000,
            retry_on_statuses=tuple(DEFAULT_RETRYABLE_STATUSES + list(range(500, 600))),
        )

        if retry is None:
            return base

        max_attempts = max(int(retry.get("max_attempts", base.max_attempts)), 1)
        initial_delay_ms = int(retry.get("initial_delay_ms", base.initial_delay_ms))
        backoff_factor = float(retry.get("backoff_factor", base.backoff_factor))
        max_delay_ms = int(retry.get("max_delay_ms", base.max_delay_ms))
        retry_statuses: Sequence[int] | None = retry.get("retry_on_statuses")

        if retry_statuses:
            retry_on_statuses = tuple(int(code) for code in retry_statuses)
        else:
            retry_on_statuses = base.retry_on_statuses

        return ResolvedRetryConfig(
            max_attempts=max_attempts,
            initial_delay_ms=initial_delay_ms,
            backoff_factor=backoff_factor,
            max_delay_ms=max_delay_ms,
            retry_on_statuses=retry_on_statuses,
        )

    def _parse_success_response(self, response: Response, request: RequestDescriptor) -> Any:
        if response.status_code == 204:
            return None

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response.text

        try:
            return response.json()
        except ValueError as exc:
            raise WorkflowAPIError(
                message="Failed to parse JSON response",
                status=response.status_code,
                status_text=response.reason or "",
                headers=dict(response.headers),
                data=None,
                request=request,
                cause=exc,
            ) from exc

    def _to_workflow_error(self, response: Response, request: RequestDescriptor) -> WorkflowAPIError:
        data = self._parse_error_body(response)
        message = self._build_error_message(response, data)
        return WorkflowAPIError(
            message=message,
            status=response.status_code,
            status_text=response.reason or "",
            headers=dict(response.headers),
            data=data,
            request=request,
        )

    def _parse_error_body(self, response: Response) -> Any:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError as exc:
                return {"parseError": str(exc)}
        try:
            text = response.text
        except RequestException as exc:  # pragma: no cover - defensive
            return {"readError": str(exc)}
        return text or None

    @staticmethod
    def _build_error_message(response: Response, data: Any) -> str:
        if isinstance(data, str) and data:
            return f"{response.status_code} {response.reason}: {data}"

        if isinstance(data, MutableMapping):
            message = data.get("message") or data.get("error")
            if isinstance(message, str) and message:
                return f"{response.status_code} {response.reason}: {message}"

        return f"{response.status_code} {response.reason}"

    def _delay_with_backoff(self, attempt: int, retry: ResolvedRetryConfig) -> None:
        exponent = max(0, attempt - 1)
        delay_ms = min(
            retry.initial_delay_ms * (retry.backoff_factor ** exponent),
            retry.max_delay_ms,
        )
        time.sleep(delay_ms / 1000.0)

    @staticmethod
    def _is_retryable_network_error(error: RequestException) -> bool:
        retryable_messages = (
            "ECONNRESET",
            "ENOTFOUND",
            "EAI_AGAIN",
            "ETIMEDOUT",
            "SOCKET HANG UP",
        )
        message = str(error).upper()
        return any(token in message for token in retryable_messages)

    @staticmethod
    def _prepare_debug_body(body: Any | None) -> Any | None:
        if body is None:
            return None

        if isinstance(body, (str, bytes, bytearray, int, float, bool)):
            return body

        try:
            return json.loads(json.dumps(body))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _build_default_headers(
        api_key: str,
        overrides: Mapping[str, str] | None,
        user_agent_suffix: str | None,
    ) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": HttpClient._build_user_agent(user_agent_suffix),
            "x-api-key": api_key,
        }
        if overrides:
            headers.update(overrides)
        return headers

    @staticmethod
    def _build_user_agent(user_agent_suffix: str | None) -> str:
        base = f"syncteams-sdk/{__version__}"
        if not user_agent_suffix:
            return base
        return f"{base} {user_agent_suffix}".strip()
