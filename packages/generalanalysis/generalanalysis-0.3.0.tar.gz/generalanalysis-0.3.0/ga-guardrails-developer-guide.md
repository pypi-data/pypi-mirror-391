# GeneralAnalysis Guardrails SDK - Developer Guide

## Quick Start

```python
import generalanalysis

# Initialize client (uses GA_API_KEY environment variable)
client = generalanalysis.Client()

# Invoke a guardrail by name, id, configuration id, or inline configuration
result = client.guards.invoke(text="Contact john@example.com", guard_name="@pii_guard")
first_guard = client.guards.list()[0]
result_by_id = client.guards.invoke(text="Contact john@example.com", guard_id=first_guard.id)
saved_config = client.guard_configurations.list()[0]
result_with_saved_config = client.guards.invoke(text="Contact john@example.com", configuration_id=saved_config.id)
result_with_inline_config = client.guards.invoke(
    text="Contact john@example.com",
    configuration=generalanalysis.GuardConfigurationBuilder().add_policy(
        guard_name="@pii_guard",
        policy_id=10,
        policy_name="EMAIL_ADDRESS",
    ),
)

# You can use either use result.block for binary decisions or policy.violation_prob for your own tunable threshold-based filtering
if result.block:
    print("Content blocked!")
    for policy in result.policies:
        if not policy.passed:
            print(f"  Violated: {policy.name} - {policy.definition}")
            print(f"  Confidence: {policy.violation_prob:.2%}")
```

### Guard Invocation Selectors

The Guards API accepts four mutually exclusive selectors. Provide exactly one when calling `guards.invoke`:

- `guard_name`: Human-friendly handle such as `"@pii_guard"`.
- `guard_id`: Numeric guard identifier returned by `guards.list()`.
- `configuration_id`: Identifier of a saved guard configuration returned by `guard_configurations.list()`.
- `configuration`: Inline configuration payload, typically built via `GuardConfigurationBuilder`.

Each selector accepts the same `text` payload and optional `project_id` overrides, enabling you to switch between ad-hoc experimentation (inline configs) and production-grade saved configurations without changing client code.

## Installation & Setup

```bash
# Install the SDK
pip install generalanalysis

# Set your API key
export GA_API_KEY="your_api_key_here"
```

### Project Scoping
Most guardrails endpoints require a project context. Provide it once via either:

- `GA_PROJECT_ID` environment variable (preferred for server environments)
- `project_id` constructor argument (`generalanalysis.Client(project_id=123)`)
- Per-call overrides (e.g., `client.guards.invoke(..., project_id=456)`)

The SDK automatically merges these sources so each request includes the correct scope when required by the Guardrails service.

## Available Guardrails

Guard availability is now project-scoped. Instead of relying on hard-coded IDs, always enumerate guards and policies dynamically:

```python
guards = client.guards.list(project_id=PROJECT_ID)
for guard in guards:
    print(guard.name, len(guard.policies))
```

To inspect reusable policies (including definitions, examples, and usage counts) call:

```python
policies = client.guards.list_policies(project_id=PROJECT_ID)
for policy in policies:
    print(policy.name, policy.definition, policy.guard_count)
```

Saved guard configurations can be inspected with:

```python
configs = client.guard_configurations.list(project_id=PROJECT_ID)
print([cfg.name for cfg in configs])
```

This workflow ensures the SDK always mirrors the latest server state, regardless of environment (dev/prod) or project membership.

## Core Operations

### List Available Guards
```python
guards = client.guards.list(project_id: Optional[int] = None) -> List[Guard]
```
Returns a list of all accessible guards (including policy details) for the scoped project.

### Invoke a Guard
```python
result = client.guards.invoke(
    text: str,
    guard_id: Optional[int] = None,
    guard_name: Optional[str] = None,
    configuration_id: Optional[int] = None,
    configuration: Optional[GuardConfigurationConfig] = None,
    project_id: Optional[int] = None,
) -> GuardInvokeResult
```
Checks the provided text against the guard's policies and returns violation results. Exactly one of `guard_id`, `guard_name`, `configuration_id`, or `configuration` must be supplied per call.

```python
# Guard name
client.guards.invoke(text="...", guard_name="@pii_guard")

# Guard id
client.guards.invoke(text="...", guard_id=guard.id)

# Saved configuration
client.guards.invoke(text="...", configuration_id=config.id)

# Inline configuration
client.guards.invoke(text="...", configuration=builder)
```

You can build inline configurations without manually crafting dictionaries by using the helper:

```python
from generalanalysis.types import GuardConfigurationBuilder

builder = GuardConfigurationBuilder()
builder.add_policy(
    guard_name="@pii_guard",
    policy_id=10,
    policy_name="EMAIL_ADDRESS",
    sensitivity=0.5,
)

result = client.guards.invoke(
    text="Reach me at foo@example.com",
    configuration=builder,
    project_id=123,
)
```

### List Guard Policies
```python
policies = client.guards.list_policies(project_id: Optional[int] = None) -> List[GuardPolicyDetail]
```
Use this to enumerate reusable policy definitions, examples, and which guards currently include them.

### List Guard Configurations
```python
configs = client.guard_configurations.list(project_id: Optional[int] = None) -> List[GuardConfigurationRecord]
```
Returns stored guard configurations (name + full config payload) for the active project scope.

### View Invocation Logs
```python
logs = client.guards.list_logs(
    guard_name: Optional[str] = None,  # Filter by guard name
    project_id: Optional[int] = None,
    page: int = 1,                   # Page number
    page_size: int = 50              # Items per page (max 100)
) -> PaginatedLogsResponse
```
Returns paginated logs of guard invocations. Each log entry contains:
- `id`: Log entry ID
- `project_id`: Project scope for the invocation
- `guard_id`: Guard that was invoked
- `guard_name`: Guard name snapshot recorded for the log
- `input_text`: Text that was evaluated
- `result`: GuardInvokeResult containing block status, latency, policies, and raw data
- `created_at`: Timestamp

### List Projects
```python
projects = client.projects.list(organization_id: Optional[int] = None) -> List[ProjectSummary]
```
Returns the projects the authenticated user can access. Pass an `organization_id` when you want to scope the results to a single workspace; omit it to retrieve every accessible project. Use this helper to discover valid `project_id` values for guard invocations.

```python
orgs = client.organizations.list()
default_org_id = orgs[0].id if orgs else None
projects = client.projects.list(organization_id=default_org_id)
for project in projects:
    print(project.id, project.name)
```

### List Organizations
```python
organizations = client.organizations.list() -> List[OrganizationSummary]
```
Lists every organization returned by `/auth/me` for the current API key. Each summary includes the organization id, name, and flags indicating whether it is personal or administered by the caller.

## Data Types

```python
from typing import Any, Dict, List, Optional
from datetime import datetime

class Guard:
    id: int
    name: str
    description: Optional[str]
    hf_id: Optional[str]
    endpoint: str
    system_prompt: Optional[str]
    policies: List[GuardPolicy]

class GuardPolicy:
    id: int
    name: str
    definition: str

class GuardInvokeResult:
    block: bool                       # Whether content should be blocked
    latency_ms: float                 # Processing time in milliseconds
    policies: List[PolicyEvaluation]  # Individual policy results
    raw: Dict[str, Any]              # Raw response data from the guard

class PolicyEvaluation:
    name: str                    # Policy identifier (e.g., "EMAIL_ADDRESS")
    definition: str              # Policy description
    passed: bool                 # True if policy check passed (no violation)
    violation_prob: float        # Probability/confidence score (0.0-1.0) of violation

class GuardLog:
    id: int
    project_id: int
    guard_id: int
    guard_name: str
    input_text: str
    created_at: str
    result: GuardInvokeResult | Dict[str, Any]  # Evaluation result (GuardInvokeResult for success, dict with error for failures)

class PaginatedLogsResponse:
    items: List[GuardLog]
    total: int
    page: int
    page_size: int
    total_pages: int
```

## Async Support

The SDK provides async versions of all methods with identical signatures and return types:

```python
async with generalanalysis.AsyncClient() as client:
    guards = await client.guards.list() -> List[Guard]
    result = await client.guards.invoke(text: str, guard_name: str) -> GuardInvokeResult
    logs = await client.guards.list_logs(...) -> PaginatedLogsResponse
```

## Error Handling

```python
from generalanalysis import (
    GuardNotFoundError,
    AuthenticationError,
    GeneralAnalysisError
)

try:
    result = client.guards.invoke(text="test", guard_name="@missing_guard")
except GuardNotFoundError as e:
    print(f"Invalid guard selector: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except GeneralAnalysisError as e:
    print(f"API error: {e}")
```

## API Reference

**Authentication**: Bearer token via `GA_API_KEY` environment variable

### Methods

| Method | Parameters | Return Type | Description |
|--------|-----------|-------------|-------------|
| `guards.list()` | `project_id: Optional[int] = None` | `List[Guard]` | List accessible guards for the scoped project |
| `guards.invoke()` | `text: str`<br>`guard_id: Optional[int]`<br>`guard_name: Optional[str]`<br>`configuration_id: Optional[int]`<br>`configuration: Optional[GuardConfigurationConfig]`<br>`project_id: Optional[int]` | `GuardInvokeResult` | Check text against a guard or guard configuration via exactly one selector |
| `guards.list_policies()` | `project_id: Optional[int] = None` | `List[GuardPolicyDetail]` | Inspect guard policies (definitions, examples, usage counts) |
| `guards.list_logs()` | `guard_name: Optional[str]`<br>`project_id: Optional[int]`<br>`page: int = 1`<br>`page_size: int = 50` | `PaginatedLogsResponse` | View invocation history |
| `guard_configurations.list()` | `project_id: Optional[int] = None` | `List[GuardConfigurationRecord]` | Enumerate saved guard configurations for the project |
| `projects.list()` | `organization_id: Optional[int] = None` | `List[ProjectSummary]` | Discover projects available in an organization or across all organizations |
| `organizations.list()` | *(none)* | `List[OrganizationSummary]` | List organizations tied to the authenticated user |

### Utility Methods

All response objects support:
- `.to_dict()` - Convert to dictionary
- `.to_json(indent=2)` - Convert to formatted JSON string

---
*SDK Version: generalanalysis 0.3.0 | Documentation Date: 2025*
