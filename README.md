# OneTapGOV Backend

Production-oriented FastAPI backend for discovering and preparing government scheme
applications. The central invariant is:

> AI understands. Rules decide. The database verifies.

AI extraction only converts natural language into validated candidate facts. Eligibility
is evaluated by a deterministic, database-versioned JSON rule engine and every decision
stores its profile snapshot, rule versions, explanation, and ruleset fingerprint.

## Architecture

```text
app/
  api/v1/routes/       HTTP validation and service calls only
  core/                settings, database, security, cache, logging, errors
  dependencies/        authentication and RBAC
  engines/             rule, recommendation, readiness, action-plan algorithms
  middleware/          trace IDs, Redis rate limits, security headers
  models/              normalized SQLAlchemy models
  repositories/        persistence boundaries
  schemas/             Pydantic v2 contracts
  services/            application use cases
  workers/             Celery application and tasks
migrations/            Alembic migrations
scripts/               idempotent seed tooling
tests/                 unit, service, and API integration tests
deploy/                production database bootstrap guidance
```

## Run Locally

Python 3.12 is required.

```powershell
cd backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
docker compose up -d postgres redis
alembic upgrade head
python -m scripts.seed --admin-email admin@example.gov --admin-password "replace-this-password"
uvicorn app.main:app --reload
```

## Enabling Providers

OpenAI / Gemini
- Set `AI_PROVIDER=openai` and `OPENAI_API_KEY=<your-key>` in `.env`.
- The `AIExtractionService` will automatically attempt to use an OpenAI-compatible client if `AI_PROVIDER` is set; otherwise it falls back to a local structured extractor.

Supabase Storage
- Set `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` in `.env`.
- Files uploaded via `/api/v1/documents/upload` will be stored in the configured Supabase storage `documents` bucket when those values are provided. If not configured, uploads are stored in a local temp directory.

AWS S3
- Optionally configure `AWS_S3_BUCKET`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION`.
- If Supabase is not configured and `AWS_S3_BUCKET` is present, uploads will be sent to S3.

OCR
- The app supports pytesseract + Pillow for OCR. Install system Tesseract binary and Python packages `pytesseract` and `Pillow` to enable OCR.
- Set `TESSERACT_CMD` in `.env` if tesseract is not on PATH.

### GitHub Secrets for OCR and S3
- `TESSERACT_CMD`: (optional) path to tesseract binary for runners that don't have it on PATH.
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_BUCKET`: credentials and bucket name for S3 uploads in CI.
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`: Supabase storage credentials (add as secrets in GitHub).

CI notes
- To run OCR tests in CI, ensure `TESSERACT_CMD` points to a tesseract binary installed on the runner (or use an image that includes tesseract).
- To test S3 integration in CI using `moto`, add `moto` and `boto3` to your dev/test deps; the included `pytest` tests use `moto` and will run without real AWS creds.

Translation
- To enable translation of user input before extraction, set `AI_TRANSLATION_ENABLED=true` and configure a provider (e.g., `AI_TRANSLATION_PROVIDER=google`). The default is a no-op provider.


Swagger is available at `http://127.0.0.1:8000/docs`.

## Main APIs

- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout`
- `POST /api/v1/auth/supabase/exchange`
- `GET|PATCH /api/v1/profiles/me`
- `POST /api/v1/ai/extract`
- `GET /api/v1/schemes`
- `POST /api/v1/eligibility/evaluate/{scheme_id}`
- `POST|GET /api/v1/recommendations`
- `POST|GET /api/v1/documents`
- `GET /api/v1/documents/readiness/{scheme_id}`
- `POST /api/v1/action-plans/generate/{scheme_id}`
- `POST|GET /api/v1/notifications`
- `/api/v1/admin/*` for versioned scheme, rule, document, and audit management

All normal responses use `success`, `message`, `data`, `errors`, and `trace_id`.
Exceptions return the same envelope without exposing stack traces.

Supabase Auth exchange supports current ES256/RS256 signing keys through the
project JWKS endpoint. Shared-secret access tokens are verified through the Auth
server when a publishable key is configured, with local HS256 verification kept
only as a legacy fallback.

## Rule Format

Rules are validated JSON ASTs rather than executable expressions:

```json
{
  "all": [
    {"condition": {"field": "profile.annual_income", "operator": "lt", "value": 200000}},
    {"condition": {"field": "profile.state", "operator": "eq", "value": "Maharashtra"}},
    {"condition": {"field": "education.is_student", "operator": "eq", "value": true}}
  ]
}
```

Supported operators are `eq`, `ne`, `lt`, `lte`, `gt`, `gte`, `in`, `not_in`,
`contains`, `exists`, and `truthy`. No dynamic Python or SQL is evaluated.

## Tests

```powershell
pytest
```

Coverage is configured to fail below 80%. See `DEPLOYMENT.md` for the Supabase,
container rollout, observability, backup, and secret-management checklist.

## Running tests locally without coverage enforcement

During development you may want to run a single test file or a subset of tests
without triggering the coverage failure configured in `pyproject.toml`.

From the `backend` directory you can use one of the helper scripts:

PowerShell (Windows):
```powershell
.\scripts\run_tests_no_cov.ps1 tests\test_workers.py
```

Bash / macOS / WSL:
```bash
./scripts/run_tests_no_cov.sh tests/test_workers.py
```

Python (cross-platform):
```bash
python scripts/run_tests_no_cov.py tests/test_workers.py
```

These helpers override the `addopts` pytest setting so coverage enforcement is skipped for fast local iterations.

## Convenience scripts (root)

Two convenience scripts are available at the repository root for starting the Celery stack and running maintenance tasks without changing directories.

- `run_celery_compose.ps1` / `run_celery_compose.sh` — start Redis + Celery worker + beat using `backend/docker-compose.celery.yml`.
- `run_maintenance.ps1` / `run_maintenance.sh` — run the maintenance task `refresh_recommendations_impl` using the backend virtualenv python when available.

Example (PowerShell):
```powershell
# start celery services (in background via docker-compose)
.\run_celery_compose.ps1

# run the maintenance task synchronously
.\run_maintenance.ps1
```

Example (Bash):
```bash
./run_celery_compose.sh
./run_maintenance.sh
```

## Periodic recompute of recommendations

The Celery beat schedule includes two maintenance jobs:

- `workers.refresh_recommendations` — invalidates `recommendations:*` cache every 10 minutes.
- `workers.recompute_recommendations` — naive full recompute of recommendations for all active users (daily).

Notes:
- The full recompute task is intentionally simple — in production, you should shard work across workers, run in parallel batches, and add rate-limiting and monitoring.
- To invoke the recompute task manually (synchronously):

PowerShell:
```powershell
& ".\.venv\Scripts\python.exe" -c "from app.workers.recompute_recommendations import recompute_recommendations_impl; import json; print(json.dumps(recompute_recommendations_impl()))"
```


## Systemd unit examples

There are example systemd unit files under `deploy/systemd/` you can adapt for production:

- `deploy/systemd/celery-worker.service`
- `deploy/systemd/celery-beat.service`

These files assume the backend is deployed to `/srv/onetapgov/backend` and a Python virtualenv exists at `/srv/onetapgov/backend/.venv`. Update `WorkingDirectory`, `ExecStart`, and environment variables to match your environment.
