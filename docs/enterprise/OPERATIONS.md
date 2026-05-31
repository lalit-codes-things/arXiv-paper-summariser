# V17 Production Operations

## Environments

| Environment | Purpose | Promotion gate |
| --- | --- | --- |
| `dev` | Fast integration and feature validation | Unit tests and static checks |
| `staging` | Production-like validation | Security scans, migration checks, smoke tests |
| `prod` | Enterprise workloads | Manual approval, signed artifacts, change ticket |

## Deployment workflow

1. Merge to `main` after peer review.
2. CI builds and scans the container image.
3. Terraform plans are generated for platform changes.
4. Staging receives automatic deployment.
5. Smoke tests validate SSO, tenant routing, health endpoints, and worker execution.
6. Production deployment requires approval and records a change event in the audit log.

## Runbooks

### API error budget burn

1. Check Grafana API overview dashboard.
2. Inspect Alertmanager annotations for route, tenant, and deployment revision.
3. Compare error rate by tenant to identify noisy-neighbor behavior.
4. Roll back with `scripts/deploy.sh rollback` if errors correlate with a new release.
5. Capture incident notes and attach dashboard snapshots to the evidence vault.

### Queue backlog

1. Review KEDA scaler metrics and queue depth.
2. Confirm workers can reach model providers and object storage.
3. Temporarily increase `worker.maxReplicas` in Helm values if saturation persists.
4. Apply tenant throttling when one tenant exceeds agreed limits.

### Audit delivery lag

1. Check `AuditLogDeliveryLagHigh` in Alertmanager.
2. Confirm log sink credentials and network egress.
3. Fail over to object-store audit buffering when SIEM ingestion is unavailable.
4. Reconcile buffered events and record evidence after recovery.

### Tenant isolation incident

1. Disable affected tenant ingress route.
2. Rotate tenant-specific secrets.
3. Export audit events for the incident window.
4. Validate NetworkPolicies and RBAC bindings.
5. Run post-incident access review.

## Backup and recovery

- PostgreSQL: continuous backups with point-in-time recovery and quarterly restore tests.
- Object storage: versioning, lifecycle rules, immutable retention for audit logs.
- Kubernetes: declarative recovery from Git, Helm, and Terraform state.
- Secrets: external secret store replication and break-glass process.

## SLO targets

| Service | Target |
| --- | --- |
| API availability | 99.9% monthly |
| P95 API latency | < 750 ms for non-summarisation endpoints |
| Worker job success | 99.0% excluding model-provider outages |
| Audit event delivery | 99.99% within 5 minutes |
| RPO | 15 minutes |
| RTO | 4 hours |
