# Production Deployment

## Topology

- Run the API and Celery workers as separate, stateless services.
- Use Supabase's transaction pooler endpoint for `DATABASE_URL`.
- Use a managed Redis deployment with persistence, TLS, authentication, and eviction alerts.
- Run `alembic upgrade head` once as a release job before rolling out application instances.
- Keep API, migration, and Supabase Auth secrets in a managed secret store.

## Supabase

1. Create the project and copy the pooled PostgreSQL connection string.
2. Set `DATABASE_URL` to the `postgresql+asyncpg://` transaction-pooler URL.
3. Run migrations with a database-owner credential.
4. Create a restricted runtime role using `deploy/supabase.sql`.
5. Configure `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, audience, and issuer.
   Asymmetric ES256/RS256 tokens are verified locally from the project's cached
   JWKS endpoint. `SUPABASE_JWT_SECRET` is only a legacy HS256 fallback.
6. Rotate the database password, JWT secret, and application `SECRET_KEY` on a schedule.

Supabase's pooler should be used for horizontally scaled API and worker instances. Keep
SQLAlchemy's per-process pool conservative so aggregate connections remain below the
project limit.

## Release

```bash
docker build -t registry.example.gov/onetapgov-api:$GIT_SHA .
docker push registry.example.gov/onetapgov-api:$GIT_SHA
alembic upgrade head
```

Deploy immutable images, require HTTPS at the load balancer, and configure health checks
against `/health`. Start with two API replicas and two workers across failure domains.

## Operations

- Export JSON logs to a centralized log platform and alert on `unhandled_exception`,
  authentication spikes, refresh-token reuse, and notification failures.
- Monitor PostgreSQL connection count, slow queries, lock waits, cache hit rate, Celery
  queue depth, task retries, API latency percentiles, and HTTP 5xx rates.
- Back up PostgreSQL with point-in-time recovery and test restoration quarterly.
- Apply retention policies to audit, AI usage, eligibility decision, and notification logs.
- Never log JWTs, passwords, document storage URLs, or raw identity documents.
- Put document objects in private storage and issue short-lived signed URLs at the edge.
