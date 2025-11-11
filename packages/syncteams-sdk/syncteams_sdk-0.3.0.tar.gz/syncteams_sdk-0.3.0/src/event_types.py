"""Typed event payloads emitted by the SyncTeams Workflow API."""
from __future__ import annotations

from typing import Any, Dict, List, TypedDict
from typing_extensions import NotRequired


class ToolResult(TypedDict, total=False):
    result: str
    tool_name: str


class AgentExecutorConfig(TypedDict, total=False):
    tools_names: str
    max_iter: int
    use_stop_words: bool
    tools_description: str
    respect_context_window: bool
    ask_for_human_input: bool
    iterations: int
    log_error_after: int


class LlmConfig(TypedDict, total=False):
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    presence_penalty: float
    frequency_penalty: float
    api_key: str
    context_window_size: int
    is_anthropic: bool
    stream: bool


class EmbedderConfig(TypedDict, total=False):
    model: str
    api_key: str


class CrewUsageMetrics(TypedDict, total=False):
    total_tokens: int
    prompt_tokens: int
    cached_prompt_tokens: int
    completion_tokens: int
    successful_requests: int


class Tool(TypedDict, total=False):
    name: str
    description: str
    description_updated: bool
    result_as_answer: bool
    current_usage_count: int


class TaskContextItem(TypedDict, total=False):
    name: str
    prompt_context: str
    description: str
    used_tools: int
    tools_errors: int
    delegations: int
    expected_output: str
    async_execution: bool
    human_input: bool
    markdown: bool
    max_retries: int
    retry_count: int


class TaskOutput(TypedDict, total=False):
    description: str
    name: str
    expected_output: str
    summary: str
    json_dict: Dict[str, Any]
    raw: str
    agent: str
    output_format: str


class Agent(TypedDict, total=False):
    role: str
    goal: str
    backstory: str
    cache: bool
    verbose: bool
    allow_delegation: bool
    tools: List[Tool]
    max_iter: int
    agent_executor: AgentExecutorConfig
    llm: LlmConfig
    crew: "CrewConfig"
    tools_results: List[ToolResult]
    multimodal: bool
    reasoning: bool
    embedder: EmbedderConfig


class Task(TypedDict, total=False):
    name: str
    prompt_context: str
    description: str
    expected_output: str
    used_tools: int
    tools_errors: int
    delegations: int
    context: List[TaskContextItem]
    output: TaskOutput
    agent: Agent
    async_execution: bool
    tools: List[Tool]
    human_input: bool
    max_retries: int
    retry_count: int


class CrewConfig(TypedDict, total=False):
    name: str
    tasks: List[Task]
    agents: List[Agent]
    process: str
    verbose: bool
    memory: bool
    embedder: EmbedderConfig
    usage_metrics: CrewUsageMetrics
    planning: bool
    execution_logs: List[Any]
    knowledge_sources: List[Any]


class LlmCall(TypedDict, total=False):
    role: str
    content: str


class ExecutionInputs(TypedDict, total=False):
    message: str


class ExecutionEvent(TypedDict, total=False):
    message: str
    iteration: int
    feedback: str
    result: str
    prompt: str
    timestamp: str
    type: str
    agent: Agent
    tools: List[Tool]
    task: Task
    output: TaskOutput
    context: str
    crew_name: str
    inputs: ExecutionInputs
    task_name: str
    agent_role: str
    messages: List[LlmCall]
    error: str
    training_mode: bool
