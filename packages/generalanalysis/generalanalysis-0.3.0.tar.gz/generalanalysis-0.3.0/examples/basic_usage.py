"""Basic usage examples for the General Analysis SDK."""

import asyncio
import os

import generalanalysis


def sync_example() -> None:
    """Basic synchronous usage example."""
    print("=== Synchronous Example ===\n")

    client = generalanalysis.Client()

    guards = client.guards.list()
    for guard in guards:
        print(f"Guard[{guard.id}]: {guard.name}")

    if guards:
        guard = guards[0]
        result = client.guards.invoke(text="Hello world", guard_name=guard.name)
        print(f"Invoked by name, block={result.block}")

        result_by_id = client.guards.invoke(text="Hello world", guard_id=guard.id)
        print(f"Invoked by id, block={result_by_id.block}")

        result_dict = result.to_dict()
        print(f"Result as dict: {result_dict}")

        result_json = result.to_json(indent=2)
        print(f"Result as JSON:\n{result_json}")

        if guard.policies:
            print("\n--- Inline configuration example ---")
            first_policy = guard.policies[0]
            builder = generalanalysis.GuardConfigurationBuilder()
            builder.add_policy(
                guard_name=guard.name,
                policy_id=first_policy.id,
                policy_name=first_policy.name,
                policy_definition=first_policy.definition,
                sensitivity=0.9,
            )
            inline_result = client.guards.invoke(
                text="Reach me at inline@example.com",
                configuration=builder,
            )
            print(f"Inline configuration blocked? {inline_result.block}")

    policies = client.guards.list_policies()
    print(f"\nDiscovered {len(policies)} policies")
    for policy in policies[:3]:
        print(f"- {policy.name}: {policy.definition}")

    configs = client.guard_configurations.list()
    print(f"\nSaved configs: {[cfg.name for cfg in configs]}")
    if configs:
        config = configs[0]
        config_result = client.guards.invoke(
            text="Reach me at saved-config@example.com",
            configuration_id=config.id,
        )
        print(f"Saved configuration blocked? {config_result.block}")

    organizations = client.organizations.list()
    print(f"\nOrganizations: {[org.name for org in organizations]}")

    if organizations:
        projects = client.projects.list(organization_id=organizations[0].id)
    else:
        projects = client.projects.list()

    print(f"Projects: {[project.name for project in projects]}")


async def async_example() -> None:
    """Basic asynchronous usage example."""
    print("\n=== Asynchronous Example ===\n")

    async with generalanalysis.AsyncClient() as client:
        guards = await client.guards.list()

        if guards:
            guard = guards[0]
            result = await client.guards.invoke(text="Hello world", guard_name=guard.name)

            result_json = result.to_json(indent=2)
            print(f"Async result (JSON):\n{result_json}")


def logs_example() -> None:
    """Example of viewing guard invocation logs."""
    print("\n=== Guard Logs Example ===\n")

    client = generalanalysis.Client()
    logs = client.guards.list_logs(page=1, page_size=1)

    if logs.items:
        log_json = logs.to_json(indent=2)
        print(log_json)


def main() -> None:
    """Run examples."""
    if not os.environ.get("GA_API_KEY"):
        print("Warning: No API key found. Set GA_API_KEY.")
        return

    try:
        sync_example()
        asyncio.run(async_example())
        logs_example()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
