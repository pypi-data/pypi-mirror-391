# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-10

### Added
- Converted Literal types to Enums for better type safety and developer experience
- Added `WorkflowStatus` enum with values: QUEUED, PENDING, RUNNING, WAITING, CANCELED, FAILED, COMPLETED
- Added `ApprovalDecision` enum with values: APPROVE, REJECT
- Added `WorkflowEventType` enum with all workflow event types
- Updated documentation with enum usage examples

### Changed
- `WorkflowStatus`, `ApprovalDecision`, and `WorkflowEventType` are now exported as enums (inheriting from `str` and `Enum`)
- All internal code updated to use enum values for consistency
- Maintains backward compatibility - string values still work alongside enums

## [0.2.0] - 2025-10-28

### Added
- Initial Python SDK release
- `WorkflowClient` with full API support
- `execute_workflow`, `get_task_status`, `continue_task` methods
- `wait_for_completion` with polling and callbacks
- `execute_and_wait` convenience method with approval handling
- Automatic retry with exponential backoff
- Type hints and comprehensive error handling
- Unit tests with pytest

### Features
- Full parity with JavaScript SDK
- Python 3.9+ support
- Async-friendly polling with stop events
- Webhook event type definitions
- Detailed error responses with `WorkflowAPIError`
