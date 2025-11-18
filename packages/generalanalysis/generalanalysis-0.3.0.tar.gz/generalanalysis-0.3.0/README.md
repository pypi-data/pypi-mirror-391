# General Analysis SDK

Python SDK for General Analysis AI Guardrails.

## Installation

```bash
pip install generalanalysis
```

## Quick Start

```python
import generalanalysis

# Uses GA_API_KEY env var by default
client = generalanalysis.Client()

# Check text against guard policies
result = client.guards.invoke(text="Text to check", guard_name="@pii_guard")

if result.block:
    print("Blocked:", [p.name for p in result.policies if not p.passed])

# Optional: scope requests to a specific project (env var or kwarg)
# export GA_PROJECT_ID=123
# client = generalanalysis.Client()
# result = client.guards.invoke(text="...", guard_name="@pii_guard", project_id=456)
```

## API Reference

### Guards Operations

```python
# List guards
guards = client.guards.list()

# Invoke guard
result = client.guards.invoke(text="...", guard_name="@pii_guard")
print(f"Blocked: {result.block}, Latency: {result.latency_ms}ms")

# Build inline configurations when you want to tweak policies without saving them first
from generalanalysis import GuardConfigurationBuilder

builder = GuardConfigurationBuilder()
builder.add_policy(
    guard_name="@pii_guard",
    policy_id=10,
    policy_name="EMAIL_ADDRESS",
    sensitivity=0.4,
)
result = client.guards.invoke(text="Reach me at foo@example.com", configuration=builder)

# Get logs (paginated)
logs = client.guards.list_logs(guard_name="@pii_guard", page=1, page_size=50)

# Inspect available guard policies
policies = client.guards.list_policies()
for policy in policies:
    print(policy.name, policy.definition)

# List saved guard configurations (requires project scope)
configs = client.guard_configurations.list(project_id=123)
print([cfg.name for cfg in configs])
```

## Async Support

```python
import asyncio
import generalanalysis

async def main():
    async with generalanalysis.AsyncClient() as client:
        results = await asyncio.gather(*[
            client.guards.invoke(text=t, guard_name="@pii_guard") 
            for t in texts
        ])
```
