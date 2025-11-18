## DPostBackend — Copilot Instructions

This file gives focused, actionable context for an AI coding assistant working on this repository.

**Big Picture**:
- **What:** A FastAPI backend that helps fork GitHub repos, push test-case JSON and a generated GitHub Actions workflow, then receive test results from those workflows.
- **Where:** Core logic lives under `app/` (`app/main.py`, `app/github_client.py`, `app/workflow_generator.py`, `app/test_case_storage.py`, `app/cache.py`).
- **Why:** Automate pushing API test cases + workflows into forks and collect CI-run test results back to this service.

**Key flows (quick)**:
- **Forking:** `POST /repos/fork` → `app.github_client.fork_repository` writes into DB cache (`app/cache.py`). See `app/main.py:create_fork`.
- **Submitting test case:** `POST /repos/test` accepts multipart JSON file → saves to `./data/test_cases/` using `app/test_case_storage.py`, returns immediately and schedules BackgroundTasks to push files.
- **Pushing & triggering:** Background task `_push_test_case_and_workflow` in `app/main.py` uses `app/github_client.create_or_update_file` and `trigger_workflow` and `app/workflow_generator.generate_workflow`.
- **Receiving results:** GitHub Actions call `POST /repos/test-results` to save results into `./data/test_results/`.

**Important files & responsibilities**:
- `app/main.py`: HTTP endpoints, background task orchestration, high-level validation.
- `app/github_client.py`: All GitHub REST interactions (fork, file content, create/update file, trigger workflow, merge-upstream). Use this module for API calls.
- `app/workflow_generator.py`: Produces `.github/workflows/api-test.yml` content per `tech_stack` (`springboot_maven`, `nodejs_express`, `python_flask`). Keep changes here to affect generated workflows.
- `app/test_case_storage.py`: Filename convention: `{owner}_{repo}_{org}.json` (org optional); files saved to `data/test_cases`.
- `app/cache.py` + `app/models.py` + `app/database.py`: SQLite default DB at `./data/cache.db` and ORM model `RepositoryCache` for caching fork responses.
- `test-runner.js`, `schema/jsonSchemaValidator.js`, `schema/schema.json`: files pushed to the fork on first push and used by workflows to run tests.

**Environment & run commands**:
- Required: `GITHUB_PAT` in `.env`. Without it, `app.github_client.get_github_pat()` raises.
- Optional: `BACKEND_API_URL`, `DATABASE_URL`, `LOG_LEVEL`.
- Start dev server: `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` (from README).
- Test PAT locally: `python scripts/test_pat.py` (reads `.env`).

**Project-specific conventions**:
- **Backgrounding:** GitHub pushes/triggers are done in FastAPI `BackgroundTasks` — endpoints return quickly and do not await GitHub operations.
- **File naming:** Test-case files and result files use the `{owner}_{repo}[_org]` pattern. Look in `app/test_case_storage.py` and `app/main.py` for examples.
- **Workflow detection:** Workflows are generated via `generate_workflow(...)`. The service compares existing workflow content (base64 from GitHub) and skips updates when identical.
- **Branches:** Default branch is taken from fork metadata (`default_branch`) but falls back to `main`.

**Debugging hints for agents**:
- If GitHub operations fail, inspect `app/github_client.py` for HTTP status handling and `httpx.HTTPStatusError` usage.
- To reproduce locally, ensure `.env` contains `GITHUB_PAT` and (optionally) `BACKEND_API_URL`; run `uvicorn` and use `scripts/update_workflow.py` or the API endpoints.
- Logs are controlled by `LOG_LEVEL` (see `app/logging_config.py`). Increase to `DEBUG` to see `httpx`/GitHub details.

**Examples to reference in code changes**:
- Add CORS origins in `app/main.py` (see `allow_origins` list).
- Update workflow templates in `app/workflow_generator.py` when adding a new tech stack.
- Persisting cache: use `app/cache.upsert_cached_response(...)` to write `RepositoryCache` entries.

If anything above is unclear or you'd like more detail for a specific task (tests, adding a new tech stack, or changing DB), tell me which area and I'll expand or update this doc.
