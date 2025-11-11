# SyncTeams Workflow SDK (Python)

A Python client for the SyncTeams Workflow API. Mirrors the capabilities of the JavaScript SDK, offering convenient helpers to execute workflows, monitor task status, and manage approval flows.

---

## Installation

```bash
pip install syncteams-sdk
```

**Requirements:** Python 3.9 or newer

---

## Quick Start

```python
from syncteams_sdk import WorkflowClient, WorkflowStatus

client = WorkflowClient(api_key="YOUR_API_KEY")

# Execute a workflow
result = client.execute_workflow(
    workflow_id="your_workflow_id",
    input={"email": "user@example.com"},
    unique_id="customer-123",
)

task_id = result["taskId"]

# Wait for completion
final_status = client.wait_for_completion(
    task_id,
    poll_interval_ms=2_000,
    on_update=lambda status: print(f"Status: {status['status']}")
)

if final_status["status"] == WorkflowStatus.COMPLETED:
    print("Workflow completed successfully!")
```

---

## Configuration

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `api_key` | ✅ | – | Your SyncTeams API key |
| `base_url` | ❌ | `https://develop.api.syncteams.studio` | API base URL |
| `timeout_ms` | ❌ | `30000` | Request timeout in milliseconds |
| `retry` | ❌ | See below | Retry configuration for failed requests |
| `default_headers` | ❌ | `{}` | Extra headers merged into every request |
| `user_agent_suffix` | ❌ | – | Extra token appended to the default User-Agent |

### Retry Configuration

By default, the SDK retries transient failures with exponential backoff:
- Maximum attempts: 3
- Initial delay: 1 second
- Backoff factor: 2x
- Maximum delay: 30 seconds
- Retries on: 408, 425, 429, and all 5xx responses

You can override any subset of these values when constructing the client.

---

## API overview

### `execute_workflow(workflow_id, input, unique_id=None)`

Starts a workflow execution.

```python
response = client.execute_workflow(
    workflow_id="your_workflow_id",
    input={"customer_id": "cust-123"},
)

print(response["taskId"], response["status"])
```

Returns the `taskId` and initial status.

### `get_task_status(task_id)`

Fetches the latest status and the filtered event log for a task.

```python
status = client.get_task_status(task_id)
print(status["status"], len(status.get("eventLogs", [])))
```

### `continue_task(task_id, decision, message=None)`

Resumes a waiting workflow after an approval decision.

```python
from syncteams_sdk import ApprovalDecision

client.continue_task(task_id=task_id, decision=ApprovalDecision.APPROVE)

client.continue_task(
    task_id=task_id,
    decision=ApprovalDecision.REJECT,
    message="Missing documentation",
)
```

When `decision` is `ApprovalDecision.REJECT`, `message` is required.

### `wait_for_completion(task_id, *, poll_interval_ms=2000, max_wait_time_ms=600000, on_update=None, exit_on_waiting=False, terminal_statuses=None, stop_event=None)`

Polls a task until it reaches a terminal status (`COMPLETED`, `FAILED`, or `CANCELED`).

```python
final_status = client.wait_for_completion(
    task_id,
    poll_interval_ms=1000,
    on_update=lambda payload: print("Status:", payload["status"]),
)
```

### `execute_and_wait(workflow_id, input, **options)`

Convenience method that starts a workflow and optionally handles approvals via `on_waiting`.

```python
from syncteams_sdk import ApprovalDecision

def handle_waiting(status):
    # Perform approval logic
    client.continue_task(task_id=status["taskId"], decision=ApprovalDecision.APPROVE)
    return True

result = client.execute_and_wait(
    workflow_id="wf-123",
    input={"amount": 500},
    on_waiting=handle_waiting,
)
```

If `on_waiting` returns `False`, polling stops and the SDK returns the current status (even if still waiting).

---

## Error Handling

The SDK raises `WorkflowAPIError` for API failures. It exposes the HTTP status, headers, response payload, and request metadata to simplify debugging.

```python
from syncteams_sdk import WorkflowAPIError

try:
    client.execute_workflow(workflow_id="invalid", input={})
except WorkflowAPIError as error:
    print("API error:", error.status, error.data)
```

Transient errors (timeouts, rate limits, server errors) are automatically retried according to the configured policy.

---

## Webhooks

You can receive workflow updates via webhooks instead of polling:

```python
from flask import Flask, request
from syncteams_sdk import WebhookEventPayload

app = Flask(__name__)

@app.post("/webhooks/syncteams")
def handle_webhook():
    payload: WebhookEventPayload = request.get_json(force=True)
    print("Task", payload["taskId"], "status:", payload["status"])
    return ("", 200)
```

---

## Type Safety with Enums

The SDK provides enums for better type safety and IDE autocomplete:

```python
from syncteams_sdk import WorkflowStatus, ApprovalDecision, WorkflowEventType

# Use enums for type-safe comparisons
if status["status"] == WorkflowStatus.COMPLETED:
    # Handle completion
    pass

# All available workflow statuses
WorkflowStatus.QUEUED
WorkflowStatus.PENDING
WorkflowStatus.RUNNING
WorkflowStatus.WAITING
WorkflowStatus.CANCELED
WorkflowStatus.FAILED
WorkflowStatus.COMPLETED

# Approval decisions
ApprovalDecision.APPROVE
ApprovalDecision.REJECT

# Enums work seamlessly with the API
client.continue_task(
    task_id=task_id,
    decision=ApprovalDecision.APPROVE  # Type-safe!
)
```

---

## Development

Install dependencies and run tests:

```bash
pip install -e .[dev]
pytest
```

---

## License

MIT
