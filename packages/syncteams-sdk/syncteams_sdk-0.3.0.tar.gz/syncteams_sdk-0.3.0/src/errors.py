"""Custom exceptions raised by the SyncTeams Python SDK."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional, Union

from .types import Headers, RequestDescriptor

ErrorResponseData = Union[Mapping[str, Any], str, None]


@dataclass
class WorkflowAPIErrorRequest:
    method: str
    url: str
    body: Optional[Any] = None


class WorkflowAPIError(Exception):
    """Raised when the SyncTeams API returns an error response."""

    def __init__(
        self,
        *,
        message: str,
        status: int,
        status_text: str,
        headers: Mapping[str, str] | Headers,
        data: ErrorResponseData,
        request: RequestDescriptor,
        cause: Exception | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.status_text = status_text
        self.headers = dict(headers)
        self.data = data
        self.request = request
        self.cause = cause

    def __repr__(self) -> str:  # pragma: no cover - repr convenience
        return (
            f"WorkflowAPIError(status={self.status!r}, message={self.args[0]!r}, "
            f"url={self.request.url!r})"
        )


def is_workflow_api_error(error: Exception) -> bool:
    """Return ``True`` if *error* is a :class:`WorkflowAPIError`."""

    return isinstance(error, WorkflowAPIError)


def normalize_headers(headers: Mapping[str, str] | Headers | None) -> Dict[str, str]:
    if headers is None:
        return {}

    if isinstance(headers, MutableMapping):
        return dict(headers)

    return {key: value for key, value in headers.items()}
