Recompute Recommendations CronJob

This document explains how to run the recompute recommendations task on Kubernetes.

1) Apply the CronJob (adjust image, secrets, schedule):

```bash
kubectl apply -f deploy/k8s/cronjobs/recompute-recommendations-cronjob.yaml
```

2) Running multiple shards

To run N shards in parallel, create N CronJobs (or N Jobs) each with a different shard index (0..N-1). Example command for a single job run:

```bash
kubectl create job --from=cronjob/recompute-recommendations recompute-shard-0-$(date +%s)
# or override args on the fly:
kubectl run --restart=OnFailure recompute-manual --image=your-registry/onetap-backend:latest -- /bin/sh -c "python -m app.workers.recompute_recommendations 0 4 50"
```

3) Environment and secrets

- `DATABASE_URL` (secret) - PostgreSQL connection string
- `REDIS_URL` (secret) - Redis connection string
- `PUSHGATEWAY_URL` (optional) - URL to Prometheus Pushgateway
- `SENTRY_DSN` (optional) - Sentry DSN for error reporting

4) Monitoring

- Prometheus: see `deploy/monitoring/prometheus-pushgateway-scrape.yaml` for an example scrape configuration for Pushgateway.
- Metrics: the recompute task will push a counter `recompute_users_processed_total` to Pushgateway when `PUSHGATEWAY_URL` is present.

5) Sentry

- Optional: set `SENTRY_DSN` via secret. The task will attempt to import `sentry-sdk` and capture exceptions if available.

6) Resource tuning

- Start with `requests: cpu=500m, memory=512Mi` and increase based on observed CPU/DB load.
- Tune `concurrency` and shard count to balance DB load and parallelism.

7) Troubleshooting

- Check job logs:

```bash
kubectl logs job/<job-name> -c recompute
```

- Check recent CronJob runs:

```bash
kubectl get cronjob recompute-recommendations -o yaml
kubectl get jobs --selector=job-name=recompute-recommendations
```

8) CI/CD (GitHub Actions) example

Add the workflow at `.github/workflows/deploy-recompute-cronjob.yml` (example included in repo). It builds and pushes a Docker image from `backend/` and applies the CronJob manifest.

Required repository secrets:

- `REGISTRY_HOST` (e.g. ghcr.io or registry.example.com)
- `REGISTRY_USERNAME`
- `REGISTRY_PASSWORD`
- `IMAGE_NAME` (e.g. myorg/onetap-backend)
- `KUBE_CONFIG_DATA` (base64-encoded kubeconfig)

Trigger manually via the Actions UI or push to `main`/`master`.
