# ga-sdk Agent Guide

Guidelines for contributors working inside the `ga-sdk` package (General Analysis Python SDK).

## Project Layout
- `generalanalysis/`: SDK source. Key modules:
  - `client.py`, `async_client.py`: sync/async entry points that wire up resources.
  - `core/`: shared plumbing (`auth.py`, `http_client.py`, `project.py`).
  - `resources/`: resource groupings (`guards.py`, `async_guards.py`, `guard_configurations.py`, etc.).
  - `types/`: Pydantic v2 models shared across the SDK (`guard_configs.py`, `guards.py`).
  - `__init__.py`: user-facing exports kept in sync with the public API.
- `tests/`: pytest suite that mocks the HTTP client to keep tests fast/offline.
- `examples/`, `README.md`, `ga-guardrails-developer-guide.md`: documentation that must stay aligned with the code surface.

## Development & Test Commands
- Install dev deps: `uv sync --group dev`
- Run unit tests: `uv run pytest`
- Format: `uv run black generalanalysis/`
- Lint: `uv run ruff check generalanalysis/`
- Type check: `uv run mypy generalanalysis/`
Run commands from the `ga-sdk/` folder. Tests rely on mocked clients—no network calls should be introduced.

## Coding Style & Conventions
- Follow PEP 8 with a 100-character line limit (enforced via Ruff/Black).
- Use explicit imports; avoid wildcard exports except in `generalanalysis/__init__.py`.
- All payload/response models must be defined with Pydantic v2 BaseModels and keep fields in lockstep with the Guardrails service schemas. Prefer `model_dump()` for serialization.
- Maintain symmetry between sync and async resources: every public method added in one must exist in the other and share argument names/behavior.
- Keep the SDK focused on *invoking* guard functionality. Do not add guard-creation or other admin endpoints here; those workflows live in higher-level apps.

## API Contract Notes
- Base URL defaults to the **dev** Guardrails API (`https://guardrails-api.generalanalysis.com`). Allow overrides via constructor args or `GA_BASE_URL` when needed.
- Guards:
  - Listing: `GET /guards`
  - Invocation: `POST /guards/invoke` (supports `guard`, `configuration_id`, or inline `configuration`; enforce “exactly one selector” rule in resources and types).
  - Logs: `GET /guards/logs`
- Guard policies now live under `GET /policies`—the legacy `/guards/policies` path is removed in the SDK. Update docs/tests whenever the server schema changes.
- Guard configurations: `GET /guard-configs` for reading saved configs. Creation/edit flows remain out of scope for now.
- Surface server errors via the typed exceptions in `generalanalysis.exceptions` (e.g., `GeneralAnalysisError`, `AuthenticationError`, `GuardNotFoundError`, `ProjectScopeError`, `OrganizationContextError`, `GuardInvocationError`, `QuotaExceededError`). Wrap 404s from guard invocations as `GuardNotFoundError` when a selector was provided.

## Documentation Expectations
- README, developer guide, and examples must mirror the public API. When changing method signatures or endpoints (e.g., policy routing), update docs in the same PR.
- `CLAUDE.md` should reflect the latest endpoint table so external agents don’t resurrect deprecated routes.

## Testing Guidance
- Add or update tests in `tests/test_guards.py` (and peers) whenever resource behavior changes.
- Tests should only assert interactions with the mocked HTTP client—no real HTTP calls or environment mutations.
- Keep fixtures simple; prefer inline helper functions (see `_sample_guard_response` etc.).

## Release Hygiene
- Update `generalanalysis/__version__.py` and `pyproject.toml` together when shipping a new version.
- Record user-visible changes in `CHANGELOG.md` before tagging.
- Re-run `uv run pytest` + `uv run ruff check` + `uv run mypy generalanalysis/` locally before publishing.
